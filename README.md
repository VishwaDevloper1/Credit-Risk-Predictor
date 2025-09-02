# Full-Stack Credit Risk Project (Flask + React + SQLite)

## What this contains
- backend/: Flask API that will train a small model on first run if model missing, stores predictions in SQLite.
- frontend/: Minimal React app to call backend /predict endpoint.

## Running locally
### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
# backend runs at http://0.0.0.0:8000
```

### Frontend (dev)
```bash
cd frontend
npm install
npm start
# open http://localhost:3000 (frontend). Ensure backend is running at port 8000
```

## Deployment notes
- Backend: Render / Railway (free tiers)
- Frontend: Vercel / Netlify
