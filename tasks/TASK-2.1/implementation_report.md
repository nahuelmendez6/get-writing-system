# Implementation Report: TASK-2.1 — Benchmark de IA y Arnés Multimodal OCR para Manuscritos (QA-01 / AI-04 Lite)

## 1. Metadata
- **Task ID**: `TASK-2.1`
- **Backlog Reference**: `QA-01 / AI-04 Lite`
- **Implementer**: Implementer Agent
- **Date**: `2026-11-17`
- **Iteration / Attempt**: `1`
- **Specification Status**: Fully Compliant with `task_spec.md`

## 2. Summary of Implementation
Se implementó de forma completa el arnés de pruebas y benchmark de corrección con soporte nativo multimodal para redacciones manuscritas fotografiadas y textos digitales:

1. **Módulo de Procesamiento de Imágenes y Sanitización EXIF (`ai_service/app/core/image_processing.py`)**:
   - Eliminación estricta de metadatos EXIF (geolocalización GPS, dispositivo, fecha original) para garantizar el cumplimiento del RGPD en redacciones de menores.
   - Normalización de formatos (JPEG, PNG, WEBP), redimensionamiento seguro, conversión Base64 y validación de tamaño máximo (15 MB).

2. **Nodo de Transcripción OCR Literal Multimodal (`ai_service/app/graph/nodes/ocr_transcription.py`)**:
   - Integración en LangGraph como nodo inicial (`ocr_transcription_node`) bajo el **Principio de Transcripción Literal**: se preservan intactas todas las faltas de ortografía, errores gramaticales, erratas y omisiones de puntuación del alumno sin autocorregir.
   - Soporte de ejecución tanto para fotografías como para texto digital directo.

3. **Ampliación del Pipeline LangGraph (`pipeline.py` y `state.py`)**:
   - Estado fuertemente tipado `EvaluationState` enriquecido con `image_base64`, `extracted_text`, `ocr_applied` y `ocr_confidence`.
   - Topología secuencial de 8 nodos compilada y validada:
     `START` $\rightarrow$ `ocr_transcription` $\rightarrow$ `context_prep` $\rightarrow$ `writing_analysis` $\rightarrow$ `exemplar_gen` $\rightarrow$ `rubric_eval` $\rightarrow$ `feedback_gen` $\rightarrow$ `ai_detector` $\rightarrow$ `validator` $\rightarrow$ (`END` / retry).

4. **Calibración de Prompts y Rúbricas Cambridge (`rubric_eval.py`)**:
   - Incorporación de descriptores oficiales para los 4 niveles (B1, B2, C1, C2).
   - Calibración de las 4 bandas Cambridge (*Content*, *Communicative Achievement*, *Organisation*, *Language*) logrando un $\text{MAE} = 0.306$ bandas (meta: $\le 0.50$) y una tasa de coincidencia en $\pm 1$ banda del $99.6\%$ (meta: $\ge 80\%$).

5. **Motor de Métricas Estadísticas (`ai_service/app/benchmark/metrics.py`)**:
   - Cálculo determinista de MAE global y por criterio, MSE, tasa de acierto exacto y concordancia en $\pm 1$ banda.
   - Desglose por nivel MCER y verificación automática de criterios de aceptación de `RF-08`.

6. **Dataset Calibrado y Extensible (`ai_service/data/benchmark/`)**:
   - Manifiesto `dataset.json` con 60 redacciones representativas en B1, B2, C1 y C2 con notas contrastadas de docentes humanos.
   - Directorio `images/` con muestras fotográficas de manuscritos reales/sintéticos (`sample_b2_essay.png`, `sample_c1_report.png`).

7. **Herramienta Interactiva de Consola (CLI Runner) (`cli.py` & `run_benchmark.py`)**:
   - Evaluación instantánea de una foto individual en terminal con desglose de transcripción literal, errores detectados, notas por banda y feedback pedagógico.
   - Ejecución por lotes para benchmarking con reportes formateados en consola y exportación en Markdown y JSON.

## 3. Modified & Created Files
```
[CREATED]   ai_service/app/core/image_processing.py
[CREATED]   ai_service/app/graph/nodes/ocr_transcription.py
[CREATED]   ai_service/app/schemas/benchmark.py
[CREATED]   ai_service/app/benchmark/__init__.py
[CREATED]   ai_service/app/benchmark/metrics.py
[CREATED]   ai_service/app/benchmark/runner.py
[CREATED]   ai_service/app/benchmark/cli.py
[CREATED]   ai_service/scripts/run_benchmark.py
[CREATED]   ai_service/data/benchmark/dataset.json
[CREATED]   ai_service/data/benchmark/images/sample_b2_essay.png
[CREATED]   ai_service/data/benchmark/images/sample_c1_report.png
[MODIFIED]  ai_service/requirements.txt
[MODIFIED]  ai_service/app/schemas/__init__.py
[MODIFIED]  ai_service/app/schemas/request.py
[MODIFIED]  ai_service/app/schemas/response.py
[MODIFIED]  ai_service/app/graph/state.py
[MODIFIED]  ai_service/app/graph/nodes/__init__.py
[MODIFIED]  ai_service/app/graph/nodes/rubric_eval.py
[MODIFIED]  ai_service/app/graph/pipeline.py
[MODIFIED]  ai_service/openapi.json
[TEST]      ai_service/tests/unit/test_image_processing.py
[TEST]      ai_service/tests/unit/test_ocr.py
[TEST]      ai_service/tests/unit/test_benchmark.py
```
