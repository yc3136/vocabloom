# Vocabloom Technical Design

**Document Version:** 1.1
**Last Updated:** July 25, 2025

---

## 1. Overview

This document outlines the technical architecture, technology choices, and infrastructure for Vocabloom, supporting all product requirements and milestones as described in the product requirements document.

---

## 2. Tech Stack Selection

### 2.1. Frontend

- **Framework:** Vue.js (with TypeScript)
- **UI Library:** Vuetify (for accessibility and rapid prototyping)
- **State Management:** Vuex (MVP), with potential migration to Pinia for advanced features
- **Routing:** Vue Router
- **Form Handling:** Vuelidate or VueUseForm
- **Internationalization:** vue-i18n
- **Testing:** Jest, Vue Testing Library, Cypress (E2E)

### 2.2. Backend

- **Language/Runtime:** Python 3.x
- **Framework:** FastAPI (for high performance, async support, and OpenAPI docs)
- **API:** REST (with OpenAPI/Swagger documentation), with GraphQL considered for future extensibility
- **Authentication:** JWT (JSON Web Tokens), OAuth 2.0 (Google, Apple, etc.)
- **Database:** PostgreSQL (primary), Redis (caching, session management)
- **ORM:** SQLAlchemy (for PostgreSQL)
- **Testing:** Pytest, HTTPX

### 2.3. AI/ML Integration

- **Provider:** Gemini API (primary for LLM-powered translation, explanation, and image generation)
- **Image Generation:** Gemini API (primary); fallback to OpenAI DALL·E or Stability AI if quality or moderation needs are not met
- **Image Moderation:** Use Gemini API’s built-in moderation where possible; supplement with OpenAI Moderation API, Google Cloud Vision SafeSearch, or AWS Rekognition for stricter requirements
- **Audio/Video:** Google Cloud Text-to-Speech, AWS Polly, or ElevenLabs (for audio pronunciation)

### 2.4. Cloud & Infrastructure

- **Cloud Provider:** Google Cloud Platform (GCP) (preferred for cost control, managed services, and Gemini integration)
- **Core Services:**
  - **Compute:** Cloud Run (for containerized FastAPI backend) or Cloud Functions (for serverless workloads)
  - **Database:** Cloud SQL (PostgreSQL)
  - **Object Storage:** Google Cloud Storage (GCS) (for images, audio, exports)
  - **CDN:** Cloud CDN
  - **Cache:** MemoryStore (Redis)
  - **Authentication:** Firebase Authentication (optional, if not rolling custom JWT/OAuth)
  - **Monitoring:** Cloud Monitoring, Error Reporting (for error tracking)
  - **CI/CD:** GitHub Actions, Cloud Build

### 2.5. DevOps & Tooling

- **Containerization:** Docker (for local development and deployment)
- **Infrastructure as Code:** Terraform or Google Cloud Deployment Manager
- **Version Control:** Git (GitHub)
- **Linting/Formatting:** ESLint, Prettier (frontend); Black, isort, flake8 (backend)
- **Documentation:** Storybook (UI), Swagger (API), Markdown (internal docs)

### 2.6. Accessibility & Compliance

- **Accessibility Testing:** axe-core, Lighthouse
- **Compliance:** GDPR, CCPA (data privacy), WCAG 2.1 AA (accessibility)

---

## 3. Setup Specifications

### 3.1. Local Development

- **Minimum Requirements:**  
  - Node.js >= 18.x (for frontend tooling)  
  - Python >= 3.10 (for backend)  
  - Docker Desktop  
  - PostgreSQL (local or Dockerized)  
  - Redis (local or Dockerized)  
  - GCloud CLI (for cloud integration)  
  - Yarn, npm, or pnpm (frontend)

- **Recommended IDE:** VSCode (with recommended extensions for TypeScript, ESLint, Prettier, Python, Docker)

### 3.2. Environments

- **Development:** Local Docker Compose, feature branches
- **Staging:** GCP (mirrors production, used for QA)
- **Production:** GCP (multi-region, auto-scaling, managed services)

---

## 4. Rationale

- **Suitability:** Vue.js and FastAPI are both modern, high-performance frameworks with strong community support and rapid development cycles. They are well-suited for building scalable, maintainable web applications and APIs.
- **Cloud Provider Choice:**
  - **GCP was chosen over AWS** for the following reasons:
    - **Cost Control:** GCP provides a $300 free credit and always-free tier, with a hard spending limit before you upgrade to a paid account, making it safer for side projects and experimentation.
    - **Gemini Integration:** Native and seamless integration with Gemini API and other Google AI/ML services.
    - **Managed Services:** GCP offers robust managed services for compute, storage, database, and monitoring, all compatible with the project’s tech stack.
    - **Developer Experience:** GCP’s developer tooling and documentation are well-suited for rapid prototyping and deployment.

---

## 5. MVP Design

### 5.1. User Journey

1. **User Input:**
   - The user enters an English term and selects a target language from a dropdown menu on the web app.
   - The user submits the request.
2. **Frontend Processing:**
   - The Vue.js frontend validates the input (non-empty, valid selection).
   - A POST request is sent to the backend API with the term and selected language.
3. **Backend Processing:**
   - The FastAPI backend receives the request, authenticates the user (if required), and validates the payload.
   - The backend calls the Gemini API to generate a translation or explanation for the term in the target language.
   - The backend processes the AI response, applies any necessary formatting or error handling, and returns the result to the frontend.
4. **Frontend Display:**
   - The frontend receives the response and displays the translation/explanation to the user.
   - If an error occurs (e.g., invalid input, API failure), a user-friendly error message is shown.

### 5.2. Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend (Vue.js)
    participant B as Backend (FastAPI)
    participant G as Gemini API

    U->>F: Enter term & select language
    F->>F: Validate input
    F->>B: POST /api/translate { term, language }
    B->>B: Validate & authenticate
    B->>G: Request translation/explanation
    G-->>B: AI response
    B->>F: Return translation/explanation
    F->>U: Display result
```

### 5.3. Error Handling
- Input validation on both frontend and backend
- Graceful error messages for failed AI requests or invalid input
- Logging and monitoring for backend/API errors

### 5.4. Extensibility
- The architecture allows for easy addition of features such as user accounts, image generation, and history/bookmarks in future milestones.

---

### 5.5. Backend Implementation

- **Framework:** Python with FastAPI for REST API endpoints.
- **Structure:**
  - Modular route handlers (e.g., `/api/translate`)
  - Middleware for input validation, authentication (if enabled), and error handling
  - SQLAlchemy ORM for database access (user data, logs, etc.)
- **API Endpoint Example:**
  - `POST /api/translate` — Receives `{ term, language }`, validates input, calls Gemini API, returns translation/explanation.
- **Error Handling:**
  - Centralized error handling for consistent API responses
  - Logging of errors and failed requests for monitoring

---

### 5.6. Gemini API Integration

- **Library:** Gemini API is accessed via official REST client or HTTP requests (e.g., using `httpx` or `requests`).
- **Authentication:** API key is securely stored in environment variables and injected at runtime.
- **Request Flow:**
  1. Backend constructs a prompt or payload for Gemini API based on user input.
  2. Sends request to Gemini API endpoint (e.g., `/v1/generate-translation`).
  3. Handles API response, including parsing, formatting, and error checking.
  4. If Gemini API returns an error or inappropriate content, backend returns a user-friendly error message.
- **Rate Limiting & Quotas:**
  - Backend monitors API usage and gracefully handles quota limits (e.g., by returning informative errors or fallback responses).
- **Security:**
  - API keys and secrets are never exposed to the frontend or client.

---

### 5.7. Deployment & Operations

- **Frontend Deployment:**
  - Deployed to Firebase Hosting for global CDN, automatic builds, and preview deployments.
  - Configured with automatic SSL/TLS certificates via Firebase.
  - Set up for single-page application routing.

- **Backend Deployment:**
  - Deployed to Cloud Run (Fargate) for managed Python hosting and auto-scaling.
  - Dockerized for consistency across environments.
  - Configured with automatic SSL/TLS certificates via Cloud Run.

- **Infrastructure Setup:**
  - GCP project configured with appropriate services
  - Primary region selected for optimal performance
  - Service account configured with appropriate permissions for deployments
  - Cloud Storage bucket configured for static assets
  - Secret Manager configured for secure API key storage
  - Cloud Monitoring enabled for logging and metrics
  - Cloud Build enabled for container builds and deployments

- **CI/CD:**
  - **CI (Continuous Integration):** GitHub Actions configured for automated testing and building
    - Frontend: Node.js build and dependency installation
    - Backend: Python/Poetry dependency installation, linting, and health checks
    - Runs on push to master and pull requests
  - **CD (Continuous Deployment):** Manual deployment with automation scripts
    - Full stack deployment: `./deploy.sh` (deploys both frontend and backend)
    - Individual deployments: `./deploy-backend.sh` and `./deploy-frontend.sh`
    - Scripts include dependency checks, building, deployment, and health testing
    - Avoids Cloud Build quota usage by using local builds
  - Environment variables and secrets managed via GCP Secret Manager

- **Environment Variables & Secrets:**
  - Managed via GCP Secret Manager for API keys, database credentials, JWT secrets, etc.
  - Service account has appropriate access to secrets for runtime access.

- **Monitoring & Logging:**
  - Cloud Monitoring for logs and metrics
  - Error reporting configured for production monitoring
  - Health check endpoints available at /health

---

### 5.8. Domain Setup

- **Custom Domain Configuration:**
  - **Primary Domain:** vocabloom.app (registered via Namecheap)
  - **DNS Management:** Namecheap Advanced DNS with CNAME records
  - **Frontend:** vocabloom.app → Firebase Hosting ([PROJECT-ID].web.app)
- **API Subdomain:** api.vocabloom.app → Cloud Run ([SERVICE-NAME]-[REGION].a.run.app)
  - **WWW Redirect:** www.vocabloom.app → vocabloom.app

- **SSL/TLS Certificates:**
  - Firebase Hosting: Automatic SSL/TLS certificate provisioning (pending DNS verification)
  - Cloud Run: Automatic SSL/TLS certificates via Google-managed certificates
  - HTTPS enforced everywhere with automatic redirects

- **Domain Verification:**
  - Firebase domain verification in progress (DNS propagation)
  - Verification records added: A record ([FIREBASE-IP]) and TXT record (hosting-site=[PROJECT-ID])
  - Expected completion: 15 minutes to 24 hours for new domain propagation

- **Security:**
  - HTTPS enforced everywhere (automatic with Cloud Run and Firebase)
  - CORS configured appropriately for frontend-backend communication
  - Service account permissions follow principle of least privilege
  - Domain ownership verified through DNS records
  - **Security Note:** Project-specific identifiers (GCP project ID, service names, IPs) have been genericized in public documentation to prevent resource enumeration and maintain security best practices 