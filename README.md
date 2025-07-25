# Vocabloom

Vocabloom is an AI-powered web platform designed for multilingual parents to effortlessly generate and save custom multilingual text and image content, simplifying the process of teaching complex terms to their children. 

## Local Development

### Prerequisites
- Node.js 20+
- Python 3.9+
- Poetry (for backend)

### Running the Full Stack
From the project root:
```bash
./run_vocabloom.sh
```
- This will start the backend (FastAPI) and frontend (Vue + Vuetify) for local development.
- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:5173

### Running Backend Only
From the project root:
```bash
cd server
./run_server.sh
```
- This will kill any previous backend instance on port 8000 and start a new one.

### Running Frontend Only
From the project root:
```bash
cd client
npm run dev
```

### Testing the Integration
- Open the frontend in your browser (http://localhost:5173)
- Enter a term and click "Look up" to see the backend response displayed below the button.
