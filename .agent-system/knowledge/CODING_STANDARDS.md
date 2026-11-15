# Coding Standards — Get Idiomas AI Writing System

## 1. General Principles

1. **Explicit Over Implicit**: Write clear, self-documenting code. Avoid "magic" behavior or hidden mutations.
2. **Strict Typing**: Python 3.12+ type hints and TypeScript strict mode are enforced across the entire codebase.
3. **Layered Architecture**: Respect architectural boundaries (Router -> Service -> Repository -> Database). Routers must remain thin.
4. **Immutability & Safety**: Never modify database models in place without auditing. Protect against SQL injection, XSS, and race conditions.

## 2. Python & FastAPI Backend Standards

### 2.1. File & Module Structure
- Organize backend modules by domain feature (`modules/auth`, `modules/assignments`, `modules/submissions`, etc.).
- Each module should structure its responsibilities cleanly:
  ```
  modules/<feature>/
  ├── __init__.py
  ├── models.py       # SQLAlchemy 2.0 mapped models
  ├── schemas.py      # Pydantic v2 request/response schemas
  ├── repository.py   # Database query abstractions
  ├── service.py      # Business logic orchestration
  └── router.py       # FastAPI route endpoints
  ```

### 2.2. FastAPI & Pydantic Guidelines
- **FastAPI Endpoints**:
  - Always declare explicit `response_model` and `status_code`.
  - Use dependency injection for DB sessions, security tokens, and current user validation:
    ```python
    @router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
    async def create_submission(
        payload: SubmissionCreate,
        db: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_active_student)
    ) -> SubmissionResponse:
        return await submission_service.create(db, payload, current_user.id)
    ```
- **Pydantic v2**:
  - Use `BaseModel` with `ConfigDict(from_attributes=True)`.
  - Use `Field(..., description="...")` with validation constraints (`ge`, `le`, `min_length`, regex).

### 2.3. SQLAlchemy 2.0 & Database Conventions
- Use modern 2.0 declarative syntax with `Mapped` and `mapped_column`:
  ```python
  class Submission(Base):
      __tablename__ = "submissions"

      id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
      assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignments.id"), nullable=False, index=True)
      student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
      status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus), default=SubmissionStatus.DRAFT, nullable=False)
      created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
      updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
  ```
- **Alembic Migrations**:
  - Every schema adjustment requires a migration file.
  - Both `upgrade()` and `downgrade()` must be fully implemented and tested.

## 3. AI Service & LangGraph Standards

1. **State Isolation**: Define explicit TypedDict schemas for graph states with immutability guarantees where required.
2. **Structured Outputs**: All LLM calls returning structured information must use Pydantic models with schema validation.
3. **Resilience & Timeouts**:
   - Wrap external LLM calls with backoff retries and explicit timeouts (max 45s per LLM node).
   - Catch `ValidationError` and route state to a repair/retry node rather than crashing the worker.
4. **Prompt Management**:
   - Prompts must live in dedicated files under `graph/prompts/` and be versioned (e.g., `writing_eval_v1_2.py`).
   - Never concatenate untrusted user text into system instructions without proper delimiter protection.

## 4. Frontend (React & TypeScript) Standards

### 4.1. TypeScript Rules
- Enable strict mode (`"strict": true` in `tsconfig.json`).
- Disallow `any`. Use discriminated unions for polymorphic states:
  ```typescript
  type SubmissionState = 
    | { status: 'DRAFT'; text: string }
    | { status: 'SUBMITTED'; submittedAt: string }
    | { status: 'PUBLISHED'; review: PublishedReview };
  ```

### 4.2. Component Architecture
- Place components inside feature directories (`src/features/<feature>/components`).
- Keep presentation decoupled from API fetching:
  - Use custom hooks for data fetching (`useSubmissions`, `useCorrectionCanvas`).
  - Use presentational components for rendering pure UI (`MistakeCard`, `RubricScoreSliders`).
- Styling:
  - Use Tailwind CSS utility classes. Avoid inline style objects.
  - Follow the visual standards established in the prototype (`prototipe/src/`).

## 5. Error Handling & Logging Standards

- **Standardized API Error Response**:
  ```json
  {
    "detail": {
      "error_code": "RESOURCE_NOT_FOUND",
      "message": "Submission with ID 8a7c... does not exist",
      "details": {}
    }
  }
  ```
- **Logging**:
  - Use structured JSON logging with correlation IDs (`trace_id`, `submission_id`).
  - Never log passwords, tokens, API keys, or student personal information.
