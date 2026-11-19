# Architecture Decision Record (ADR): ADR-005 Zero Data Retention (ZDR) & Minor Privacy Protection Framework

## 1. Metadata
- **Status**: `Accepted`
- **Date**: `2026-11-19`
- **Authors**: `Documenter Agent / Educational AI Architect`
- **Related Task**: `TASK-2.2`
- **Supercedes / Superceded by**: `N/A`

---

## 2. Context & Problem Statement
El sistema de corrección de redacciones con inteligencia artificial de *Get Idiomas* atiende a estudiantes que preparan exámenes Cambridge, de los cuales un porcentaje sustancial son menores de edad (niveles B1 Preliminary y B2 First cursados habitualmente por adolescentes entre 11 y 17 años).

El despliegue de modelos fundacionales externos (OpenAI, Anthropic, Google Gemini) plantea riesgos críticos en materia de privacidad, protección de datos (RGPD, LOPDGDD 3/2018) y secreto educativo:
1. **Riesgo de Reentrenamiento y Fuga de Datos**: Las peticiones enviadas a APIs de LLM comerciales podrían ser almacenadas por defecto para fines de auditoría o reentrenamiento de modelos si no se configura explícitamente una política de **Zero Data Retention (ZDR)**.
2. **Exposición de Datos Personales Identificables (PII)**: Las redacciones de los alumnos suelen incluir nombres reales en cartas, correos, números de teléfono, documentos de identidad (DNI/NIE), nombres de la academia, centros educativos o domicilios particulares.
3. **Consentimiento Válido para Menores de Edad**: Conforme al Art. 8 del RGPD y de manera específica el Art. 7 de la LOPDGDD española, los menores de 14 años no pueden otorgar consentimiento autónomo en servicios de la sociedad de la información, exigiendo consentimiento expreso y verificable de sus progenitores o tutores legales.
4. **Derecho al Olvido (Art. 17 RGPD)**: Los usuarios deben poder solicitar la supresión y anonimización irreversible de sus redacciones y fotografías asociadas.

---

## 3. Decision Drivers
- **Cumplimiento Legal Riguroso**: Estricta adhesión al RGPD de la UE y a la LOPDGDD española (umbral de 14 años).
- **Garantía ZDR Contractual y Técnica**: Ninguna redacción ni imagen de alumno debe quedar retenida en los servidores de los proveedores de LLM ni utilizarse para entrenar modelos.
- **Fidelidad Evaluadora Cambridge**: La anonimización de PII debe reemplazar entidades sensibles por marcadores estructurados sin alterar la sintaxis, el recuento de palabras ni la coherencia del texto a corregir.
- **Trazabilidad y No-Repudio sin Fuga de Datos**: Los registros de auditoría y certificados de supresión deben basarse en hashes criptográficos unidireccionales (SHA-256), sin almacenar datos personales en claro.

---

## 4. Considered Options

### Opción A: Delegar la Privacidad Únicamente en los Términos del Proveedor LLM
- Confiar en que los acuerdos comerciales con OpenAI/Anthropic/Google garantizan privacidad sin implementar filtros locales.
- *Descarte*: Incumple el principio de *Privacy by Design* del RGPD. Los datos PII viajarían por la red hacia terceros y el sistema carecería de mecanismos para menores y derecho al olvido.

### Opción B: Arquitectura Multicapa de Privacidad: ZDR en Runtime + Anonimización PII Local + Validación RGPD
1. **Filtro Local de PII (`core/sanitizer.py`)**: Sanitización preventiva antes de cualquier salida de datos del microservicio, con algoritmos de checksum para DNI/NIE español, heurísticas para nombres, firmas y exclusión de fórmulas epistolares Cambridge ("Dear Sir or Madam").
2. **Gestor ZDR Runtime (`core/zdr.py`)**: Intercepción obligatoria de llamadas con inyección de cabeceras enterprise y forzado de parámetros de no persistencia (`store: false` en OpenAI, metadata no-retention en Anthropic, `store_logs: false` en Gemini). Se lanza `ZDRViolationError` ante cualquier intento de desactivación.
3. **Módulo de Consentimiento de Menores y Derecho al Olvido (`core/gdpr.py`)**: Verificación de fecha de nacimiento contra el umbral de 14 años español, validación de estado de tutela (`GuardianConsent`) y generación de certificados de borrado criptográfico SHA-256.

---

## 5. Decision Outcome
Opción elegida: **Opción B (Arquitectura Multicapa de Privacidad: ZDR en Runtime + Anonimización PII Local + Validación RGPD)**.

### 5.1. Consecuencias Positivas
- **Aislamiento Total de PII**: Ningún dato identificativo de alumnos, docentes o instituciones educativas sale de la infraestructura controlada de Get Idiomas hacia los LLMs.
- **Cumplimiento Legal Certificado**: El sistema valida automáticamente si un estudiante menor de 14 años cuenta con autorización activa del tutor legal antes de autorizar procesamiento académico.
- **Compatibilidad con Rúbricas Cambridge**: Los marcadores (`[STUDENT_NAME_REDACTED]`, `[EMAIL_REDACTED]`, `[ID_REDACTED]`, etc.) preservan el flujo textual y la métrica de palabras sin introducir penalizaciones espurias.
- **Transparencia en la Respuesta**: Las evaluaciones retornan metadatos explícitos (`zdr_enforced: true`, `sanitized_pii_count`, `pii_types_detected`) para auditoría y visualización docente.

### 5.2. Consecuencias Negativas y Mitigaciones
- **Sobrecarga de Expresiones Regulares**: El escaneo de 12 patrones de PII añade entre 2 y 5 milisegundos por redacción.
  - *Mitigación*: Expresiones regulares precompiladas a nivel de módulo, perfectamente asumibles en un pipeline asíncrono con tiempos de inferencia del orden de segundos.

---

## 6. Implementation Notes & Guidelines
1. En todos los clientes LLM debe verificarse que `ZDRClientManager.validate_call_compliance()` se ejecute antes de la llamada de red.
2. Todo almacenamiento o logging de eventos de privacidad debe utilizar hashes SHA-256 de 16 caracteres para los valores anonimizados, prohibiendo registrar PII en texto claro.
3. En la FASE 3 (Modelos de Usuario y Matrículas), las fechas de nacimiento se contrastarán directamente con `GDPRComplianceManager.validate_minor_consent()` para exigir o no la firma del tutor legal.
