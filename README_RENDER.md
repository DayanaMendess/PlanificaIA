# Publicar PlanificaIA en Render

Esta versión usa un Web Service Python: sirve la página y procesa chat y recomendaciones desde el servidor. El archivo `render.yaml` configura Python, `python web_app.py` y la ruta `/health`.

1. Integra estos archivos en el repositorio conectado al servicio del grupo: `render.yaml`, `web_app.py`, `agente_tareas.py`, `requirements.txt` y `dist/index.html`.
2. En Render, ejecuta **Manual Deploy → Deploy latest commit** o usa **New → Blueprint** si vas a crear otro servicio.
3. En **Environment**, comprueba que `GROQ_API_KEY` exista como variable privada del servicio. Nunca la pongas en el HTML ni en GitHub.
4. Espera el estado **Live** y abre la URL. Comprueba el chat, micrófono, lectura de voz, crear/completar tarea y calendario.

Las tareas permanecen en el almacenamiento del navegador de cada visitante. El backend no las guarda. Al hablar con el agente se envían los mensajes y las tareas pendientes a Groq; usa solo información académica no sensible. El dictado y la lectura en voz alta usan las funciones del navegador. El micrófono requiere permiso y un navegador compatible.

El RAR entregado por el grupo contiene su propio repositorio Git y un `.env`; este paquete de trabajo excluye ambos. Para actualizar exactamente el enlace ya publicado, Sneyder debe llevar los cambios a la rama conectada al servicio Render. No se crea un segundo servicio ni se publica sobre un dominio ajeno desde este paquete.

