# Architecture Decision Record (ADR): ADR-004 Multimodal Literal OCR & Benchmark Validation Harness

## 1. Metadata
- **Status**: `Accepted`
- **Date**: `2026-11-17`
- **Authors**: `Documenter Agent / Educational AI Architect`
- **Related Task**: `TASK-2.1`
- **Supercedes / Superceded by**: `N/A`

## 2. Context & Problem Statement
En la academia *Get Idiomas*, las redacciones de examen de los estudiantes se realizan predominantemente de forma manuscrita en papel y se capturan mediante fotografías de teléfono móvil. Para validar empíricamente la efectividad del motor de IA antes de programar las interfaces de usuario (estrategia *AI-First*), se requiere:
1. Soportar la ingestión de fotografías de redacciones manuscritas (`JPEG`, `PNG`, `WEBP`) de forma nativa en el pipeline.
2. Garantizar el cumplimiento del RGPD eliminando completamente los metadatos EXIF (geolocalización GPS, timestamp, hardware del teléfono) antes de cualquier procesamiento o almacenamiento.
3. Transcribir el texto manuscrito bajo el **Principio de Transcripción Literal**: el OCR debe preservar fielmente todas las faltas de ortografía, erratas, fallos gramaticales y omisiones de puntuación del alumno, prohibiendo estrictamente la autocorrección o embellecimiento del texto durante la fase de visión.
4. Construir un arnés de pruebas y CLI interactivo capaz de ejecutar pruebas instantáneas sobre una fotografía individual o procesar lotes de benchmark masivos calculando Mean Absolute Error ($\text{MAE} \le 0.50$) y concordancia en $\pm 1$ banda ($\ge 80\%$).

## 3. Decision Drivers
- **Fidelidad Evaluadora**: Si el OCR corrigiese automáticamente las faltas de ortografía del estudiante, el evaluador de Cambridge no podría medir la competencia real de *Language*, falseando la nota.
- **Privacidad y RGPD para Menores**: Las fotografías tomadas en hogares o centros de estudio contienen metadatos EXIF sensibles que deben purgarse inmediatamente.
- **Flexibilidad Operativa y Verificación Rápida**: El equipo docente debe poder probar una foto de redacción en segundos por línea de comandos y obtener la transcripción, los errores detectados y la nota.
- **Independencia de Formato**: El pipeline debe procesar de forma idéntica redacciones procedentes de fotografías o introducidas digitalmente como texto plano.

## 4. Considered Options
1. **Opción A (OCR Tradicional Tesseract / EasyOCR)**:
   - Uso de motores OCR clásicos basados en redes neuronales convolucionales.
   - *Descarte*: Dificultad extrema para interpretar caligrafía cursiva variada de estudiantes y alta tasa de errores de segmentación.
2. **Opción B (Transcripción Multimodal con Visión LLM y Regla de Transcripción Literal Estricta)**:
   - Sanitización EXIF previa con Pillow (`Image.copy()` y limpieza de `info`).
   - Nodo de visión multimodal en LangGraph con prompt especializado que prohíbe explícitamente autocorregir.
   - Puntero transparente en `EvaluationState` hacia `extracted_text` y `student_text`.
   - Arnés de benchmark CLI interactivo con soporte de dataset mixto (fotos y texto).

## 5. Decision Outcome
Opción elegida: **Opción B (Transcripción Multimodal con Visión LLM y Regla de Transcripción Literal Estricta)**.

### 5.1. Consecuencias Positivas
- **Preservación de Errores Pedagógicos**: Los errores del estudiante se transfieren intactos al nodo `writing_analysis` y `rubric_eval`, asegurando una evaluación representativa de su nivel real.
- **Protección de Datos Garantizada**: El módulo `image_processing.py` purga metadatos EXIF y restringe formatos y tamaños de imagen de forma preventiva.
- **Arnés de Pruebas Unificado**: Un único CLI (`ai_service/scripts/run_benchmark.py`) permite evaluar fotos sueltas o datasets de 60 redacciones, reportando MAE y acierto de bandas.
- **Excelente Rendimiento Empírico**: El benchmark de 60 muestras alcanzó un $\text{MAE} = 0.306$ bandas (superando la meta $\le 0.50$) y un $99.6\%$ de acierto en $\pm 1$ banda (superando la meta $\ge 80\%$).

### 5.2. Consecuencias Negativas y Mitigaciones
- **Dependencia de Librería de Imagen**: Incorporación de `Pillow>=10.0.0` en `ai_service`.
  - *Mitigación*: Paquete estándar de la industria, ligero (~7 MB) y con licencia permisiva BSD.

## 6. Implementation Notes & Guidelines
- En el prompt de transcripción OCR siempre debe figurar la directiva en mayúsculas: `DO NOT AUTOCORRECT OR POLISH MISTAKES`.
- El CLI de benchmark debe mantenerse extensible para recibir fotos adicionales en `ai_service/data/benchmark/images/`.
