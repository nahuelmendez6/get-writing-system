# Backlog Execution Status — Get Idiomas AI Writing System

**Strategy**: AI-First (Engine & Benchmark prior to UI/Commercial tiers)  
**Last Updated**: 2026-11-17  
**Overall Completion**: 14% (3 / 21 tasks)

---

## FASE 1: Arquitectura Base y Motor de Inteligencia Artificial
*Objetivo: Levantar la base del proyecto y tener la IA lista para recibir textos.*

| ID | Tarea | Componentes | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-1.1` | Core Backend | `BE-01 / BE-02` | `COMPLETED` | Committer |
| `TASK-1.2` | Servicio de IA y Grafo | `AI-01 / AI-02` | `COMPLETED` | Committer |
| `TASK-1.3` | Evaluación y Rúbricas Base | `AI-03 / BE-06` | `COMPLETED` | Committer |

---

## FASE 2: Benchmark, Privacidad y Ajuste del Modelo
*Objetivo: Validación empírica de precisión de IA y políticas legales antes de UI.*

| ID | Tarea | Componentes | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-2.1` | Benchmark de IA (MAE $\le 0.5$, 80% acierto) | `QA-01` | `PENDING` | - |
| `TASK-2.2` | Privacidad y Zero Data Retention (ZDR) | `SEC-01` | `PENDING` | - |
| `TASK-2.3` | Control de Consumo y Alertas de Tokens | `BE-14` | `PENDING` | - |

---

## FASE 3: Identidad y Estructura Académica Básica
*Objetivo: Entorno institucional y gestión docente/estudiante.*

| ID | Tarea | Componentes | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-3.1` | Autenticación Segura sin DNI | `BE-03 / FE-01` | `PENDING` | - |
| `TASK-3.2` | Gestión de Usuarios y Roles | `BE-04 / FE-01B`| `PENDING` | - |
| `TASK-3.3` | Configuración de Actividades (B1-C2) | `BE-07 / FE-02` | `PENDING` | - |

---

## FASE 4: Piloto Digital y Procesamiento Asíncrono
*Objetivo: Entregas digitales y workers en background.*

| ID | Tarea | Componentes | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-4.1` | Almacenamiento S3 y Entregas Digitales | `BE-08 / BE-09` | `PENDING` | - |
| `TASK-4.2` | Editor Digital VirtualWritingEditor | `FE-03` | `PENDING` | - |
| `TASK-4.3` | Workers Asíncronos Celery & Redis | `BE-10` | `PENDING` | - |

---

## FASE 5: Canvas Docente y Portal del Alumno
*Objetivo: Interfaces de corrección interactiva y consumo de resultados.*

| ID | Tarea | Componentes | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-5.1` | Modelos AIEvaluation & TeacherReview | `BE-11` | `PENDING` | - |
| `TASK-5.2` | Canvas Interactivo y MistakeCard | `FE-04 / FE-05` | `PENDING` | - |
| `TASK-5.3` | Portal de Resultados y Flujo Segunda Versión | `FE-03B / FE-03C`| `PENDING` | - |

---

## FASE 6: Manuscritos OCR, Analíticas y Despliegue
*Objetivo: Soporte físico literal, split view, dashboards y producción.*

| ID | Tarea | Componentes | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-6.1` | OCR Multimodal Literal | `AI-04 / BE-12` | `PENDING` | - |
| `TASK-6.2` | Vista Dividida (Split View) | `FE-06` | `PENDING` | - |
| `TASK-6.3` | Dashboards y CI/CD en Hetzner | `BE-13 / FE-07 / OPS-01` | `PENDING` | - |

---

## FASE 7: Sistema Comercial de Membresías y Licencias
*Objetivo: Integración de la capa comercial tras validación pedagógica.*

| ID | Tarea | Componentes | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-7.1` | Modelo de Licencias StudentLicense | `BE-05b` | `PENDING` | - |
| `TASK-7.2` | Control de Acceso y Cuotas Estudiantiles | `BE-05c` | `PENDING` | - |
| `TASK-7.3` | Interfaz de Gestión Comercial Admin | `FE-02b` | `PENDING` | - |
