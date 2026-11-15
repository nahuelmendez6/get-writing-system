# Task Specification: TASK-1.2 — Servicio de IA y Grafo (ai_service con LangGraph)

## 1. Metadata
- **Task ID**: `TASK-1.2`
- **Backlog Reference**: `AI-01 / AI-02`
- **Module / Target Component**: `/ai_service`
- **Related Requirements**: `RF-06`, `RF-08`, `RF-09`, `RNF-REND-01`, `RNF-SEG-01`
- **Author**: Planner Agent
- **Date**: `2026-11-15`
- **Status**: `COMPLETED`

---

## 2. Objective & Summary
Establecer el microservicio aislado de inteligencia artificial **`ai_service`** utilizando FastAPI y **LangGraph** como motor de procesamiento por grafos de estado tipados (`StateGraph`).

Esta tarea sienta las bases del pipeline de IA para evaluar textos académicos conforme a los estándares de Cambridge English (focalizado en niveles **B2 First** y **C1 Advanced**), implementando:
1. **Grafo de Estado Tipado (`StateGraph`)**: Pipeline con nodos asíncronos y transiciones explícitas.
2. **Preparación de Contexto y Gestión de Prompts**: Prompts versionados y parametrizados por nivel CEFR (B2/C1) y tipo de texto (Essay, Article, Report, Review, Email, Proposal).
3. **Análisis de Escritura (Ortografía, Gramática y Léxico)**: Detección estructurada de errores con índices de caracteres (`start_index`, `end_index`), texto citado, corrección sugerida, categoría canónica y explicación pedagógica.
4. **Generación de Modelo Ejemplar (Banda 5)**: Reescritura mejorada del texto que modela el nivel superior de suficiencia comunicativa y léxica.
5. **Detector de Texto Generado por IA**: Algoritmo / nodo de inferencia para calcular probabilidad de autoría sintética y emitir la alerta *"Posible texto generado por IA"*.
6. **Validación de Salida y Bucle de Reintento**: Validación estricta con esquemas Pydantic v2 y nodo de reparación ante respuestas mal formateadas.
7. **Políticas de Privacidad y ZDR**: Aislamiento estricto del servicio con configuración de cabeceras Zero Data Retention (ZDR) y sanitización previa de PII.

---

## 3. Technical Analysis & Pre-requisites
- **Existing Codebase Dependencies**:
  - `TASK-1.1` completado: Core backend operativo con convenciones y Docker Compose base.
  - `docker-compose.yml`: Se integrará el servicio `ai_service` conectado a la red `get_network`.
- **Pre-requisite Tasks**: `TASK-1.1` (Core Backend).
- **Reusable Assets**:
  - Definiciones arquitectónicas en `.agent-system/knowledge/ARCHITECTURE.md`.
  - Estándares de codificación en `.agent-system/knowledge/CODING_STANDARDS.md`.
  - Reglas de privacidad y ZDR en `.agent-system/knowledge/SECURITY_RULES.md`.

---

## 4. Implementation Details

### 4.1. Project Layout & Dependencies
El microservicio `ai_service/` se estructurará de forma modular e independiente:
```
ai_service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Servidor FastAPI interno, lifespan y middlewares
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings con pydantic-settings (LLM API keys, modelos, ZDR)
│   │   ├── logging.py           # Logging estructurado JSON
│   │   └── exceptions.py        # Excepciones custom y manejadores de error
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py             # TypedDict EvaluationState
│   │   ├── pipeline.py          # StateGraph compilado y orquestador del flujo
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── context_prep.py  # Nodo 1: Preparación de contexto y sanitización PII
│   │   │   ├── writing_analysis.py # Nodo 2: Detección de errores ortográficos, gramaticales y léxicos
│   │   │   ├── exemplar_gen.py  # Nodo 3: Generación de texto ejemplar Banda 5
│   │   │   ├── ai_detector.py   # Nodo 4: Detección y probabilidad de texto generado por IA
│   │   │   └── validator.py     # Nodo 5: Validación de contrato Pydantic y bucle de reintento
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── templates.py     # Plantillas maestras de prompts
│   │       ├── b2_first.py      # Criterios específicos B2 (rubric context)
│   │       └── c1_advanced.py   # Criterios específicos C1 (rubric context)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py           # EvaluationRequest schema
│   │   ├── response.py          # EvaluationResponse, MistakeAnnotation, AIDetectionResult
│   │   └── health.py            # HealthCheckResponse
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── router.py        # Router interno
│           └── endpoints/
│               ├── __init__.py
│               ├── health.py    # GET /health
│               └── evaluate.py  # POST /internal/v1/evaluate
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures pytest asíncronos y mocks de LLM
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_prompts.py      # Pruebas de formateo e inyección de prompts
│   │   ├── test_nodes.py        # Pruebas unitarias de nodos individuales
│   │   └── test_schemas.py      # Pruebas de validación de modelos Pydantic
│   └── integration/
│       ├── __init__.py
│       └── test_evaluation_api.py # Prueba del endpoint /internal/v1/evaluate con mock LLM
├── Dockerfile                   # Imagen ligera Python 3.12-slim
├── pyproject.toml               # Dependencias (fastapi, langgraph, langchain-core, pydantic)
├── requirements.txt             # Dependencias congeladas
└── .env.example                 # Variables de entorno
```

### 4.2. State Schema & LangGraph Graph Architecture

#### Estado Tipado (`EvaluationState`):
```python
from typing import Literal, TypedDict
from pydantic import BaseModel, Field

class Mistake(BaseModel):
    id: str = Field(..., description="Identificador único del error")
    start_index: int = Field(..., description="Índice de carácter inicial en el texto original")
    end_index: int = Field(..., description="Índice de carácter final en el texto original")
    quote: str = Field(..., description="Fragmento textual original con el error")
    correction: str = Field(..., description="Corrección sugerida")
    category: Literal["grammar", "spelling", "punctuation", "vocabulary", "style"] = Field(
        ..., description="Categoría pedagógica del error"
    )
    explanation: str = Field(..., description="Explicación clara del error en español")

class AIDetection(BaseModel):
    probability: float = Field(..., ge=0.0, le=1.0, description="Probabilidad estimada de autoría por IA")
    is_likely_ai: bool = Field(..., description="Bandera booleana de alerta si supera el umbral")
    confidence: Literal["LOW", "MEDIUM", "HIGH"] = Field(..., description="Nivel de confianza de la detección")
    rationale: str = Field(..., description="Justificación técnica de la detección de patrones sintéticos")

class EvaluationState(TypedDict, total=False):
    submission_id: str
    student_text: str
    sanitized_text: str
    task_prompt: str
    level: str  # B2, C1
    text_type: str  # essay, article, report, review, email, proposal
    min_words: int | None
    max_words: int | None
    word_count: int
    mistakes: list[dict]
    exemplar_model: str
    ai_detection: dict
    validation_passed: bool
    retry_count: int
    errors: list[str]
```

#### Transiciones del Grafo:
```
[START]
   │
   ▼
[context_prep_node]  (Sanitiza PII, calcula word_count, prepara contexto B2/C1)
   │
   ▼
[writing_analysis_node]  (Extrae errores ortográficos, gramaticales, léxicos y offsets)
   │
   ▼
[exemplar_gen_node]  (Genera versión mejorada Banda 5)
   │
   ▼
[ai_detector_node]  (Evalúa patrones de texto sintético y asigna probabilidad/alerta)
   │
   ▼
[validator_node]  (Valida contrato Pydantic completo)
   │
   ├── (Si falla y retry_count < 2) ──► [writing_analysis_node]
   │
   └── (Si es válido o retry_count >= 2) ──► [END]
```

### 4.3. API & Data Contracts

#### Endpoint: `POST /internal/v1/evaluate`
- **Autenticación**: Header opcional/interno `X-Internal-Token` configurado en variables de entorno.
- **Request Payload**:
```json
{
  "submission_id": "8a7c6b5a-4d3e-4f2a-b1c0-9d8e7f6a5b4c",
  "student_text": "In recent years, the technology has changed our life significantly...",
  "task_prompt": "Write an essay discussing the advantages and disadvantages of online education.",
  "level": "B2",
  "text_type": "essay",
  "min_words": 140,
  "max_words": 190
}
```
- **Response Payload (`200 OK`)**:
```json
{
  "submission_id": "8a7c6b5a-4d3e-4f2a-b1c0-9d8e7f6a5b4c",
  "word_count": 165,
  "mistakes": [
    {
      "id": "err-1",
      "start_index": 17,
      "end_index": 31,
      "quote": "the technology",
      "correction": "technology",
      "category": "grammar",
      "explanation": "El sustantivo 'technology' en sentido general no requiere artículo determinado 'the'."
    }
  ],
  "exemplar_model": "In recent years, technology has transformed our daily lives remarkably...",
  "ai_detection": {
    "probability": 0.15,
    "is_likely_ai": false,
    "confidence": "HIGH",
    "rationale": "El texto presenta variabilidad natural de longitud de oraciones y errores típicos de interlengua."
  },
  "status": "SUCCESS",
  "execution_time_seconds": 2.45
}
```

### 4.4. Business Logic & Prompts

1. **Prompts Versionados**:
   - `writing_eval_v1`: Prompt base con directrices para corrección de ortografía, puntuación, gramática y vocabulario, con salida obligatoria en formato JSON estructurado.
   - Parámetros por nivel:
     - **B2 First**: Enfoque en precisión gramatical básica-intermedia (tiempos verbales, colocaciones, conectores lógicos comunes).
     - **C1 Advanced**: Enfoque en flexibilidad léxica, sutileza estilística, modismos y estructuras complejas (inversión, condicionales mixtos).
2. **Generación de Modelo Ejemplar**:
   - Reescribe la redacción manteniendo el argumento e ideas originales del estudiante, elevando el vocabulario y variedad sintáctica a nivel Banda 5.
3. **Detección de IA**:
   - Analiza la perplejidad sintética estimada, rigidez de estructuras y ausencia de errores comunes de interlengua.
   - Si la probabilidad supera `AI_DETECTION_THRESHOLD` (por defecto `0.70`), activa la alerta `is_likely_ai = true`.
4. **Resiliencia & Timeout**:
   - Timeout máximo de 45 segundos por nodo LLM.
   - Soporte para cliente LLM configurable (soporte de proveedores externos como OpenAI, Anthropic, Gemini o Mock LLM para testing).

### 4.5. Infrastructure & Containerization
- **Dockerfile (`ai_service/Dockerfile`)**:
  - Base: `python:3.12-slim`.
  - Puerto expuesto: `8001`.
  - Entrypoint: `uvicorn app.main:app --host 0.0.0.0 --port 8001`.
- **Actualización de `docker-compose.yml`**:
  - Incorporar el servicio `ai_service` dependiente de la red `get_network`.

---

## 5. Security, Privacy & Compliance (ZDR & RGPD)
1. **Zero Data Retention (ZDR)**:
   - Configuración explícita de cabeceras en clientes de LLM para evitar que las redacciones de estudiantes sean utilizadas para entrenamiento de modelos.
2. **Sanitización de PII**:
   - Antes de enviar el texto al modelo de lenguaje, el nodo `context_prep_node` inspecciona y reemplaza nombres propios, correos electrónicos o números identificadores para proteger la privacidad de los alumnos.
3. **Aislamiento de Red**:
   - `ai_service` no expone puertos públicos al frontend; únicamente es accesible desde la red interna de contenedores (`get_network`) para llamadas originadas por el backend y workers de Celery.

---

## 6. Acceptance Criteria & Test Scenarios

### Scenario 1: Evaluación exitosa de texto digital B2/C1 (Happy Path)
- **Given**: Un payload válido con `student_text`, `task_prompt`, `level: "B2"` y `text_type: "essay"`.
- **When**: Se envía una petición `POST /internal/v1/evaluate`.
- **Then**: El servicio responde con HTTP 200 OK, lista de `mistakes` con offsets válidos, texto `exemplar_model` de Banda 5, métricas de `ai_detection` y `word_count` calculado.

### Scenario 2: Alerta de texto generado por IA
- **Given**: Un texto con patrones altamente sintéticos o generado artificialmente.
- **When**: Se procesa a través del nodo `ai_detector_node`.
- **Then**: El objeto `ai_detection` asigna una probabilidad superior a 0.70 y marca `is_likely_ai: true` con justificación en `rationale`.

### Scenario 3: Bucle de reparación ante respuesta mal formateada del LLM
- **Given**: Un nodo de LLM que devuelve JSON sintácticamente inválido o incompleto en el primer intento.
- **When**: El nodo `validator_node` detecta el fallo de validación Pydantic.
- **Then**: El grafo reintenta la transición incrementando `retry_count` hasta alcanzar validación exitosa o límite de 2 reintentos sin colapsar el proceso.

### Scenario 4: Validación de entrada y rechazo de parámetros inválidos
- **Given**: Una petición con nivel desconocido (ej. `"Z1"`) o texto vacío.
- **When**: Se envía la petición a `POST /internal/v1/evaluate`.
- **Then**: El servicio rechaza la petición con código HTTP 422 Unprocessable Entity y formato de error canónico.

### Scenario 5: Verificación de salud y cabeceras ZDR
- **Given**: El microservicio `ai_service` ejecutándose.
- **When**: Se consulta `GET /health`.
- **Then**: Responde HTTP 200 con estado `"healthy"`, versión, entorno y confirmación de política ZDR activa.

---

## 7. Definition of Done Checklist
- [ ] Estructura modular de `ai_service` creada conforme a estándares de arquitectura.
- [ ] Pipeline LangGraph (`StateGraph`) implementado con nodos tipados y bucle de reintento.
- [ ] Prompts versionados para B2 First y C1 Advanced organizados en `graph/prompts/`.
- [ ] Detección de errores ortográficos, gramaticales y léxicos con offsets.
- [ ] Generador de modelo ejemplar Banda 5 y detector de texto IA implementados.
- [ ] Endpoint interno `POST /internal/v1/evaluate` y `GET /health` funcionales.
- [ ] `Dockerfile` y actualización de `docker-compose.yml` completados.
- [ ] Pruebas unitarias y de integración pasando con $\ge 80\%$ de cobertura.
- [ ] `ruff check` y `mypy --strict` pasando sin errores.
