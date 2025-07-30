# Vocabloom

An AI-powered language learning platform that provides instant translations and explanations for multilingual families.

## 🎯 Project Status

**Current Status:** MVP Complete ✅ | Milestone 2 In Progress 🚧

**Production URLs:**
- **Frontend**: https://vocabloom.app (custom domain)
- **Backend**: Cloud Run (URL dynamically determined during deployment)
- **Database**: Cloud SQL PostgreSQL (vocabloom-db instance)
- **GitHub**: https://github.com/yc3136/vocabloom

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Google Cloud CLI
- Firebase CLI
- Poetry (Python dependency management)

### Local Development
```bash
# Start the complete local development stack
./run_vocabloom.sh

# Or start components individually:
# Frontend development server
cd client && npm run dev

# Backend development server
cd server && poetry run uvicorn app.main:app --reload
```

## Deployment

### Unified Deployment Script
The `deploy.sh` script provides flexible deployment options:

```bash
# Deploy everything (default)
./deploy.sh

# Deploy specific components
./deploy.sh --frontend    # Frontend only
./deploy.sh --backend     # Backend only
./deploy.sh --database    # Database setup only
./deploy.sh -f -b         # Frontend and backend only

# Show help
./deploy.sh --help
```

### What Each Option Does:

- **`--all` (default)**: Sets up database, deploys backend, and deploys frontend
- **`--frontend`**: Deploys frontend to Firebase Hosting with dynamic backend URL
- **`--backend`**: Deploys backend to Cloud Run with production database
- **`--database`**: Sets up Cloud SQL database and user (safe to run multiple times)

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

## 🏗️ Architecture

### Tech Stack
- **Frontend:** Vue.js 3 + TypeScript + Vuetify 3
- **Backend:** FastAPI + Python 3.13 + SQLAlchemy
- **Database:** Cloud SQL PostgreSQL
- **Authentication:** Firebase Auth
- **AI Integration:** Gemini 2.0 Flash API
- **Infrastructure:** Google Cloud Platform
  - Cloud Run (Backend)
  - Firebase Hosting (Frontend)
  - Cloud SQL (Database)
  - Secret Manager (API Keys)
- **Domain:** vocabloom.app with SSL/TLS

### Key Features
- ✅ AI-powered translation and explanation using Gemini 2.0 Flash
- ✅ Multi-language support (20+ languages with native names)
- ✅ Responsive Vue.js frontend with markdown rendering
- ✅ FastAPI backend with proper error handling
- ✅ User authentication with Firebase Auth
- ✅ Flashcard management system
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Custom domain with SSL/TLS
- ✅ Automated deployment scripts
- ✅ Local development environment setup

## 📋 Features

### MVP (Completed ✅)
- [x] AI-powered translation and explanation using Gemini 2.0 Flash
- [x] Multi-language support (20+ languages)
- [x] User-friendly interface with responsive design
- [x] Custom domain with SSL/TLS
- [x] Automated deployment scripts
- [x] Local development environment

### Milestone 2 (In Progress 🚧)
- [x] User authentication with Firebase Auth
- [x] PostgreSQL database integration
- [x] Flashcard creation and management
- [x] User account management
- [x] Translation history tracking
- [ ] Flashcard collections and organization
- [ ] Advanced user settings

### Future Milestones
- [ ] Image generation for flashcards
- [ ] Advanced learning features
- [ ] Mobile app development
- [ ] Social features and sharing

## 🔒 Security

This project follows security best practices:
- Service account keys and credentials are excluded from version control
- Project-specific identifiers are genericized in public documentation
- HTTPS is enforced everywhere with automatic SSL/TLS certificates
- Environment variables and secrets are managed via GCP Secret Manager
- CORS is properly configured for frontend-backend communication
- User authentication via Firebase Auth with secure token verification
- Database connections use SSL encryption

**Note:** Configuration files (`.firebaserc`, deployment scripts) contain actual project IDs and service names as required for deployment functionality. These are not security risks as they only work with proper authentication and access controls.

## 🛠️ Development

### Project Structure
```
vocabloom/
├── client/          # Vue.js frontend
├── server/          # FastAPI backend
├── docs/            # Documentation
├── deploy.sh        # Unified deployment script
└── run_vocabloom.sh # Local development setup
```

### Key Commands
```bash
# Local development
./run_vocabloom.sh

# Deployment
./deploy.sh              # Deploy everything
./deploy.sh --frontend   # Frontend only
./deploy.sh --backend    # Backend only
./deploy.sh --database   # Database setup only

# Help
./deploy.sh --help
```

### Environment Setup
1. Clone the repository
2. Install dependencies (see Prerequisites)
3. Set up environment files:
   - `client/.env` (copy from `client/env.example`)
   - `server/.env` (copy from `server/env.example`)
4. **Important**: All API keys and secrets are managed through Google Cloud Secret Manager
   - No need to add API keys to `.env` files
   - Secrets are automatically loaded from Secret Manager
5. Run `./run_vocabloom.sh` for local development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📚 Documentation

- **Deployment Guide**: See `DEPLOYMENT.md` for detailed deployment instructions
- **Technical Design**: See `docs/technical-design.md` for architecture details
- **Product Requirements**: See `docs/product-requirements.md` for feature specifications
- **Implementation Tasks**: See `docs/implementation-tasks.md` for development roadmap
