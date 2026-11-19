# Task Specification: TASK-2.2 — Privacidad y Zero Data Retention (ZDR) (SEC-01)

## 1. Metadata
- **Task ID**: `TASK-2.2`
- **Backlog Reference**: `SEC-01`
- **Module / Target Component**: `ai_service` & `backend`
- **Related Requirements**: `RF-03` (Cumplimiento RGPD desde el diseño: consentimiento de menores, ZDR en IA)
- **Author**: Planner Agent
- **Date**: `2026-11-19`
- **Status**: `PLANNED`

---

## 2. Objective & Summary
Implementar de manera rigurosa la capa de seguridad, privacidad y cumplimiento legal del sistema de IA y Backend:
1. **Configuración Estricta de Zero Data Retention (ZDR)** en los clientes y llamadas de API a modelos LLM (`OpenAI`, `Anthropic`, `Google Gemini`), garantizando contractualmente y mediante cabeceras técnicas (`store: false`, directivas enterprise no-retention) que ninguna redacción, texto o imagen de los alumnos sea almacenada en servidores externos o utilizada para reentrenamiento de modelos.
2. **Módulo Exhaustivo de Anonimización de Textos y PII (`ai_service/app/core/sanitizer.py`)**, encargado de purgar nombres de alumnos, nombres de usuario, firmas/saludos, correos electrónicos, números de teléfono, documentos de identidad (DNI, NIE, Pasaportes), nombres de academias/profesores y direcciones físicas antes de cualquier invocación a motores de lenguaje externos, preservando la métrica de palabras y la estructura gramatical para no perjudicar la evaluación Cambridge.
3. **Marco de Validación RGPD para Menores de Edad (`ai_service/app/core/gdpr.py` y contratos en `backend/app/schemas/privacy.py`)**, implementando las reglas de edad según el Art. 8 del RGPD y el Art. 7 de la LOPDGDD española (umbral de 14 años para consentimiento autónomo), verificación de consentimiento de padres/tutores legales (`GuardianConsent`) y soporte técnico para el Derecho al Olvido (*Right to Erasure* / Art. 17 RGPD) con anonimización irreversible y purga de fotografías.

---

## 3. Technical Analysis & Pre-requisites
- **Existing Codebase Dependencies**:
  - `TASK-1.2`: Grafo LangGraph y nodo preliminar `context_prep_node`.
  - `TASK-2.1`: Módulo `image_processing.py` con sanitización EXIF de imágenes de manuscritos.
  - `backend/app/core/models.py`: Estructura base de modelos UUID y timestamps.
- **Pre-requisite Tasks**: `TASK-1.1`, `TASK-1.2`, `TASK-1.3`, `TASK-2.1` (`COMPLETED`).
- **Knowledge References**:
  - [SECURITY_RULES.md](file:///home/nahuel/projects/get/project-root/.agent-system/knowledge/SECURITY_RULES.md) (Secciones 1 y 2).
  - [BUSINESS_RULES.md](file:///home/nahuel/projects/get/project-root/.agent-system/knowledge/BUSINESS_RULES.md).
  - [functional-and-non-functional-requirements.md](file:///home/nahuel/projects/get/project-root/docs/requirements/functional-and-non-functional-requirements.md) (`RF-03`).

---

## 4. Implementation Details

### 4.1. Módulo de Anonimización y Filtro PII (`ai_service/app/core/sanitizer.py`)
- Clase `PIISanitizer`:
  - Detección basada en expresiones regulares avanzadas, validación de dígitos de control y reconocimiento contextual:
    - **Nombres de alumnos y firmas**: Patrones como `Dear [Name]`, `My name is [Name]`, `Signed: [Name]`, `Best regards, [Name]`, `Love, [Name]` y menciones directas $\rightarrow$ `[STUDENT_NAME_REDACTED]`.
    - **Correos electrónicos**: `[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+` $\rightarrow$ `[EMAIL_REDACTED]`.
    - **Números de teléfono**: Formatos españoles (`+34`, `6xx`, `7xx`, `8xx`, `9xx`), internacionales y agrupaciones con guiones o espacios $\rightarrow$ `[PHONE_REDACTED]`.
    - **Identificaciones Nacionales**: DNI español (8 dígitos + letra de control verificada con módulo 23), NIE (letra X/Y/Z + 7 dígitos + letra de control), Pasaportes alfanuméricos $\rightarrow$ `[ID_REDACTED]`.
    - **Centros educativos y docentes**: Menciones a "Get Idiomas", "Cambridge Academy", "Colegio...", "IES...", "Prof. [Name]", "Teacher [Name]" $\rightarrow$ `[INSTITUTION_REDACTED]` / `[INSTRUCTOR_REDACTED]`.
    - **Direcciones físicas y geolocalizaciones**: Calles, avenidas, códigos postales españoles de 5 dígitos (e.g., 28001) $\rightarrow$ `[ADDRESS_REDACTED]`.
  - Método `sanitize(text: str) -> SanitizationResult`:
    - Devuelve `clean_text: str`, `pii_detected_count: int`, `pii_types: list[str]` y `redaction_log: list[RedactionEntry]` (sin almacenar datos personales crudos en texto claro).
- Integración en LangGraph (`ai_service/app/graph/nodes/context_prep.py`):
  - Sustituir la función básica previa por `PIISanitizer.sanitize()`.
  - Enriquecer `EvaluationState` con `sanitized_text`, `pii_detected_count` y `pii_types`.

### 4.2. Módulo de Zero Data Retention (ZDR) (`ai_service/app/core/zdr.py`)
- Clase `ZDRClientManager`:
  - Enforce de políticas ZDR en todas las configuraciones de proveedores LLM:
    - **OpenAI**: Enforce estricto del parámetro `store: False` en todas las llamadas API (evitando persistencia en logs del proveedor) y cabeceras enterprise no-retention.
    - **Anthropic**: Inyección de cabeceras de privacidad y parámetros que prohíben el entrenamiento y logging del proveedor.
    - **Google Gemini**: Verificación de directivas de no retención de datos.
    - **Mock / Local**: Simulación de verificación de políticas ZDR con trazas de auditoría.
  - Excepción `ZDRViolationError`: se dispara si alguna llamada a inferencia intenta omitir las directivas ZDR o si `ENFORCE_ZDR=True` y se detecta una configuración no segura.
  - Función decoradora / context manager `enforce_zdr_policy()` para garantizar la trazabilidad en cualquier invocación externa.

### 4.3. Marco RGPD para Menores y Derecho al Olvido (`ai_service/app/core/gdpr.py` y `backend/app/schemas/privacy.py`)
- Reglas de Consentimiento para Menores (Art. 8 RGPD / Art. 7 LOPDGDD España):
  - Umbral legal: en España, los menores de **14 años** no pueden prestar consentimiento por sí mismos para servicios de la sociedad de la información; requieren consentimiento verificado de sus padres o tutores legales.
  - Menores entre 14 y 17 años: consentimiento propio con asociación obligatoria de datos de contacto de tutor para fines académicos.
  - Función `validate_minor_consent(birth_date: date, guardian_consent: GuardianConsent | None) -> MinorConsentValidationResult`.
- Modelos y Esquemas de Consentimiento:
  - `GuardianConsent`: `guardian_name`, `guardian_email`, `guardian_phone`, `relationship` (`PARENT`, `LEGAL_GUARDIAN`), `verification_method` (`DIGITAL_SIGNATURE`, `VERIFIED_EMAIL`, `ACADEMY_PAPER`), `consent_date`, `document_hash`, `status` (`ACTIVE`, `REVOKED`, `EXPIRED`).
  - `MinorConsentValidationResult`: `is_minor: bool`, `requires_guardian_consent: bool`, `is_valid: bool`, `legal_basis: str`, `errors: list[str]`.
- Utilidades para el Derecho al Olvido (*Right to Erasure* / Art. 17 RGPD):
  - Función `execute_right_to_erasure(student_id: UUID | str, submission_text: str, photo_paths: list[str]) -> ErasureCertificate`:
    - Anonimización criptográfica irreversible del texto del alumno.
    - Eliminación / purga segura de fotos y metadatos EXIF.
    - Generación de certificado de borrado con hash SHA-256 para auditoría sin contener PII.

### 4.4. Esquemas Pydantic y Endpoints de Privacidad
- Esquemas (`ai_service/app/schemas/privacy.py` y `backend/app/schemas/privacy.py`):
  - `SanitizeTextRequest`, `SanitizeTextResponse`, `ZDRStatusResponse`, `MinorConsentValidationRequest`, `ErasureRequest`, `ErasureCertificateResponse`.
- Endpoints en `ai_service` (`ai_service/app/api/v1/endpoints/privacy.py`):
  - `POST /api/v1/privacy/sanitize`: Endpoint interno/externo para sanitizar redacciones y obtener informe de PII detectado.
  - `GET /api/v1/privacy/status`: Consulta el estado de cumplimiento ZDR y directivas de privacidad activas.
- Integración en `POST /api/v1/evaluate`:
  - Retornar en la respuesta los metadatos `zdr_enforced: bool`, `sanitized_pii_count: int` y `pii_types_detected: list[str]`.

---

## 5. Security, Privacy & Compliance (ZDR & RGPD)
- **Zero Data Retention Mandatorio**: Todas las invocaciones a modelos de lenguaje incorporan directivas de no retención.
- **Anonimización Previa al Envío**: Ningún texto sale del límite de la aplicación sin pasar por `PIISanitizer`.
- **Protección de Menores**: Validación determinista de edad y consentimiento según LOPDGDD y RGPD.
- **Trazabilidad sin Fuga de PII**: Los logs registran categorías de PII interceptadas y hashes, nunca valores reales.

---

## 6. Acceptance Criteria & Test Scenarios

### Scenario 1: Anonimización Exhaustiva de PII en Redacción de Alumno
- **Given**: Una redacción de estudiante que incluye nombre propio, email, teléfono español, DNI con letra de control, nombre de la academia y dirección física.
- **When**: Se invoca `PIISanitizer.sanitize()`.
- **Then**: Todos los datos identificativos son reemplazados por sus respectivos tokens de redacción (`[STUDENT_NAME_REDACTED]`, `[EMAIL_REDACTED]`, `[PHONE_REDACTED]`, `[ID_REDACTED]`, `[INSTITUTION_REDACTED]`, `[ADDRESS_REDACTED]`), la estructura gramatical se mantiene intacta y se registra el conteo exacto de PII eliminada.

### Scenario 2: Enforzamiento Estricto de Zero Data Retention (ZDR)
- **Given**: El gestor de clientes ZDR configurado en la aplicación.
- **When**: Se preparan los parámetros y cabeceras para una llamada a OpenAI o Anthropic.
- **Then**: Se valida que `store: False` y las cabeceras de no-retención estén explícitamente presentes; cualquier intento de desactivar ZDR con `ENFORCE_ZDR=True` genera una excepción `ZDRViolationError`.

### Scenario 3: Validación de Consentimiento de Menores (RGPD / LOPDGDD)
- **Given**: La fecha de nacimiento de un estudiante menor de 14 años.
- **When**: Se valida el consentimiento sin aportar autorización del tutor legal.
- **Then**: El resultado determina `requires_guardian_consent=True` e `is_valid=False`. Al aportar un `GuardianConsent` activo, el estado cambia a `is_valid=True`.

### Scenario 4: Ejecución del Derecho al Olvido (Right to Erasure)
- **Given**: Una entrega de redacción almacenada con texto y fotografías asociadas.
- **When**: Se ejecuta la función de ejercicio del Derecho al Olvido.
- **Then**: El texto es sustituido por una versión irreversiblemente anonimizada, se genera una orden de purga para las fotografías y se emite un certificado criptográfico con hash SHA-256.

### Scenario 5: Endpoints de Privacidad y ZDR en API
- **Given**: El microservicio `ai_service` en ejecución.
- **When**: Se consulta `GET /api/v1/privacy/status` o se envía una solicitud a `POST /api/v1/privacy/sanitize`.
- **Then**: La API responde con HTTP 200, certificando el estado ZDR activo y devolviendo el texto sanitizado con su desglose de tipos de PII.

---

## 7. Definition of Done Checklist
- [ ] Módulo `ai_service/app/core/sanitizer.py` implementado con soporte de nombres, emails, teléfonos, DNI/NIE/Pasaportes, instituciones y direcciones.
- [ ] Módulo `ai_service/app/core/zdr.py` implementado con enforzamiento de directivas no-retention (`store: false`).
- [ ] Módulo `ai_service/app/core/gdpr.py` y schemas de consentimiento implementados para minoría de edad y derecho al olvido.
- [ ] Integración en `context_prep_node` y respuesta de evaluación de `ai_service`.
- [ ] Endpoints `/api/v1/privacy/status` y `/api/v1/privacy/sanitize` operativos y documentados en OpenAPI.
- [ ] Schemas de privacidad en `backend` sincronizados.
- [ ] Suite de pruebas unitarias e integración en `ai_service` y `backend` con 100% de éxito.
- [ ] Cero regresiones en los 70 tests preexistentes.
- [ ] Verificación de linter (`ruff check .`) y tipos (`mypy --strict`) con 0 errores.
- [ ] ADR-005 documentado y `CHANGELOG.md` actualizado.
