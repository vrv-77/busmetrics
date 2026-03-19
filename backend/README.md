# Backend - BusMetric Fuel API

## Run

```bash
python -m venv .venv
# activate venv
pip install -r requirements.txt
copy .env.example .env
python run.py
```

## API docs

- Swagger UI: `http://localhost:8000/docs`

## Tests

```bash
.venv\\Scripts\\python -m pytest -q
```

## ETL highlights

- Deteccion real de archivo: `.xlsx`, `.xls`, `.xls` HTML
- Preview de columnas + mapeo manual
- Normalizacion, calidad de datos, alertas y deduplicacion historica
