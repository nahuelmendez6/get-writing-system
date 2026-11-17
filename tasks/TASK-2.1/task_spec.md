# Task Specification: TASK-2.1 — Benchmark de IA y Arnés Multimodal OCR para Manuscritos (QA-01 / AI-04 Lite)

## 1. Metadata
- **Task ID**: `TASK-2.1`
- **Backlog Reference**: `QA-01 / AI-04 Lite`
- **Module / Target Component**: `ai_service`
- **Related Requirements**: `RF-06`, `RF-07`, `RF-08`, `RF-16`
- **Author**: Planner Agent
- **Date**: `2026-11-17`
- **Status**: `PLANNED`

---

## 2. Objective & Summary
Implementar el arnés de pruebas y benchmark de corrección con soporte nativo multimodal para redacciones manuscritas fotografiadas (manuscritos en papel/cuaderno) y textos digitales. La tarea dota a `ai_service` de la capacidad de recibir imágenes (`.jpg`, `.png`, etc.), sanitizar metadatos EXIF por privacidad (RGPD), transcribir literalmente el texto manuscrito mediante inferencia de visión multimodal sin autocorregir los errores del alumno (*Literal OCR Principle*), e inyectar el texto en el pipeline de evaluación LangGraph para obtener el análisis de errores, modelo ejemplar (Banda 5), bandas Cambridge (0 a 5) y feedback pedagógico.

Asimismo, se construye una herramienta de consola interactiva (CLI Runner) que permite al equipo docente probar redacciones individuales fotografiadas al instante o ejecutar lotes masivos de benchmark calculando métricas estadísticas de concordancia ($\text{MAE} \le 0.5$ bandas y acierto en $\pm 1$ banda $\ge 80\%$) y exportando reportes en Markdown y JSON.

---

## 3. Technical Analysis & Pre-requisites
- **Existing Codebase Dependencies**:
  - `TASK-1.2`: Grafo `StateGraph` de LangGraph, prompts base B2/C1 y análisis de errores lingüísticos.
  - `TASK-1.3`: Nodos de evaluación `rubric_eval` (4 criterios Cambridge) y `feedback_gen` con calificación institucional sobre 10.
- **Pre-requisite Tasks**: `TASK-1.1`, `TASK-1.2`, `TASK-1.3` (`COMPLETED`).
- **Reusable Assets**:
  - `ai_service/app/graph/pipeline.py` y `ai_service/app/graph/state.py`.
  - `ai_service/app/graph/nodes/rubric_eval.py` (`CAMBRIDGE_DESCRIPTORS`).
  - [BUSINESS_RULES.md](file:///home/nahuel/projects/get/project-root/.agent-system/knowledge/BUSINESS_RULES.md#L58-L66) (*Literal OCR Policy*).

---

## 4. Implementation Details

### 4.1. Módulo de Procesamiento de Imagen y Eliminación EXIF (`ai_service/app/core/image_processing.py`)
- Función `sanitize_image(image_bytes: bytes) -> tuple[bytes, dict[str, Any]]`:
  - Decodifica la imagen y elimina completamente los metadatos EXIF (coordenadas GPS de la foto, modelo de dispositivo, marca de tiempo original) para garantizar privacidad RGPD.
  - Valida formatos soportados (`JPEG`, `PNG`, `WEBP`) y límites de tamaño (hasta 15 MB).
  - Extrae metadatos seguros de visualización: dimensiones (`width`, `height`), formato normalizado y tamaño sanitizado.
  - Convierte a codificación Base64 estandarizada para inferencia multimodal.

### 4.2. Nodo de Transcripción OCR Literal Multimodal (`ai_service/app/graph/nodes/ocr_transcription.py`)
- Nodo LangGraph `ocr_transcription_node(state: EvaluationState) -> dict[str, Any]`:
  - Si el estado contiene `image_bytes` o `image_base64`:
    - Sanitiza la imagen eliminando EXIF.
    - Ejecuta el prompt estricto de **Transcripción Literal**:
      > *"You are an expert Cambridge handwriting transcriber. Transcribe the handwritten student essay strictly verbatim. You MUST PRESERVE all spelling mistakes, punctuation errors, grammatical slips, capitalization choices, and paragraph breaks exactly as written by the student. DO NOT correct, fix, or polish any mistake under any circumstance."*
    - En modo simulado/mock o pruebas: utiliza heurística de transcripción literal con fallos sintéticos representativos para permitir ejecución sin dependencia obligatoria de credenciales externas.
    - Asigna el texto resultante a `student_text` y `extracted_text`, registrando `ocr_applied: True` y la confianza de transcripción.
  - Si no contiene imagen (entrada digital directa): propaga el texto sin modificar y establece `ocr_applied: False`.

### 4.3. Integración en el Pipeline LangGraph (`ai_service/app/graph/state.py` y `pipeline.py`)
- Actualizar `EvaluationState`:
  - `image_base64: str | None`
  - `image_format: str | None`
  - `extracted_text: str | None`
  - `ocr_confidence: float | None`
  - `ocr_applied: bool`
- Topología del Grafo ampliada:
  `START` $\rightarrow$ `ocr_transcription` $\rightarrow$ `context_prep` $\rightarrow$ `writing_analysis` $\rightarrow$ `exemplar_gen` $\rightarrow$ `rubric_eval` $\rightarrow$ `feedback_gen` $\rightarrow$ `ai_detector` $\rightarrow$ `validator` $\rightarrow$ (`END` / retry).

### 4.4. Esquemas Pydantic para el Arnés de Benchmark y Multimodal (`ai_service/app/schemas/benchmark.py`)
- `BenchmarkCriterionScores`: `content`, `communicative_achievement`, `organisation`, `language`, `raw_score`, `institutional_score`.
- `BenchmarkSample`: Soporta tanto `student_text` como `image_path` / `image_base64`, con consigna (`prompt`), nivel (`cefr_level`), tipología (`task_type`) y notas humanas de referencia.
- `BenchmarkEvaluationResult`: Registro comparativo con errores absolutos, coincidencia en $\pm 1$ banda y texto transcrito.
- `BenchmarkReportSummary`: MAE global, % dentro de $\pm 1$ banda, métricas por criterio y nivel.

### 4.5. Estructura de Datos Extensible (`ai_service/data/benchmark/`)
- Carpeta `images/`: Almacena fotografías de prueba de redacciones manuscritas.
- Manifiesto `dataset.json`: Lote inicial extensible de redacciones calibradas (B1 a C2) preparadas para recibir nuevas fotos reales de la academia.

### 4.6. Motor de Métricas y Runner CLI (`ai_service/app/benchmark/`)
- `metrics.py`: Cálculo matemático de $\text{MAE}$, coincidencia en $\pm 1$ banda, exact match y desglose por nivel.
- `runner.py`: Orquestador asíncrono para ejecutar el pipeline sobre el dataset de fotos/textos.
- `cli.py` & `ai_service/scripts/run_benchmark.py`:
  - Comando individual para probar una foto en segundos:
    ```bash
    python -m ai_service.app.benchmark.cli --image ruta/foto.jpg --level B2 --type essay
    ```
  - Comando masivo para ejecutar el benchmark completo:
    ```bash
    python -m ai_service.app.benchmark.cli --dataset ai_service/data/benchmark/dataset.json --output-md report.md --output-json report.json
    ```

---

## 5. Security, Privacy & Compliance (ZDR & EXIF)
- **Eliminación EXIF Mandatoria**: Ningún archivo fotográfico transmitido a proveedores LLM conservará geolocalización o metadatos de cámara.
- **Zero Data Retention (ZDR)**: Las llamadas multimodales enlazan cabeceras `store: false` para impedir que las fotos de exámenes se usen para entrenar modelos.
- **Aislamiento de PII**: Datos del alumno detectados en la imagen (nombres, correos) se anonimizan tras la transcripción literal antes de la evaluación.

---

## 6. Acceptance Criteria & Test Scenarios

### Scenario 1: Sanitización de Imagen y Eliminación de EXIF
- **Given**: Una imagen JPEG que contiene metadatos EXIF (coordenadas GPS de prueba).
- **When**: Se procesa a través de `sanitize_image`.
- **Then**: La imagen resultante mantiene su calidad visual pero carece totalmente de etiquetas EXIF privadas, y se extraen dimensiones válidas.

### Scenario 2: Transcripción OCR Literal sin Autocorrección
- **Given**: Una fotografía de redacción manuscrita con errores ortográficos evidentes (ej. "everyday" como adverbio, "don't must", "informations").
- **When**: Se ejecuta el nodo `ocr_transcription_node`.
- **Then**: El texto transcrito preserva fielmente los errores exactos del alumno sin corregirlos automáticamente, y activa `ocr_applied: true`.

### Scenario 3: Corrección End-to-End a Partir de una Fotografía
- **Given**: Una fotografía de manuscrito procesada por el pipeline de evaluación.
- **When**: Se invoca el pipeline completo `evaluate_writing`.
- **Then**: El sistema transcribe la foto, detecta los errores ortográficos y gramaticales sobre la transcripción literal, asigna bandas Cambridge (0 a 5) y genera feedback pedagógico estructurado en español.

### Scenario 4: Ejecución por Consola de una Redacción en Foto
- **Given**: El comando CLI ejecutado con `--image <ruta_foto> --level B2`.
- **When**: El ejecutor procesa la imagen.
- **Then**: La consola muestra en tabla la transcripción obtenida, la lista de errores encontrados, las 4 bandas evaluadas y el feedback formativo.

### Scenario 5: Cumplimiento de Umbrales de Benchmark (RF-08)
- **Given**: El dataset extensible con redacciones de referencia humanas.
- **When**: Se ejecuta el runner masivo de benchmark.
- **Then**: El MAE global es $\le 0.5$ bandas y la tasa de coincidencia en $\pm 1$ banda es $\ge 80\%$, resultando en veredicto `APPROVED`.

---

## 7. Definition of Done Checklist
- [ ] Módulo de sanitización EXIF `image_processing.py` implementado.
- [ ] Nodo de transcripción OCR literal `ocr_transcription_node` integrado en LangGraph.
- [ ] Esquemas Pydantic `ai_service/app/schemas/benchmark.py` estrictamente tipados.
- [ ] Estructura `ai_service/data/benchmark/` con muestras fotográficas de prueba y manifiesto `dataset.json`.
- [ ] Motor de métricas y CLI runner operativo para probar fotos individuales y lotes completos.
- [ ] Suite de pruebas unitarias e integración en `ai_service/tests/unit/test_ocr.py` y `test_benchmark.py` pasando al 100%.
- [ ] Sin regresión en las 56 pruebas previas de `backend` y `ai_service`.
- [ ] `ruff check` y `mypy --strict` pasando con 0 errores.
