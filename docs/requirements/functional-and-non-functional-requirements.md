Documento 2: Especificación de Requerimientos (Restructurada)

1. Contexto y Roles
Plataforma "Get Idiomas" para gestión de entregas de redacción, evaluación IA, corrección docente y venta de licencias/membresías.
Roles: Administrador, Docente, Estudiante. (Autenticación mediante email/contraseña; se prohíbe el uso del DNI como credencial de acceso).

2. Requerimientos Funcionales (RF)

    Módulo 1: Identidad y Seguridad (Adelantado)

        RF-01: Autenticación segura por Email y recuperación de contraseña por correo.

        RF-02: Bloqueo estricto de roles de desarrollo (DevRoleSwitcher) y demos en producción.

        RF-03: Cumplimiento RGPD desde el diseño (consentimiento de menores, ZDR en IA).

    Módulo 2: Usuarios y Membresías

        RF-04: Gestión completa de usuarios (con frontend visual).

        RF-05: Sistema de Licencias/Membresías: control de acceso a tipos de writing, mentorías o correcciones humanas vs. automatizadas.

    Módulo 3: Cursos y Tareas (Writings)

        RF-06: Soporte estructural para niveles B1 Preliminary, B2 First, C1 Advanced y C2 Proficiency (activando B2 y C1 para el piloto).

        RF-07: Inclusión de todos los tipos de tarea (Essay, Email, Article, Review, Report, Story, Proposal).

    Módulo 4: Motor IA y Benchmark

        RF-08: Validación de precisión de IA (Benchmark) con desviación máxima MAE de 0.5 bandas y 80% de acierto exacto.

        RF-09: Detección de redacciones generadas por IA y alertas de plagio.

        RF-10: Panel de control de consumo de tokens y alertas de límite de gasto.

    Módulo 5: Portal del Alumno y Entregas

        RF-11: Editor digital y subida de manuscritos.

        RF-12: Pantalla de resultados del alumno (nota, feedback y observaciones).

        RF-13: Flujo de "Segunda Versión": reescritura tras el feedback y comparación de versiones.

    Módulo 6: Canvas Docente

        RF-14: Evaluación sobre 10 (fórmula de equivalencia interna, sin usar marca "Cambridge").

        RF-15: Configuración de visibilidad del modelo Banda 5 (siempre visible vs. visible tras reescritura).

        RF-16: Corrección de manuscritos en Split View y transcripción OCR estrictamente literal.

    Módulo 7: Analíticas

        RF-17: Frontends de Dashboards para Admin, Docente y Estudiante.
