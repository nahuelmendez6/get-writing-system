Backlog y Subtareas (Reestructurado - IA First)
Proyecto: Plataforma de corrección de Writings y Membresías (Get Idiomas) Estrategia: Desarrollo inicial centrado en el despliegue del motor de IA para ejecutar el Benchmark lo antes posible. La capa comercial (membresías) se desplaza al final del ciclo.
FASE 1: Arquitectura Base y Motor de Inteligencia Artificial
El objetivo de esta fase es levantar la base del proyecto y tener la IA lista para recibir textos, sin depender de la interfaz visual del alumno.
TAREA 1.1. Core Backend (BE-01 / BE-02): Configuración de FastAPI, PostgreSQL, Alembic y Docker. Convenciones de modelos (UUID, timestamps) y conexión a base de datos.
TAREA 1.2. Servicio de IA y Grafo (AI-01 / AI-02): Creación del servicio aislado ai_service con LangGraph. Diseño de prompts (B2/C1), análisis de ortografía/gramática, generación de modelo ejemplar y alerta de "Posible texto generado por IA".
TAREA 1.3. Evaluación y Rúbricas Base (AI-03 / BE-06): Mapeo en backend de los 4 criterios de Cambridge y sus descriptores. Nodo de IA para calificar bandas (0-5) y generar feedback estructurado en JSON.
FASE 2: Benchmark, Privacidad y Ajuste del Modelo
Fase exclusiva de pruebas y validación legal antes de programar las interfaces de usuario.
TAREA 2.1. Benchmark de IA (QA-01): Ejecución masiva por consola del pipeline de IA sobre un dataset de 50-80 redacciones reales de la academia. Ajuste de prompts hasta lograr ±1 banda de coincidencia (80% de los casos) y un MAE <= 0.5.
TAREA 2.2. Privacidad y ZDR (SEC-01): Configuración estricta de Zero Data Retention (ZDR) en la API del LLM, anonimización de textos antes del envío y validación de políticas RGPD para menores.
TAREA 2.3. Control de Consumo (BE-14): Endpoint interno para medir tokens de entrada/salida y establecer límites de gasto con alertas automáticas.
FASE 3: Identidad y Estructura Académica Básica
Creación del entorno para que los usuarios puedan interactuar con la plataforma.
TAREA 3.1. Autenticación sin DNI (BE-03 / FE-01): Modelo de usuario basado en email. Flujo de registro, JWT y recuperación de contraseña. Bloqueo estricto del rol "Demo" en producción.
TAREA 3.2. Gestión de Usuarios (BE-04 / FE-01B): Endpoints CRUD y pantalla de administración de usuarios (baja lógica, filtros).
TAREA 3.3. Configuración de Actividades (BE-07 / FE-02): Creación de Assignments básicos. Incorporación de los niveles B1 a C2 y tipos de texto (incluyendo Story para B1 y Proposal para C1).
FASE 4: Piloto Digital y Procesamiento Asíncrono
Habilitación de las entregas digitales para los estudiantes y su conexión con el motor de IA.
TAREA 4.1. Almacenamiento y Entregas (BE-08 / BE-09): Configuración de S3/MinIO para archivos. Modelo de estado de entregas (DRAFT, SUBMITTED, etc.).
TAREA 4.2. Editor Digital (FE-03): VirtualWritingEditor.tsx para el estudiante, con contador de palabras, autoguardado en localStorage y modo examen.
TAREA 4.3. Workers Asíncronos (BE-10): Integración de Celery y Redis para que las entregas se procesen en la IA en segundo plano sin bloquear el servidor.
FASE 5: Canvas Docente y Portal del Alumno
Interfaces de revisión y consumo de resultados.
TAREA 5.1. Modelos de Revisión (BE-11): Separación en base de datos de AIEvaluation (inmutable) y TeacherReview (modificable).
TAREA 5.2. Canvas Interactivo (FE-04 / FE-05): Anotador bidireccional (MistakeCard.tsx). Aceptar/rechazar falsos positivos. Equivalencia interna de nota sobre 10. Toggle de visibilidad de la Banda 5. Barra para corrección en serie.
TAREA 5.3. Portal de Resultados y Reescritura (FE-03B / FE-03C): Pantalla del alumno para ver nota, feedback y modelo. Flujo de "Segunda versión" para reescribir la redacción aplicando el feedback.
FASE 6: Manuscritos OCR, Analíticas y Despliegue
Soporte físico, métricas y puesta en producción.
TAREA 6.1. OCR Multimodal Literal (AI-04 / BE-12): Transcripción estricta de manuscritos conservando errores ortográficos y de puntuación. Eliminación de metadatos EXIF.
TAREA 6.2. Vista Dividida (FE-06): Split View para comparar la fotografía con la transcripción y corregir los fallos del OCR antes de evaluar.
TAREA 6.3. Dashboards y Despliegue (BE-13 / FE-07 / OPS-01): Pantallas de métricas, evolución del alumnado, y Live Audit Log. CI/CD mediante GitHub Actions y traspaso de propiedad (Hetzner, APIs, código) a "Get Idiomas".
FASE 7: Sistema Comercial de Membresías y Licencias
Integración de la capa de negocio una vez validado todo el proceso académico y de corrección.
TAREA 7.1. Modelo de Licencias (BE-05b): Expansión del sistema de cursos para incluir StudentLicense. Definición de paquetes (ej. "Créditos de mentoría", "Acceso solo a essays C1", "Corrección humana vs IA").
TAREA 7.2. Control de Acceso Estudiantil (BE-05c): Lógica en el backend para bloquear o permitir la entrega de actividades (Assignments) en función de los créditos o membresía activa del usuario.
TAREA 7.3. Interfaz de Gestión Comercial (FE-02b): Modales para que el Administrador o Docente pueda asignar, revocar o auditar las licencias de cada estudiante desde el panel de control.



