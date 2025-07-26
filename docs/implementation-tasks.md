# Vocabloom Implementation Tasks

---

## Implementation Checklist (MVP Scope)

### 1. Development Environment & Repository
1. [x] Set up monorepo (client + server) for project structure
2. [x] Configure GitHub repository with branch protection and code review rules
3. [x] Add .gitignore, README, and contribution guidelines
4. [x] Set up Prettier and ESLint for code formatting and linting (frontend); Black and flake8 for backend
5. [x] Configure basic testing frameworks (Jest, Vue Testing Library for frontend; Pytest for backend)

### 2. GCP & Cloud Setup
1. [ ] Register GCP account and configure IAM users/roles
2. [ ] Set up Google Cloud DNS for domain management
3. [ ] Set up Google Cloud Storage (GCS) and Cloud CDN for static asset hosting (frontend)
4. [ ] Set up Cloud Run for backend container hosting
5. [ ] Set up Secret Manager for API keys and JWT secrets
6. [ ] Set up Cloud Monitoring and Error Reporting for logging and monitoring
7. [ ] Set up Google-managed SSL/TLS certificates

### 3. CI/CD Pipeline
1. [x] Configure GitHub Actions for automated build, test, and deploy
2. [ ] Set up environment variables and secrets in CI/CD

### 4. Frontend Implementation
1. [x] Scaffold Vue.js app with TypeScript and Vuetify
2. [x] Implement project branding and remove default Vite/Vue content
3. [ ] Set up routing and basic page structure
4. [ ] Implement language selection and term input UI
5. [ ] Implement form validation and error handling
6. [ ] Integrate API calls to backend for translation/explanation
7. [ ] Display translation/explanation results
8. [ ] Add loading and error states
9. [ ] Add basic tests for UI components and flows

### 5. Backend Implementation
1. [x] Scaffold Python FastAPI app
2. [x] Set up Poetry for dependency management
3. [ ] Implement `/api/translate` endpoint
4. [ ] Integrate Gemini API for translation/explanation
5. [ ] Add input validation and error handling middleware
6. [ ] Add logging (Cloud Monitoring integration)
7. [ ] Add basic authentication (JWT, optional for MVP)
8. [ ] Add tests for API endpoints and error cases

### 6. Frontend-Backend Integration
1. [x] Scaffold /api/translate endpoint in backend
2. [x] Connect frontend to backend /api/translate endpoint
3. [x] Display response in frontend UI

### 7. Deployment & Domain
1. [x] Deploy frontend to Firebase Hosting or GCS + Cloud CDN
2. [x] Deploy backend to Cloud Run
3. [x] Configure custom domains via Namecheap DNS (vocabloom.app, api.vocabloom.app)
4. [x] Set up SSL/TLS certificates via Google-managed certificates
5. [x] Test HTTPS and domain routing
6. [ ] Complete Firebase domain verification (DNS propagation in progress)

**Note:** Custom domain vocabloom.app is configured and DNS records are set up. Firebase domain verification is pending DNS propagation (15 minutes to 24 hours expected).

### 8. Public Launch Preparation
1. [ ] Monitor logs and metrics in Cloud Monitoring
2. [ ] Ensure privacy policy and terms of service are available
3. [ ] Open public access to the product
