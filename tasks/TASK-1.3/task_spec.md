# Task Specification: TASK-1.3 — Evaluación y Rúbricas Base (AI-03 / BE-06)

## 1. Metadata
- **Task ID**: `TASK-1.3`
- **Backlog Reference**: `AI-03 / BE-06`
- **Module / Target Component**: `fullstack` (`backend` y `ai_service`)
- **Related Requirements**: `RF-06`, `RF-07`, `RF-08`, `RF-14`
- **Author**: Planner Agent
- **Date**: `2026-11-16`
- **Status**: `PLANNED`

---

## 2. Objective & Summary
Implementar la infraestructura de evaluación pedagógica cuantitativa y cualitativa basada en los estándares oficiales de Cambridge Assessment English (focalizado en niveles B2 First y C1 Advanced, con soporte estructural para B1 y C2).

La tarea abarca dos componentes esenciales:
1. **Módulo Backend de Rúbricas Reutilizables (`BE-06`)**:
   - Modelos SQLAlchemy para `Rubric` y `RubricCriterion` con tipado estricto, claves primarias UUIDv4, timestamps UTC y descriptores oficiales por banda (0 a 5).
   - Migración de base de datos con Alembic (`upgrade` y `downgrade`).
   - Esquemas Pydantic v2 para validación y serialización.
   - Endpoints REST para consulta y gestión de rúbricas (`GET /api/v1/rubrics`, `GET /api/v1/rubrics/{id}`, `POST /api/v1/rubrics`, `POST /api/v1/rubrics/{id}/criteria`).
   - Plantillas predeterminadas de Cambridge (B2 First y C1 Advanced) con los 4 criterios oficiales: *Content*, *Communicative Achievement*, *Organisation* y *Language*.
   - Función matemática para cálculo de nota interna sobre 10 sin usar la marca registrada "Cambridge" en reportes.

2. **Nodos de Evaluación por Rúbrica y Feedback Pedagógico en `ai_service` (`AI-03`)**:
   - Nodo `rubric_eval`: Evaluación estricta de las 4 bandas Cambridge (0 a 5) con justificación textual extraída de la redacción del alumno y control de penalización por longitud de palabras fuera de rango ($\pm 10\%$).
   - Nodo `feedback_gen`: Generación estructurada de feedback pedagógico diferenciado: fortalezas detectadas (`strengths`), áreas prioritarias de mejora (`areas_for_improvement`) y 3 consejos prácticos accionables (`actionable_tips`).
   - Integración en el pipeline `StateGraph` de LangGraph preservando el estado tipado `EvaluationState` y actualizando el nodo de validación `validator` para verificar rangos de notas y completitud.
   - Actualización de contratos de respuesta en `ai_service` (`EvaluationResponse`) y exportación del esquema OpenAPI.

---

## 3. Technical Analysis & Pre-requisites
- **Existing Codebase Dependencies**:
  - `TASK-1.1`: Backend FastAPI con SQLAlchemy asíncrono y convención `BaseModel`.
  - `TASK-1.2`: `ai_service` con LangGraph `StateGraph`, prompts base B2/C1 y análisis de errores.
- **Pre-requisite Tasks**: `TASK-1.1`, `TASK-1.2`.
- **Reusable Assets**:
  - `backend/app/core/models.py` (`BaseModel`, `UUIDPrimaryKeyMixin`, `TimestampMixin`).
  - `backend/app/core/database.py` (`AsyncSessionLocal`, `get_db_session`).
  - `ai_service/app/graph/state.py` (`EvaluationState`).
  - `ai_service/app/graph/pipeline.py` (`StateGraph`).
  - `BUSINESS_RULES.md` (Fórmula de calificación: $\text{Nota} = (\text{Total raw} / 20) \times 10$).

---

## 4. Implementation Details

### 4.1. Backend (`BE-06`)
#### 4.1.1. Modelos de Base de Datos
- `backend/app/models/rubric.py`:
  - `Rubric`: Representa la plantilla o rúbrica de evaluación.
    - `id`: UUID (PK)
    - `name`: String(100) (ej. "Cambridge B2 First General Rubric")
    - `cefr_level`: Enum/String(10) (`B1`, `B2`, `C1`, `C2`)
    - `description`: Text (opcional)
    - `is_template`: Boolean (default True)
    - `is_active`: Boolean (default True)
    - `criteria`: relationship `RubricCriterion`, cascade all, delete-orphan, lazy="selectin"
  - `RubricCriterion`: Representa cada criterio individual.
    - `id`: UUID (PK)
    - `rubric_id`: ForeignKey("rubrics.id", ondelete="CASCADE")
    - `name`: String(100) (ej. "Content", "Communicative Achievement", "Organisation", "Language")
    - `description`: Text (opcional)
    - `weight`: Float (default 1.0)
    - `max_band`: Integer (default 5)
    - `sort_order`: Integer (default 0)
    - `descriptors`: JSON (diccionario estructurado con descriptores para Bandas 0, 1, 2, 3, 4, 5)

#### 4.1.2. Esquemas Pydantic
- `backend/app/schemas/rubric.py`:
  - `RubricCriterionBase`, `RubricCriterionCreate`, `RubricCriterionRead`
  - `RubricBase`, `RubricCreate`, `RubricRead`, `RubricListResponse`
  - Métodos y validadores auxiliares para conversión de notas institucionales sobre 10.

#### 4.1.3. Endpoints REST
- `backend/app/api/v1/endpoints/rubrics.py`:
  - `GET /api/v1/rubrics`: Listado con filtro opcional `level` y paginación básica.
  - `GET /api/v1/rubrics/{id}`: Detalle de rúbrica con sus criterios y descriptores.
  - `POST /api/v1/rubrics`: Creación de rúbrica (incluyendo criterios anidados).
  - `POST /api/v1/rubrics/{id}/criteria`: Adición de un criterio individual a una rúbrica.

#### 4.1.4. Datos Semilla (Seeds)
- `backend/app/core/seed_rubrics.py`:
  - Plantillas oficiales precargadas para B2 First y C1 Advanced con descriptores completos de Cambridge para Content, Communicative Achievement, Organisation y Language.

#### 4.1.5. Migración Alembic
- `backend/alembic/versions/001_create_rubrics_and_criteria.py`:
  - Creación de tablas `rubrics` y `rubric_criteria` con índices y claves foráneas.

---

### 4.2. AI Service (`AI-03`)
#### 4.2.1. Nodos LangGraph
- `ai_service/app/graph/nodes/rubric_eval.py`:
  - Nodo `rubric_eval_node`:
    - Evalúa el texto del estudiante en función del nivel y los 4 criterios Cambridge.
    - Asigna una banda entera o semientera (0.0 a 5.0) para cada criterio:
      - Content (0-5)
      - Communicative Achievement (0-5)
      - Organisation (0-5)
      - Language (0-5)
    - Incluye justificación (`justification`) citando evidencias concretas del texto.
    - Calcula `raw_score` (suma de bandas sobre 20).
    - Calcula `institutional_score` sobre 10: $(\text{raw\_score} / 20) \times 10.0$.
    - Evalúa si existe penalización por longitud (`length_penalty`: bool y `word_count_status`: `NORMAL` | `TOO_SHORT` | `TOO_LONG`) si `word_count` se desvía más del $\pm 10\%$ de `min_words` o `max_words`.
- `ai_service/app/graph/nodes/feedback_gen.py`:
  - Nodo `feedback_gen_node`:
    - Genera síntesis pedagógica en español:
      - `overall_feedback`: Resumen constructivo del nivel de suficiencia demostrado.
      - `strengths`: 2 a 4 fortalezas observadas en el texto.
      - `areas_for_improvement`: 2 a 4 aspectos prioritarios a corregir.
      - `actionable_tips`: Exactamente 3 recomendaciones de estudio o redacción para futuros writings.

#### 4.2.2. Esquemas Actualizados
- `ai_service/app/schemas/response.py`:
  - `CriterionEvaluation`: `name`, `score`, `max_score`, `band_descriptor`, `justification`.
  - `RubricEvaluation`: `criteria: list[CriterionEvaluation]`, `raw_score: float`, `max_raw_score: float = 20.0`, `institutional_score: float`, `length_penalty: bool`, `word_count_status: str`.
  - `PedagogicalFeedback`: `overall_feedback: str`, `strengths: list[str]`, `areas_for_improvement: list[str]`, `actionable_tips: list[str]`.
  - Actualización de `EvaluationResponse` incorporando `rubric_evaluation: RubricEvaluation` y `feedback: PedagogicalFeedback`.

#### 4.2.3. Pipeline LangGraph
- `ai_service/app/graph/state.py`:
  - Añadir campos a `EvaluationState`: `rubric_evaluation: dict[str, Any]`, `feedback: dict[str, Any]`.
- `ai_service/app/graph/pipeline.py`:
  - Secuencia de nodos:
    `START` $\rightarrow$ `context_prep` $\rightarrow$ `writing_analysis` $\rightarrow$ `exemplar_gen` $\rightarrow$ `rubric_eval` $\rightarrow$ `feedback_gen` $\rightarrow$ `ai_detector` $\rightarrow$ `validator` $\rightarrow$ condicional (retry o `END`).
- `ai_service/app/graph/nodes/validator.py`:
  - Validación de que los 4 criterios estén presentes, las notas en rango [0, 5], y los arrays de feedback pedagógico poblados correctamente.

---

## 5. Acceptance Criteria

### Scenario 1: Consulta de Rúbricas Base en Backend
- **Given**: La base de datos inicializada con las plantillas predeterminadas.
- **When**: El cliente envía una petición `GET /api/v1/rubrics?level=B2`.
- **Then**: El servicio responde HTTP 200 con la rúbrica oficial de B2 First conteniendo los 4 criterios (Content, Communicative Achievement, Organisation, Language) y descriptores para las bandas 0 a 5.

### Scenario 2: Creación de Rúbrica Personalizada con Criterios
- **Given**: Un payload válido con metadatos de rúbrica y criterios ponderados.
- **When**: Se envía un `POST /api/v1/rubrics`.
- **Then**: El servicio persiste la entidad, responde HTTP 201 y asigna identificadores UUIDv4.

### Scenario 3: Evaluación Completa por Rúbrica Cambridge en `ai_service`
- **Given**: Un texto de redacción B2 o C1 válido y un prompt de examen.
- **When**: Se invoca el endpoint `POST /internal/v1/evaluate`.
- **Then**: La respuesta HTTP 200 incluye el objeto `rubric_evaluation` con las 4 bandas evaluadas (0 a 5), `raw_score` sobre 20, `institutional_score` sobre 10 y justificaciones fundamentadas.

### Scenario 4: Generación Estructurada de Feedback Pedagógico
- **Given**: La evaluación de un writing en el pipeline LangGraph.
- **When**: Se ejecuta el nodo `feedback_gen`.
- **Then**: Se generan `overall_feedback`, `strengths`, `areas_for_improvement` y exactamente 3 `actionable_tips` orientados al estudiante.

### Scenario 5: Detección de Penalización por Conteo de Palabras
- **Given**: Un writing configurado con rango [140, 190] palabras cuyo texto contiene 100 palabras (desviación superior al 10%).
- **When**: Se ejecuta la evaluación de rúbrica.
- **Then**: `rubric_evaluation.length_penalty` es `true` y `word_count_status` es `TOO_SHORT`.

---

## 6. Security, Privacy & ZDR Considerations
- Mantener cabeceras Zero Data Retention (ZDR) en todas las consultas de inferencia hacia proveedores de LLM.
- Preservar la anonimización de PII realizada en el nodo `context_prep` antes de evaluar los criterios de rúbrica.
- Aislamiento estricto: El cálculo de nota interna sobre 10 no debe exponer marcas registradas de Cambridge hacia el alumno.
- Migraciones seguras: Inclusión de script reversible (`upgrade` y `downgrade`) con SQLAlchemy y Alembic.
