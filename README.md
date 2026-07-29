# Investigation Platform

Backend for an investigative intelligence platform used by oversight bodies, corporate compliance, and financial investigation teams. The platform supports three applications — Analytics (reports and dashboards), Investigator (relationship graphs and link analysis), and Case Manager (case management and task workflows) — all sharing a single unified search endpoint.

## How to run

### Prerequisites

- Python 3.12
- Docker (for the database)

### Setup

```bash
# Create a virtual environment and install dependencies
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Start the database
docker compose up -d

# Run the application
uvicorn app.main:create_app --factory --reload
```

### Run tests

```bash
source .venv/bin/activate
python -m pytest
```

The application will be available at `http://localhost:8000`. The health check endpoint is at `GET /health`.
