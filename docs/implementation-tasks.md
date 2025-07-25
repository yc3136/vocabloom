# Vocabloom Implementation Tasks

---

## Implementation Checklist (MVP Scope)

### 1. Development Environment & Repository
1. [x] Set up monorepo (client + server) for project structure
2. [x] Configure GitHub repository with branch protection and code review rules
3. [x] Add .gitignore, README, and contribution guidelines
4. [x] Set up Prettier and ESLint for code formatting and linting (frontend); Black and flake8 for backend
5. [x] Configure basic testing frameworks (Jest, Vue Testing Library for frontend; Pytest for backend)

### 2. AWS & Cloud Setup
1. [ ] Register AWS account and configure IAM users/roles
2. [ ] Set up AWS Route 53 for domain management
3. [ ] Set up AWS S3 and CloudFront for static asset hosting (frontend)
4. [ ] Set up AWS ECS (Fargate) for backend container hosting
5. [ ] Set up Amazon RDS (PostgreSQL) for production database
6. [ ] Set up AWS Secrets Manager for API keys, DB credentials, JWT secrets
7. [ ] Set up AWS CloudWatch for logging and monitoring
8. [ ] Set up AWS Certificate Manager (ACM) for SSL/TLS

### 3. CI/CD Pipeline
1. [ ] Configure GitHub Actions for automated build, test, and deploy
2. [ ] Set up environment variables and secrets in CI/CD

### 4. Frontend Implementation
1. [ ] Scaffold Vue.js app with TypeScript and Vuetify
2. [ ] Set up routing and basic page structure
3. [ ] Implement language selection and term input UI
4. [ ] Implement form validation and error handling
5. [ ] Integrate API calls to backend for translation/explanation
6. [ ] Display translation/explanation results
7. [ ] Add loading and error states
8. [ ] Add basic tests for UI components and flows

### 5. Backend Implementation
1. [ ] Scaffold Python FastAPI app
2. [ ] Set up SQLAlchemy ORM and connect to PostgreSQL (local/dev and AWS RDS)
3. [ ] Implement `/api/translate` endpoint
4. [ ] Integrate Gemini API for translation/explanation
5. [ ] Add input validation and error handling middleware
6. [ ] Add logging (CloudWatch integration)
7. [ ] Add basic authentication (JWT, optional for MVP)
8. [ ] Add tests for API endpoints and error cases

### 6. Database & Persistence
1. [ ] Design and migrate initial database schema (users, logs, etc.)
2. [ ] Set up SQLAlchemy migrations and seed scripts
3. [ ] Test local and cloud database connections

### 7. Deployment & Domain
1. [ ] Deploy frontend to AWS Amplify or S3 + CloudFront
2. [ ] Deploy backend to AWS ECS (Fargate)
3. [ ] Configure custom domains via Route 53 (e.g., www.vocabloom.com, api.vocabloom.com)
4. [ ] Set up SSL/TLS certificates via ACM
5. [ ] Test HTTPS and domain routing

### 8. Public Launch Preparation
1. [ ] Monitor logs and metrics in CloudWatch
2. [ ] Ensure privacy policy and terms of service are available
3. [ ] Open public access to the product
