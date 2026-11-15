# Implementation Report: TASK-1.2 — Servicio de IA y Grafo (ai_service con LangGraph)

## 1. Metadata
- **Task ID**: `TASK-1.2`
- **Backlog Reference**: `AI-01 / AI-02`
- **Implementer**: Implementer Agent
- **Date**: `2026-11-15`
- **Iteration / Attempt**: `1`
- **Specification Status**: Fully Compliant with `task_spec.md`

## 2. Summary of Implementation
Se implementó de forma completa y aislada el microservicio **`ai_service`** utilizando FastAPI y **LangGraph** (`StateGraph`) como motor de evaluación de redacciones académicas para los niveles Cambridge B2 First y C1 Advanced.

Se desarrollaron los 5 nodos principales del pipeline de evaluación:
1. **`context_prep_node`**: Anonimización estricta de PII (correos y teléfonos), cómputo de recuento de palabras y carga de directrices pedagógicas según el nivel CEFR.
2. **`writing_analysis_node`**: Detección estructurada de errores ortográficos, gramaticales, léxicos y de puntuación con cálculo exacto de offsets (`start_index`, `end_index`), citas textuales y explicaciones pedagógicas en español.
3. **`exemplar_gen_node`**: Generación de modelo ejemplar de reescritura Banda 5 elevando vocabulario y cohesión mientras preserva los argumentos centrales del alumno.
4. **`ai_detector_node`**: Análisis de patrones y expresiones formulaicas para estimar probabilidad de autoría por IA y generar la alerta *"Posible texto generado por IA"*.
5. **`validator_node`**: Validación estricta con esquemas Pydantic v2 y bucle de reintento ante respuestas mal formateadas.

Se expuso la API interna (`POST /internal/v1/evaluate` y `GET /health`), se configuró la política de Zero Data Retention (ZDR), y se integró el microservicio en `docker-compose.yml` con su respectivo `Dockerfile`.

## 3. Modified & Created Files
```
[MODIFIED]  docker-compose.yml
[CREATED]   ai_service/pyproject.toml
[CREATED]   ai_service/requirements.txt
[CREATED]   ai_service/.env.example
[CREATED]   ai_service/Dockerfile
[CREATED]   ai_service/README.md
[CREATED]   ai_service/app/__init__.py
[CREATED]   ai_service/app/main.py
[CREATED]   ai_service/app/core/__init__.py
[CREATED]   ai_service/app/core/config.py
[CREATED]   ai_service/app/core/logging.py
[CREATED]   ai_service/app/core/exceptions.py
[CREATED]   ai_service/app/schemas/__init__.py
[CREATED]   ai_service/app/schemas/request.py
[CREATED]   ai_service/app/schemas/response.py
[CREATED]   ai_service/app/schemas/health.py
[CREATED]   ai_service/app/graph/__init__.py
[CREATED]   ai_service/app/graph/state.py
[CREATED]   ai_service/app/graph/pipeline.py
[CREATED]   ai_service/app/graph/prompts/__init__.py
[CREATED]   ai_service/app/graph/prompts/templates.py
[CREATED]   ai_service/app/graph/prompts/b2_first.py
[CREATED]   ai_service/app/graph/prompts/c1_advanced.py
[CREATED]   ai_service/app/graph/nodes/__init__.py
[CREATED]   ai_service/app/graph/nodes/context_prep.py
[CREATED]   ai_service/app/graph/nodes/writing_analysis.py
[CREATED]   ai_service/app/graph/nodes/exemplar_gen.py
[CREATED]   ai_service/app/graph/nodes/ai_detector.py
[CREATED]   ai_service/app/graph/nodes/validator.py
[CREATED]   ai_service/app/api/__init__.py
[CREATED]   ai_service/app/api/v1/__init__.py
[CREATED]   ai_service/app/api/v1/router.py
[CREATED]   ai_service/app/api/v1/endpoints/__init__.py
[CREATED]   ai_service/app/api/v1/endpoints/health.py
[CREATED]   ai_service/app/api/v1/endpoints/evaluate.py
[TEST]      ai_service/tests/__init__.py
[TEST]      ai_service/tests/conftest.py
[TEST]      ai_service/tests/unit/__init__.py
[TEST]      ai_service/tests/unit/test_core.py
[TEST]      ai_service/tests/unit/test_schemas.py
[TEST]      ai_service/tests/unit/test_prompts.py
[TEST]      ai_service/tests/unit/test_nodes.py
[TEST]      ai_service/tests/integration/__init__.py
[TEST]      ai_service/tests/integration/test_evaluation_api.py
```

## 4. Key Implementation Highlights
- **LangGraph StateGraph Engine**:
  - Estado fuertemente tipado en `EvaluationState` con propagación de errores y conteo de reintentos.
  - Ensamblado secuencial con control condicional `should_continue_or_retry` hacia el nodo de reintento `writing_analysis` cuando falla la validación.
- **Privacy & Zero Data Retention (ZDR)**:
  - Sanitización de PII previa a cualquier interpolación de texto.
  - Indicador `zdr_enforced=True` en la verificación de salud.
- **AI Text Detection**:
  - Detección basada en patrones formulaicos sintéticos con cálculo de umbral (`AI_DETECTION_THRESHOLD=0.70`).
- **Resiliencia & Tipado Estricto**:
  - 100% compliant con `mypy --strict` en los 38 archivos del servicio.
  - Linter `ruff` pasando sin advertencias.
  - 27 pruebas unitarias y de integración pasando con **94%** de cobertura de código.

## 5. Pre-flight Self-Checks
- [x] Code formatted with `ruff format`.
- [x] Static type check passed with `mypy --strict` (38/38 files clean).
- [x] Linter passed with `ruff check`.
- [x] Local tests executed and passing (27/27 passed, 94% coverage).
- [x] Backend tests verified (12/12 passed, no regression).
- [x] No hardcoded secrets, test API keys, or temporary debug code.

## 6. Known Limitations or Deferred Items
- La calificación explícita de bandas (0-5) sobre los 4 criterios de Cambridge (Content, Communicative Achievement, Organisation, Language) corresponde a la siguiente tarea `TASK-1.3` (Evaluación y Rúbricas Base).
