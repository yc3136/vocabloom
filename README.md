# Vocabloom

An AI-powered language learning platform that provides instant translations, explanations, flashcards, stories, and images for multilingual families.

## 🎯 Project Status

**Current Status:** MVP Complete ✅ | Milestone 2 Complete ✅ | Milestone 3 Complete ✅ | Milestone 4 Complete ✅ | Content Discovery Complete ✅ | Advanced Features Complete ✅

### 🏆 Project Summary
Vocabloom is a comprehensive AI-powered language learning platform that demonstrates full-stack development capabilities with modern technologies. The project showcases:

- **Frontend Development**: Vue.js 3 with TypeScript, Vuetify 3, and responsive design
- **Backend Development**: FastAPI with Python 3.13, SQLAlchemy ORM, and comprehensive API design
- **AI Integration**: Gemini 2.0 Flash API for translations/stories and Imagen 4.0 Standard for image generation
- **Cloud Infrastructure**: Google Cloud Platform with Cloud Run, Firebase, Cloud SQL, and Cloud Storage
- **Database Design**: PostgreSQL with Redis caching and proper indexing
- **DevOps**: Automated deployment scripts, CI/CD pipeline, and environment management
- **Security**: Firebase Auth, Secret Manager, SSL/TLS, and proper CORS configuration
- **User Experience**: Dark mode, mobile responsiveness, unified design system, and comprehensive error handling

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
- **Database:** Cloud SQL PostgreSQL + Redis (quota management)
- **Authentication:** Firebase Auth
- **AI Integration:** Gemini 2.0 Flash API (translations/stories) + Imagen 4.0 Standard (images)
- **Infrastructure:** Google Cloud Platform
  - Cloud Run (Backend)
  - Firebase Hosting (Frontend)
  - Cloud SQL (Database)
  - Cloud Storage (Image storage)
  - Secret Manager (API Keys)
  - Redis (Quota management)
- **Domain:** vocabloom.app with SSL/TLS

### Key Features
- ✅ AI-powered translation and explanation using Gemini 2.0 Flash
- ✅ Multi-language support (20+ languages with native names)
- ✅ Responsive Vue.js frontend with markdown rendering
- ✅ FastAPI backend with proper error handling
- ✅ User authentication with Firebase Auth
- ✅ Flashcard management system with templates and customization
- ✅ Story generation with age-appropriate content
- ✅ Image generation using Imagen 4.0 Standard via Vertex AI
- ✅ Content discovery and search system
- ✅ Dark mode and unified design system
- ✅ Redis-based quota management
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

### Milestone 2 (Completed ✅)
- [x] User authentication with Firebase Auth
- [x] PostgreSQL database integration
- [x] Flashcard creation and management
- [x] User account management and preferences
- [x] Translation history tracking
- [x] Content organization by original word
- [x] LLM response caching system
- [x] Age-appropriate content generation

### Milestone 3 (Completed ✅)
- [x] AI-powered story generation with Gemini 2.0 Flash
- [x] Age-appropriate story content (toddler to middle school)
- [x] Multi-word story generation with context preservation
- [x] Related words system with contextual recommendations
- [x] Story management with search and filtering
- [x] Content discovery and search system
- [x] Unified content interface for translations, flashcards, and stories
- [x] Advanced filtering (language, age range, content type)

### Milestone 4 (Completed ✅)
- [x] AI-powered image generation using Imagen 4.0 Standard
- [x] Text-free educational image generation
- [x] Image gallery with search, filtering, and click-to-open
- [x] AI-generated image titles and descriptions
- [x] Google Cloud Storage integration
- [x] User quota management system
- [x] Immediate UX with toast notifications

### Advanced Features (Completed ✅)
- [x] Dark mode support across all components
- [x] Unified design system with consistent styling
- [x] Mobile-responsive design
- [x] Redis-based quota management
- [x] Comprehensive error handling
- [x] Custom confirmation modals
- [x] Interactive flashcard viewer integration

### Future Enhancements
- [ ] Audio generation for pronunciations
- [ ] Advanced learning features (quizzes, spaced repetition)
- [ ] Community features and content sharing
- [ ] Premium subscription features
- [ ] Mobile app development

## 🔒 Security

This project follows security best practices:
- Service account keys and credentials are excluded from version control
- Project-specific identifiers are genericized in public documentation
- HTTPS is enforced everywhere with automatic SSL/TLS certificates
- Environment variables and secrets are managed via GCP Secret Manager
- CORS is properly configured for frontend-backend communication
- User authentication via Firebase Auth with secure token verification
- Database connections use SSL encryption
- Redis quota management with secure connections

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
