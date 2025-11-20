# SignalScope Backend API

FastAPI backend for the SignalScope application - network coverage and signal quality analytics platform.

## Setup

### Prerequisites
- Python 3.11+
- pip
- MongoDB (or MongoDB Atlas)

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **macOS/Linux**: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
DATABASE_URL=mongodb://localhost:27017/signalscope
# OR for MongoDB Atlas:
# DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/signalscope

SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database connection
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── auth/
│   │   ├── __init__.py
│   │   └── utils.py     # Authentication utilities
│   ├── routers/         # API route handlers
│   │   ├── auth.py
│   │   ├── towers.py
│   │   ├── reports.py
│   │   └── analytics.py
│   └── utils/
│       ├── __init__.py
│       └── haversine.py  # Distance calculations
├── requirements.txt
├── Procfile             # For Railway/Heroku deployment
├── railway.toml         # Railway deployment config
├── railway.nixpacks.toml
├── .gitignore
├── .railwayignore
└── README.md
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Towers
- `GET /api/towers` - Get all towers (with optional filters)
- `GET /api/towers/{tower_id}` - Get specific tower

### Reports
- `POST /api/reports` - Submit signal report (Protected)
- `GET /api/reports` - Get all reports (Protected)
- `GET /api/reports/user` - Get user's reports (Protected)

### Analytics
- `GET /api/analytics` - Get dashboard analytics (Protected)
- `GET /api/analytics/by-zip` - Get signal data by ZIP code
- `GET /api/analytics/by-carrier` - Get data by carrier

### Coverage
- `GET /api/coverage/estimate` - Estimate signal at coordinates

## Testing

Run the test scripts:
```bash
python test_register.py
python test_mongo.py
```

## Deployment

### Railway

This backend is configured for Railway deployment. The `railway.toml` and `railway.nixpacks.toml` files contain the necessary configuration.

### Other Platforms

The `Procfile` can be used for Heroku or other platforms that support it.

## Development

To seed the database with sample tower data:
```bash
python seed_towers.py
```

