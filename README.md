# ANAF PDF Generator

Serviciu FastAPI pentru generarea declarațiilor ANAF în format PDF cu XML atașat.

## Declarații suportate

| Declarație | Endpoint | Descriere |
|------------|----------|-----------|
| D112 | `POST /api/v1/d112/generate` | Declarație unică |
| D212 | `POST /api/v1/d212/generate` | Declarație unică (via ANAF API) |
| D300 | `POST /api/v1/d300/generate` | Decont TVA |
| D301 | `POST /api/v1/d301/generate` | Decont special TVA |
| D390 | `POST /api/v1/d390/generate` | Declarație recapitulativă |
| D394 | `POST /api/v1/d394/generate` | Declarație informativă |

## Rulare cu Docker

```bash
docker-compose up -d
```

Serviciul va fi disponibil pe `http://localhost:8001`

## Dezvoltare locală

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Structura proiectului

```
├── app/
│   ├── main.py              # FastAPI app
│   ├── services/            # Generatoare PDF
│   │   ├── d112_generator.py
│   │   ├── d212_generator.py
│   │   ├── d300_generator.py
│   │   ├── d301_generator.py
│   │   ├── d390_generator.py
│   │   └── d394_generator.py
│   └── templates/           # Template-uri PDF ANAF
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Health Check

```bash
curl http://localhost:8001/health
```
