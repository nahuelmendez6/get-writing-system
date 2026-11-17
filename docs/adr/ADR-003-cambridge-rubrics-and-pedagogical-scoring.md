# Architecture Decision Record (ADR): ADR-003 Cambridge Rubrics & Pedagogical Scoring Engine

## 1. Metadata
- **Status**: `Accepted`
- **Date**: `2026-11-17`
- **Authors**: `Documenter Agent / Educational AI Architect`
- **Related Task**: `TASK-1.3`
- **Supercedes / Superceded by**: `N/A`

## 2. Context & Problem Statement
El sistema de corrección asistida por IA para exámenes de inglés requiere un marco formal de calificación pedagógica alineado con los estándares internacionales de evaluación de Cambridge Assessment English (B1 Preliminary, B2 First, C1 Advanced, C2 Proficiency).

Para garantizar validez pedagógica, neutralidad comercial y extensibilidad técnica, se requiere:
1. Modelar rúbricas reutilizables con soporte para criterios ponderados y descriptores de desempeño por banda (0 a 5).
2. Computar una calificación decimal institucional estandarizada en escala de 0.0 a 10.0 a partir del puntaje bruto (0 a 20).
3. Evaluar desviaciones en la longitud del texto con tolerancia de $\pm 10\%$ respecto a los límites de la consigna.
4. Generar feedback pedagógico constructivo y accionable en español sin exponer marcas registradas de Cambridge en informes dirigidos al estudiante.

## 3. Decision Drivers
- **Fidelidad Pedagógica**: Evaluación basada en los 4 criterios oficiales: *Content*, *Communicative Achievement*, *Organisation* y *Language*.
- **Neutralidad de Marca**: Separación rigurosa entre las escalas de evaluación interna y las denominaciones mostradas en el portal del alumno ("Calificación del Writing", "Nivel de Dominio").
- **Flexibilidad de Rúbricas**: Almacenamiento semi-estructurado de descriptores por banda mediante tipos JSONB/JSON para permitir rúbricas institucionales personalizadas sin alterar el esquema de base de datos.
- **Transparencia Cualitativa**: Toda calificación debe estar acompañada de evidencias textuales citadas y feedback constructivo con recomendaciones prácticas.

## 4. Considered Options
1. **Opción A (Calificación Global por LLM sin Rúbrica)**: El modelo asigna directamente una nota de 0 a 10 con una justificación general en un solo paso.
2. **Opción B (Rúbricas Base Relacionales con Descriptores JSONB y Nodos Dedicados en LangGraph)**:
   - Backend: Entidades `Rubric` y `RubricCriterion` con descriptores de banda (0 a 5) en PostgreSQL JSONB y migración Alembic.
   - AI Service: Nodos específicos `rubric_eval` y `feedback_gen` integrados en el pipeline `StateGraph`.
   - Cálculo matemático determinista de la nota institucional sobre 10: $(\text{raw\_score} / 20) \times 10.0$.
3. **Opción C (Tablas Relacionales Rígidas por Banda)**: Una tabla relacional para cada banda (0, 1, 2, 3, 4, 5) con claves foráneas cruzadas para cada descriptor.

## 5. Decision Outcome
Opción elegida: **Opción B (Rúbricas Relacionales con Descriptores JSONB y Nodos Dedicados en LangGraph)**.

Esta arquitectura desacopla la definición académica de las rúbricas (gestionable vía API REST en backend) de la ejecución de inferencia pedagógica en `ai_service`.

### 5.1. Consecuencias Positivas
- **Trazabilidad y Calibración**: Cada criterio Cambridge recibe una puntuación individual (0 a 5) con descriptor oficial asociado y justificación basada en el texto.
- **Fórmula Matemática Objetiva**: La nota sobre 10 es calculada de forma determinista mediante $(\text{Total raw} / 20) \times 10.0$, eliminando alucinaciones numéricas del LLM.
- **Control de Penalización por Longitud**: Desviaciones $> 10\%$ sobre `min_words` o `max_words` disparan automáticamente `length_penalty: true` y afectan el criterio *Content*.
- **Feedback Estructurado para el Alumno**: Estructura fija de 3 elementos: síntesis general, fortalezas (2-4), áreas de mejora (2-4) y exactamente 3 consejos accionables (`actionable_tips`).

### 5.2. Consecuencias Negativas y Mitigaciones
- **Complejidad del Grafo**: Se incorporan 2 nodos adicionales al pipeline LangGraph (`rubric_eval` y `feedback_gen`), incrementando la profundidad del grafo a 7 nodos.
  - *Mitigación*: Validación estricta en `validator_node` con estructuras fallback válidas para garantizar continuidad en caso de respuestas incompletas.

## 6. Implementation Notes & Guidelines
- La política de marca neutral debe ser respetada en cualquier pantalla o exportación PDF: nunca citar "Cambridge Assessment" como emisor de la calificación institucional.
- Las plantillas predeterminadas de Cambridge B2 First y C1 Advanced deben mantenerse idempotentes a través del servicio `seed_default_rubrics`.
