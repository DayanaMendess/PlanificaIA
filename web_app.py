"""Servidor web de PlanificaIA (solo biblioteca estándar).

Sirve la página (dist/index.html) y la API que consulta a Groq con la clave guardada en el
servidor (variable de entorno GROQ_API_KEY). La clave nunca se envía al navegador.
Las tareas viven en el navegador de cada visitante; el servidor no las almacena.
"""
from __future__ import annotations

import json
import os
import threading
import time
from collections import defaultdict, deque
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import agente_tareas as agente

BASE_DIR = Path(__file__).resolve().parent
INDEX = BASE_DIR / "dist" / "index.html"
MAX_BODY = 20_000
MAX_BODY_CHAT = 40_000
LIMITE_SOLICITUDES, VENTANA_SEGUNDOS = 12, 60


class LimitadorPorIP:
    """Limita solicitudes de IA por IP para proteger la cuota de la clave compartida."""

    def __init__(self, limite, ventana):
        self.limite, self.ventana, self.registro, self.lock = limite, ventana, defaultdict(deque), threading.Lock()

    def permitir(self, ip):
        ahora = time.monotonic()
        with self.lock:
            cola = self.registro[ip]
            while cola and ahora - cola[0] > self.ventana:
                cola.popleft()
            if len(cola) >= self.limite:
                return False
            cola.append(ahora)
            if len(self.registro) > 5000:   # evita crecimiento sin límite
                for k in [k for k, v in self.registro.items() if not v]:
                    del self.registro[k]
            return True


limitador = LimitadorPorIP(LIMITE_SOLICITUDES, VENTANA_SEGUNDOS)
CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
       "connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")


def fecha_cliente(valor):
    """Usa la fecha del navegador si es válida y cercana a la del servidor (zonas horarias)."""
    hoy = date.today()
    try:
        d = date.fromisoformat(str(valor))
    except ValueError:
        return hoy
    return d if abs((d - hoy).days) <= 2 else hoy


class Handler(BaseHTTPRequestHandler):
    server_version = "PlanificaIA"
    sys_version = ""

    def _enviar(self, status, cuerpo: bytes, tipo, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(cuerpo)

    def _json(self, status, obj, extra=None):
        self._enviar(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", extra)

    def _ip(self):
        reenviada = self.headers.get("X-Forwarded-For", "")
        return reenviada.split(",")[0].strip() or self.client_address[0]

    def _ruta(self):
        return self.path.split("?", 1)[0]

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        ruta = self._ruta()
        if ruta in {"/", "/index.html"}:
            try:
                self._enviar(200, INDEX.read_bytes(), "text/html; charset=utf-8")
            except OSError:
                self._json(500, {"error": "No se encontró dist/index.html"})
        elif ruta == "/health":
            self._json(200, {"status": "ok"})
        elif ruta == "/api/estado":
            # Permite detectar un .env añadido después de iniciar el proceso local.
            agente.cargar_configuracion_local()
            self._json(200, {"ia_configurada": agente.groq_configurado(), "modelos": agente.modelos_a_probar()[:1]})
        else:
            self._json(404, {"error": "No encontrado"})

    def _leer_json(self, maximo):
        """Devuelve el cuerpo JSON (dict) o None si ya respondió con un error."""
        try:
            size = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._json(411, {"error": "Falta Content-Length."})
            return None
        if size < 0 or size > maximo:
            self._json(413, {"error": "Solicitud demasiado grande."})
            return None
        try:
            datos = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(datos, dict):
                raise ValueError("El cuerpo debe ser un objeto JSON.")
            return datos
        except (ValueError, UnicodeDecodeError) as exc:      # JSONDecodeError es ValueError
            self._json(400, {"error": f"Datos no válidos: {exc}"})
            return None

    def do_POST(self):
        ruta = self._ruta()
        if ruta not in {"/api/recomendar", "/api/chat"}:
            return self._json(404, {"error": "No encontrado"})
        agente.cargar_configuracion_local()
        datos = self._leer_json(MAX_BODY_CHAT if ruta == "/api/chat" else MAX_BODY)
        if datos is None:
            return
        try:
            if ruta == "/api/chat":
                tareas = agente.sanitizar_estado_chat(datos.get("tareas", []))
                mensajes = agente.sanitizar_mensajes(datos.get("mensajes"))
            else:
                tareas = agente.sanitizar_tareas(datos.get("tareas", []))
        except ValueError as exc:
            return self._json(400, {"error": f"Datos no válidos: {exc}"})
        if not limitador.permitir(self._ip()):
            return self._json(429, {"error": "Demasiadas consultas seguidas. Espera un minuto e intenta de nuevo."},
                              {"Retry-After": str(VENTANA_SEGUNDOS)})
        hoy = fecha_cliente(datos.get("hoy"))
        try:
            if ruta == "/api/chat":
                try:
                    return self._json(200, agente.chat(mensajes, tareas, hoy))
                except agente.GroqError as exc:
                    return self._json(502, {"error": f"No se pudo consultar a la IA: {exc}"})
            self._json(200, agente.recomendar(tareas, hoy))
        except Exception:                                    # nunca dejar la conexión colgada
            self._json(500, {"error": "Error interno al generar la respuesta."})

    def log_message(self, fmt, *args):
        print("[web] " + (fmt % args), flush=True)


def main():
    puerto = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST") or ("0.0.0.0" if os.getenv("PORT") else "127.0.0.1")
    servidor = ThreadingHTTPServer((host, puerto), Handler)
    servidor.daemon_threads = True
    ia = "Groq activo" if agente.groq_configurado() else "SIN clave de Groq (solo reglas locales)"
    print(f"PlanificaIA escuchando en http://{host}:{puerto} | IA: {ia}", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        servidor.server_close()


if __name__ == "__main__":
    main()

