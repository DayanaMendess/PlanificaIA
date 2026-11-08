# Despliegue de PlanificaIA en Render

**Aplicación pública:** https://planificaia.onrender.com/  
**Repositorio:** https://github.com/DayanaMendess/PlanificaIA

## Configuración del servicio

El repositorio contiene `render.yaml`, que define un **Web Service** Python llamado `planificaia`. Usa `pip install -r requirements.txt` para la construcción, `python web_app.py` para iniciarlo y `/health` como comprobación. El servidor toma el puerto asignado por Render mediante la variable `PORT`.

Para crear un despliegue desde cero, conecta el repositorio en **Render → New → Blueprint**, selecciona la rama `main` y revisa el servicio propuesto. Para actualizar el servicio existente, sube los cambios a `main` y usa **Manual Deploy → Deploy latest commit** si Render no inicia el despliegue automáticamente.

## Variable privada de Groq

En **Environment** del servicio configura:

```text
GROQ_API_KEY=<clave autorizada>
```

`render.yaml` declara la variable con `sync: false`, de modo que su valor se escribe en Render y no en GitHub. `GROQ_MODEL` tiene como valor inicial `openai/gpt-oss-120b`. Nunca agregues `.env` ni una clave real al repositorio; `.env` es solo para la ejecución local y está incluido en `.gitignore`.

## Verificación después de publicar

1. Espera a que el servicio muestre **Live**.
2. Abre https://planificaia.onrender.com/health y comprueba `{"status":"ok"}`.
3. Abre la aplicación. El indicador debe mostrar **IA Groq activa**.
4. Envía una pregunta breve en el chat para verificar una respuesta real del modelo.
5. Crea y completa una tarea, revisa el calendario y prueba **Exportar PDF**.

Las tareas web se guardan en el `localStorage` del navegador, por lo que un visitante nuevo empieza con una lista vacía. El servidor no guarda tareas compartidas. El dictado requiere permiso de micrófono y soporte del navegador. En el plan gratuito, la primera carga puede tardar tras un tiempo sin uso.

Para la descripción de arquitectura, instrucciones de uso y pruebas, consulta el [README principal](README.md). El [informe final](informe/Informe_Final_PlanificaIA_APA7.pdf) presenta las evidencias académicas.

