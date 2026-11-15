# AI Service — Get Idiomas Writing Evaluation

Microservicio especializado en la evaluación automática de redacciones académicas de inglés (CEFR B2 First y C1 Advanced) mediante pipelines orquestados con **LangGraph**.

## Arquitectura del Servicio

El servicio implementa un grafo de estado dirigido (`StateGraph`) estructurado en 5 nodos principales:

```
[START]
   │
   ▼
[context_prep_node]      # Anonimización PII, recuento de palabras y carga de directrices B2/C1
   │
   ▼
[writing_analysis_node]  # Detección de fallos ortográficos, gramaticales y léxicos con offsets
   │
   ▼
[exemplar_gen_node]      # Generación de reescritura ejemplar Banda 5
   │
   ▼
[ai_detector_node]       # Detección de patrones sintéticos y alerta de autoría por IA
   │
   ▼
[validator_node]         # Validación estricta con Pydantic v2 y control de reintentos
   │
   ├── (Si falla y reintentos < 2) ──► [writing_analysis_node]
   │
   └── (Si es válido o reintentos >= 2) ──► [END]
```

## Políticas de Privacidad y ZDR

- **Zero Data Retention (ZDR)**: Forzado por defecto (`ENFORCE_ZDR=true`). Las redacciones no se utilizan para reentrenar modelos fundacionales.
- **Anonimización PII**: Eliminación automática de direcciones de correo y teléfonos antes de la evaluación.

## Endpoints

- `GET /health`: Verificación de salud y estado de la política ZDR.
- `POST /internal/v1/evaluate`: Ejecución completa del pipeline LangGraph sobre la redacción.
- `GET /docs`: Documentación interactiva Swagger UI.

## Ejecución Local y Pruebas

```bash
cd ai_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Ejecutar tests y cobertura
pytest -v --cov=app

# Verificaciones estáticas
ruff check .
ruff format --check .
mypy --strict app tests
```
