# Vocabloom

An AI-powered language learning platform that provides instant translations and explanations for multilingual families.

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Google Cloud CLI
- Firebase CLI

### Development
```bash
# Start frontend development server
cd client && npm run dev

# Start backend development server
cd server && poetry run uvicorn app.main:app --reload
```

## Deployment

### Full Stack Deployment
Deploy both frontend and backend with one command:
```bash
./deploy.sh
```

### Individual Deployments
Deploy only the backend:
```bash
./deploy-backend.sh
```

Deploy only the frontend:
```bash
./deploy-frontend.sh
```

### Manual Deployment
If you prefer to deploy manually:

**Backend:**
```bash
cd server
gcloud run deploy vocabloom-api --source . --region=us-central1 --allow-unauthenticated
```

**Frontend:**
```bash
cd client
npm run build
firebase deploy --only hosting
```

## Architecture

- **Frontend:** Vue.js 3 + TypeScript + Vuetify
- **Backend:** FastAPI + Python 3.11
- **Infrastructure:** Google Cloud Platform
  - Cloud Run (Backend)
  - Firebase Hosting (Frontend)
  - Cloud Storage (Assets)
  - Secret Manager (API Keys)
- **Domain:** vocabloom.app (with API subdomain)
- **SSL/TLS:** Automatic certificates via Firebase and Cloud Run

## Features

- [x] AI-powered translation and explanation (MVP)
- [x] Multi-language support
- [x] User-friendly interface
- [x] Responsive design
- [x] Custom domain with SSL/TLS
- [x] Automated deployment scripts
- [x] CI/CD pipeline with GitHub Actions

## Security

This project follows security best practices:
- Service account keys and credentials are excluded from version control
- Project-specific identifiers are genericized in public documentation
- HTTPS is enforced everywhere with automatic SSL/TLS certificates
- Environment variables and secrets are managed via GCP Secret Manager
- CORS is properly configured for frontend-backend communication

**Note:** Configuration files (`.firebaserc`, deployment scripts) contain actual project IDs and service names as required for deployment functionality. These are not security risks as they only work with proper authentication and access controls.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
