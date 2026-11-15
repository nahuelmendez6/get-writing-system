# Architecture Decision Record (ADR): ADR-002 LangGraph Evaluation Pipeline & AI Detection

## 1. Metadata
- **Status**: `Accepted`
- **Date**: `2026-11-15`
- **Authors**: `Documenter Agent / AI Systems Architect`
- **Related Task**: `TASK-1.2`
- **Supercedes / Superceded by**: `N/A`

## 2. Context & Problem Statement
La evaluación pedagógica automatizada de textos de examen Cambridge (B2 First y C1 Advanced) requiere un procesamiento secuencial por etapas: sanitización de datos personales, análisis ortográfico y gramatical con referencias posicionales, generación de modelos exemplares de reescritura, detección de posibles textos generados por IA, y validación estricta de esquemas antes de retornar datos al backend académico.
Se necesita una arquitectura resiliente que permita reintentar llamadas ante respuestas mal formateadas sin provocar caídas del servicio y garantizando la política de Zero Data Retention (ZDR).

## 3. Decision Drivers
- Desacoplamiento total entre la API académica de FastAPI y el motor de IA.
- Control explícito de estados y transiciones en grafos dirigidos con reintentos controlados.
- Anonimización previa de PII para cumplimiento estricto de RGPD en entornos educativos.
- Prevención de falsos positivos en detección de autoría sintética mediante umbrales parametrizables.
- Tiempos de respuesta predecibles con límites de tiempo (timeout) por nodo.

## 4. Considered Options
1. **Opción A (Monolito de Prompts en Backend)**: Llamadas directas desde el backend a APIs de LLM con prompts extensos en un solo paso.
2. **Opción B (Servicio Aislado con LangGraph StateGraph)**: Microservicio `ai_service` dedicado que modela el flujo como un grafo de estado (`EvaluationState`) con nodos especializados y bucle de reparación/reintento.
3. **Opción C (Chain secuencial tradicional con LangChain SimpleSequentialChain)**: Flujo lineal sin control de estados tipados ni bucles condicionales de reintento.

## 5. Decision Outcome
Opción elegida: **Opción B (LangGraph StateGraph)**, porque proporciona aislamiento arquitectónico, tipado estricto del estado en cada nodo, recuperación automática ante salidas no conformes mediante transiciones condicionales, y garantiza que el frontend y el backend nunca invoquen directamente a los proveedores de LLM.

### 5.1. Consecuencias Positivas
- Cada nodo (`context_prep`, `writing_analysis`, `exemplar_gen`, `ai_detector`, `validator`) tiene una responsabilidad única y comprobable en aislamiento.
- Los reintentos están acotados a un máximo de 2 intentos, evitando bucles infinitos de consumo de tokens.
- El esquema de respuesta tipado (`EvaluationResponse`) garantiza contratos inmutables para el backend y workers de Celery.
- Cumplimiento de ZDR documentado y verificado en la raíz del servicio.

### 5.2. Consecuencias Negativas y Mitigaciones
- Mayor número de componentes y necesidad de gestionar un microservicio adicional.
  - *Mitigación*: Se orquesta mediante `docker-compose.yml` en la red compartida `get_network` y se provee modo mock determinista para pruebas locales.

## 6. Implementation Notes & Guidelines
- Los nuevos nodos de evaluación (ej. evaluación de rúbricas en `TASK-1.3`) deben agregarse al grafo `StateGraph` respetando el esquema `EvaluationState`.
- Ningún nodo de LLM debe superar los 45 segundos de timeout.
