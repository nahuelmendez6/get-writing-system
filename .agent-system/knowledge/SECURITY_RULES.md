# Security & Privacy Rules — Get Idiomas AI Writing System

## 1. Zero Data Retention (ZDR) & LLM Privacy

1. **Mandatory ZDR Policy**:
   - Every external LLM API client (`OpenAI`, `Anthropic`, `Google Gemini`) must be explicitly initialized with **Zero Data Retention** enterprise flags.
   - Student writings must never be stored on provider infrastructure or used for model retraining.
2. **Text Anonymization Filter**:
   - Before any text or image reference is dispatched to `ai_service`, it must pass through an anonymization sanitizer (`core/sanitizer.py`).
   - The sanitizer strips:
     - Student full names and usernames.
     - Email addresses and phone numbers.
     - Identification numbers (DNI, NIE, Passport).
     - School, academy, and instructor names.
     - Specific physical addresses or geolocations.

## 2. GDPR Compliance & Minor Protection

1. **Consent & Guardian Association**:
   - Since users include minors preparing for B1/B2 exams, the system requires verified parental/guardian consent metadata during enrollment.
2. **EXIF Metadata Stripping**:
   - All uploaded handwritten photos must undergo automated EXIF metadata removal (GPS coordinates, camera model, timestamp) before saving to S3 or passing to multimodal models.
3. **Right to Erasure (Forget Me)**:
   - Soft-delete mechanisms must anonymize submission text and delete associated handwritten photographs from S3 when an erasure request is executed.

## 3. Authentication & Password Security

1. **Email-Based Identity (No DNI as Password)**:
   - In strict compliance with **RF-01**, authentication is based exclusively on email and strong passwords.
   - The usage of national ID numbers (DNI) as access passwords or default credentials is strictly prohibited.
2. **Cryptographic Hashing**:
   - Passwords must be hashed using Argon2id or bcrypt (salt rounds $\ge 12$). Plaintext passwords must never be stored or logged.
3. **Token Management**:
   - JWT Access Tokens: short-lived (15 to 30 minutes).
   - JWT Refresh Tokens: stored as cryptographic hashes in Redis with 7-day expiration and automatic rotation upon use.
   - Logout must blacklist active tokens in Redis until their expiration.

## 4. Production Safeguards (RF-02)

1. **DevRoleSwitcher Elimination**:
   - The prototype component `DevRoleSwitcher` and all 1-click demo login buttons must be conditionally excluded from production bundles.
   - If `ENVIRONMENT=production`, attempting to invoke any demo auth endpoint or switch roles without credentials returns HTTP 403 Forbidden.
2. **Demo Account Lockout**:
   - Seeded demo accounts (`admin@cambridge.demo`, `teacher@cambridge.demo`, `student@cambridge.demo`) must not exist in production databases.

## 5. Authorization & Resource Ownership (RBAC)

1. **Role Verification**:
   - Every protected route must verify roles (`ADMIN`, `TEACHER`, `STUDENT`) via FastAPI dependencies.
2. **Object-Level Ownership Checks**:
   - Role verification alone is insufficient. The API must verify resource relationship:
     - Teachers can only view/edit assignments and submissions for courses they explicitly teach.
     - Students can only view assignments of courses where they hold an active enrollment.
     - Students can only access their own submissions and published evaluations.
3. **Draft Evaluation Shielding**:
   - Endpoints queried by students must filter out evaluations with statuses other than `PUBLISHED`.
   - The backend must enforce this at the database query level (`WHERE status = 'PUBLISHED'`), never relying on frontend concealment.

## 6. Storage Security (S3 / MinIO)

1. **Private Buckets Only**:
   - S3 buckets containing handwritten essays or student materials must never allow public read access.
2. **Presigned URLs**:
   - Access to uploaded images is restricted to temporary Presigned URLs with a maximum TTL of 15 minutes.
   - Presigned upload URLs must validate MIME type (`image/jpeg`, `image/png`) and file size ($\le 15$ MB).
