# SettleLens AI

An AI-powered fintech settlement investigation agent for Origin Hackathon PS-8.

## Overview

SettleLens AI takes a transaction ID, traces it across mock gateway, bank, and ledger data, explains the settlement status/reason in plain English, and gives an honest exception list when uncertain.

## Project Structure

```
settlelens/
├── backend/                  # FastAPI backend
│   ├── app/                  # Application code
│   ├── data/                 # CSV mock data
│   ├── tests/                # Backend tests
│   └── ... 
├── frontend/                 # React + Vite frontend
│   ├── src/                  # Source code
│   └── ...
└── ...
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 16+ (with npm or yarn)
- FreeLLMAPI running at http://127.0.0.1:31415/v1

### Backend Setup

1. Clone the repository
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy the environment example:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to set your `FREELLMAPI_API_KEY`.
6. Seed the database with mock data:
   ```bash
   python -m app.services.data_loader
   ```
7. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy the environment example (if using Vite env variables):
   ```bash
   cp .env.example .env
   ```
   Note: Vite requires variables to start with `VITE_` so they are injected into the client.
4. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

## Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests (if any)
```bash
cd frontend
npm test
```

## Environment Variables

### Backend (`.env`)
- `FREELLMAPI_API_KEY`: Your FreeLLMAPI API key (required)
- `FREELLMAPI_BASE_URL`: Base URL for FreeLLMAPI (default: http://127.0.0.1:31415/v1)
- `FREELLMAPI_MODEL`: Model to use (default: auto)
- `DATABASE_URL`: SQLite database URL (default: sqlite:///./settlelens.db)
- `BACKEND_HOST`: Host to bind the backend (default: 0.0.0.0)
- `BACKEND_PORT`: Port for the backend (default: 8000)

### Frontend (`.env` in frontend/)
- `VITE_API_URL`: URL of the backend API (default: http://localhost:8000)

## Mock Data Scenarios

The mock data includes the following scenarios:
- Successful settlement
- Delayed bank settlement
- Failed transaction
- Missing ledger entry
- Amount mismatch
- Duplicate transaction
- Unknown transaction ID

## API Endpoints

### POST /investigate
Investigate a transaction by ID.

**Request Body:**
```json
{
  "transaction_id": "string"
}
```

**Response:**
```json
{
  "status": "SETTLED | PENDING | FAILED | PARTIAL | UNKNOWN",
  "plain_english": "string",
  "exceptions": ["string"],
  "confidence": 0.0-1.0
}
```

## License

MIT