# PlanificaIA

Asistente para organizar tareas académicas, conversar por texto o voz y recibir recomendaciones de prioridad.

## Funciones

- Chat con Groq: crea, modifica o completa tareas a partir de mensajes; pregunta cuando falta información.
- Dictado por micrófono en Chrome y Edge, y lectura de respuestas en voz alta.
- Tablero con búsqueda, filtros, edición, historial de tareas completadas, respaldo JSON y progreso.
- Calendario mensual: las fechas vencidas aparecen en rojo; hoy y las entregas pendientes tienen indicadores propios.
- Priorización por reglas verificables, explicada por Groq cuando la API está configurada.
- Tareas del navegador guardadas en `localStorage`. No se sincronizan entre dispositivos.

## Ejecutar localmente

1. (Opcional) Copia `.env.example` como `.env` y configura `GROQ_API_KEY` si el docente autorizó su uso.
2. Haz doble clic en `Iniciar_PlanificaIA.bat`, o ejecuta `python web_app.py` desde PowerShell en esta carpeta.
3. Abre <http://127.0.0.1:8000> en el navegador. Para apagar el servidor, pulsa Ctrl+C en la ventana negra.
4. Para la versión de consola, ejecuta `python agente_tareas.py`.

**Importar** acepta un respaldo JSON de PlanificaIA (hasta 2 MB), normalmente creado con **Exportar**. Combina las tareas por ID; no importa archivos Excel, PDF ni calendarios externos.

La clave no debe aparecer en el HTML, el repositorio, capturas ni el ZIP. El navegador envía los mensajes del chat y las tareas pendientes al servidor cuando solicita a Groq una respuesta. El audio de entrada/salida lo procesa el navegador.

## Publicar en Render

Usa **New → Blueprint** sobre el repositorio que contiene `render.yaml`. En el servicio agrega `GROQ_API_KEY` en Environment; Render la guarda como variable privada del servidor. Cuando la publicación termine, la ruta `/health` debe responder con estado correcto.

## Archivos

- `agente_tareas.py`: reglas, validación, herramientas de chat, Groq y consola.
- `web_app.py`: servidor HTTP y API de chat/recomendaciones.
- `dist/index.html`: interfaz responsiva, audio, calendario y tablero.
- `render.yaml`: configuración del despliegue.

