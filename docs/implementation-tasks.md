# Vocabloom Implementation Tasks

---

## 🎉 Current Status: MVP Complete ✅ | Milestone 2 In Progress 🚧

**Production URLs:**
- **Frontend**: https://vocabloom.app (custom domain) / https://vocabloom-467020.web.app (Firebase)
- **Backend**: Cloud Run (URL dynamically determined during deployment)
- **Database**: Cloud SQL PostgreSQL (vocabloom-db instance)
- **GitHub**: https://github.com/yc3136/vocabloom

**Key Features Implemented:**
- ✅ AI-powered translation and explanation using Gemini 2.0 Flash
- ✅ Multi-language support (20+ languages with native names)
- ✅ Responsive Vue.js frontend with markdown rendering
- ✅ FastAPI backend with proper error handling
- ✅ Google Cloud Platform infrastructure
- ✅ Custom domain with SSL/TLS
- ✅ Automated deployment scripts
- ✅ Local development environment setup

**New Features in Milestone 2:**
- 🚧 My Words Page (personal word dashboard)
- 🚧 LLM response caching system (cost optimization)
- 🚧 User preferences management

---

## Milestone 2: My Words Dashboard & Content Discovery

### 🎯 **Implementation Priority**
1. **My Words Page** - Personal word dashboard showing user's looked-up words
2. **LLM Caching** - Cost optimization and performance
3. **User Preferences** - Personalization features

### Overview
Implement personal word dashboard (My Words page), LLM response caching for cost optimization, and user preferences management. Focus on personal content organization and performance optimization.

### 1. Deployment & Infrastructure

#### 1.1. Environment Configuration
- [x] Update environment variables for PostgreSQL
- [x] Configure Firebase credentials in production
- [x] Set up database connection strings in Secret Manager
- [x] Update deployment scripts for new dependencies
- [x] Implement complete environment separation strategy
- [x] Configure local development environment
- [x] Set up production environment isolation

#### 1.2. Security Setup
- [x] Configure database security rules
- [x] Set up Firebase Auth in production
- [x] Configure CORS for authenticated requests
- [x] Implement environment-specific secret management
- [x] Secure local development configuration

### 2. Database Setup & Migration

#### 2.1. Cloud SQL (PostgreSQL) Setup
- [ ] Create Cloud SQL PostgreSQL instance (db-f1-micro for free tier)
- [ ] Configure database connection
- [ ] Set up Cloud SQL Proxy for local development
- [ ] Set up database user and permissions

#### 2.2. Database Schema Implementation
- [ ] Create users table with Firebase UID integration and preferences JSONB
- [ ] Create content table for organizing content by original word
- [ ] Create flashcards table with JSONB fields and content_id foreign key
- [ ] Create cached_translations table for LLM response caching
- [ ] Add comprehensive indexes for performance optimization

#### 2.3. Database Migration System
- [ ] Set up Alembic for database migrations
- [ ] Create initial migration script
- [ ] Test migration in development

### 3. Backend Implementation

#### 3.1. Database Integration
- [x] Install and configure SQLAlchemy ORM
- [ ] Create SQLAlchemy models (User, Content, Flashcard)
- [x] Implement database session management
- [x] Add basic error handling

#### 3.2. Firebase Auth Integration
- [x] Install Firebase Admin SDK
- [x] Configure Firebase project credentials
- [x] Implement token verification middleware
- [x] Create authentication decorators for protected endpoints
- [ ] Add password change and reset functionality

#### 3.3. API Endpoints Implementation
- [x] Implement `/api/auth/register` endpoint
- [x] Implement `/api/auth/login` endpoint
- [ ] Implement `/api/auth/change-password` endpoint
- [ ] Implement `/api/auth/reset-password` endpoint
- [ ] Implement `/api/content` (GET, POST, PUT, DELETE)
- [x] Implement `/api/flashcards` (GET, POST, PUT, DELETE)
- [x] Implement `/api/flashcards/preview` endpoint
- [ ] Implement `/api/user/preferences` (GET, PUT)
- [x] Add basic error handling and validation

#### 3.4. My Words API (Priority 1)
- [ ] Create `/api/words/my` endpoint to get user's unique words
- [ ] Implement word aggregation by original_word and target_language
- [ ] Add translation and flashcard counts per word
- [ ] Create `/api/words/{word}` endpoint for word detail view
- [ ] Add search and filtering for user's words

# Discovery API moved to Milestone 3: Public Content Discovery

#### 3.6. LLM Response Caching System
- [ ] Create cached_translations table with prompt hash indexing
- [ ] Implement prompt hashing function (word + language + user preferences)
- [ ] Update translation endpoint to check cache before calling Gemini API
- [ ] Add cache statistics endpoint for monitoring
- [ ] Implement cache invalidation for prompt changes
- [ ] Add cache hit/miss metrics and logging

#### 3.5. Flashcard Service Logic
- [x] Implement flashcard creation with template support
- [x] Add basic flashcard validation
- [x] Implement flashcard search and filtering
- [x] Add flashcard update and deletion logic
- [ ] Link flashcards to content records

### 4. Frontend Implementation

#### 4.1. Firebase Auth Setup
- [x] Install Firebase Auth SDK for Vue.js
- [x] Configure Firebase client credentials
- [x] Set up authentication state management
- [x] Add basic authentication error handling

#### 4.2. State Management (Pinia)
- [x] Install and configure Pinia
- [x] Create Auth store for user authentication
- [ ] Create Content store for word-based content management
- [x] Create Flashcard store for flashcard management
- [x] Create Translation store for current translation state
- [ ] Create User store for preferences management

#### 4.3. Authentication UI Components
- [x] Create login modal/component
- [x] Create registration modal/component
- [ ] Create password change modal/component
- [ ] Create password reset modal/component
- [x] Implement authentication prompt for save actions
- [x] Add user profile dropdown/menu
- [x] Create logout functionality

#### 4.4. User Preferences UI
- [ ] Create user preferences form (child name, age)
- [ ] Implement preferences update functionality
- [ ] Add preferences validation
- [ ] Create preferences display in user profile

#### 4.5. My Words Page (Priority 1)
- [ ] Create `/words/my` page showing user's unique words
- [ ] Display word list with translation and flashcard counts
- [ ] Add word search and filtering functionality
- [ ] Create word detail view showing all content for a word
- [ ] Add navigation to user profile and settings

# Discovery Page moved to Milestone 3: Public Content Discovery

#### 4.7. Flashcard Management UI
- [x] Create flashcard creation modal/form
- [x] Implement flashcard preview functionality
- [x] Add flashcard dashboard/grid view
- [x] Add flashcard edit/delete functionality
- [x] Create basic search interface

#### 4.8. Hybrid User Experience
- [x] Implement anonymous user translation flow
- [x] Add "Create Flashcard" button for all users
- [x] Implement authentication prompts for save actions
- [x] Create seamless transition from anonymous to authenticated
- [x] Add basic value proposition messaging for sign-up

#### 4.9. Caching Performance Indicators
- [ ] Add cache hit/miss indicators in translation responses
- [ ] Display cache statistics in admin/user dashboard
- [ ] Show performance improvements (response time, cost savings)
- [ ] Add cache status indicators in UI

### 5. Integration & Testing

#### 5.1. Frontend-Backend Integration
- [x] Connect frontend authentication to backend
- [x] Implement API calls with authentication headers
- [x] Add basic error handling for API failures
- [x] Test authentication flow end-to-end

#### 5.2. Simple Testing
- [x] Test user registration and login manually
- [x] Test flashcard creation and saving manually
- [x] Test anonymous user translation flow manually
- [x] Test authentication prompts work correctly
- [x] Verify basic responsive design on different screen sizes

### 6. Documentation & Polish

#### 6.1. Basic Documentation
- [ ] Document new API endpoints
- [ ] Update README with new setup instructions
- [ ] Add basic code comments

#### 6.2. UI Polish
- [x] Add basic loading states
- [x] Add success/error notifications
- [x] Ensure responsive design works
- [x] Add basic accessibility features

---

## Milestone 3: Public Content Discovery

### Overview
Implement public content discovery features allowing users to browse, search, and discover content created by other users, with comprehensive privacy controls.

### 1. Backend Implementation

#### 1.1. Discovery API
- [ ] Implement `/api/discover` endpoint for public content feed
- [ ] Implement `/api/discover/search` endpoint for content search
- [ ] Implement `/api/discover/word/{word}` endpoint for word-specific content
- [ ] Add pagination and filtering support
- [ ] Implement content search optimization with full-text search

#### 1.2. Privacy Management API
- [ ] Implement `/api/content/{id}/privacy` endpoint for individual privacy updates
- [ ] Implement `/api/content/bulk-privacy` endpoint for bulk privacy changes
- [ ] Add privacy validation and security checks
- [ ] Implement privacy change logging

#### 1.3. Database Optimizations
- [ ] Add content privacy indexes for performance
- [ ] Implement full-text search indexes
- [ ] Add content statistics tracking
- [ ] Optimize queries for public content discovery

### 2. Frontend Implementation

#### 2.1. Discover Tab
- [ ] Create discover tab in main navigation
- [ ] Implement feed-like interface for public content
- [ ] Add infinite scroll or pagination
- [ ] Create content cards with rich display
- [ ] Add loading states and error handling

#### 2.2. Search & Filter Interface
- [ ] Create search bar for content discovery
- [ ] Implement filter options (language, topic, keywords)
- [ ] Add search result highlighting
- [ ] Create advanced search interface
- [ ] Add search history and suggestions

#### 2.3. Content Privacy Controls
- [ ] Create privacy toggle component
- [ ] Implement bulk privacy management interface
- [ ] Add privacy indicators throughout the UI
- [ ] Create privacy settings page
- [ ] Add privacy change confirmations

#### 2.4. Enhanced Content Discovery
- [ ] Implement related content suggestions
- [ ] Add content statistics display
- [ ] Create alternative translations view
- [ ] Implement content sharing features

### 3. Integration & Testing

#### 3.1. End-to-End Testing
- [ ] Test public content discovery flow
- [ ] Test content privacy controls
- [ ] Test search and filter functionality
- [ ] Test anonymous user access to discovery features

#### 3.2. Performance Testing
- [ ] Test content feed performance
- [ ] Test search performance with large datasets
- [ ] Optimize database queries for discovery

---

## Milestone 4: Image Generation & Visual Content

### Overview
Implement image generation capabilities using DALL-E 3 API and Stable Diffusion API, with comprehensive storage, safety, and quota management.

### 1. Backend Implementation

#### 1.1. Image Generation Service
- [ ] Integrate DALL-E 3 API for primary image generation
- [ ] Integrate Stable Diffusion API as fallback
- [ ] Implement prompt engineering for educational content
- [ ] Add content safety filtering
- [ ] Implement retry logic and error handling

#### 1.2. Image Storage Service
- [ ] Set up Google Cloud Storage for image files
- [ ] Implement image metadata storage in PostgreSQL
- [ ] Add image optimization and compression
- [ ] Implement CDN integration for fast delivery
- [ ] Add image thumbnail generation

#### 1.3. Quota Management
- [ ] Implement user-specific image generation quotas
- [ ] Add quota tracking and usage monitoring
- [ ] Create quota reset mechanisms
- [ ] Implement quota upgrade options

#### 1.4. API Endpoints
- [ ] Implement `/api/images/generate` endpoint
- [ ] Implement `/api/images` endpoint for user's images
- [ ] Implement `/api/images/{id}` DELETE endpoint
- [ ] Implement `/api/images/quota` endpoint
- [ ] Add image generation progress tracking

### 2. Frontend Implementation

#### 2.1. Image Generation UI
- [ ] Create image generation button/interface
- [ ] Implement generation progress indicators
- [ ] Add image generation options and settings
- [ ] Create image preview functionality
- [ ] Add generation error handling and retry

#### 2.2. Image Gallery
- [ ] Create image gallery component
- [ ] Implement image grid/list views
- [ ] Add image search and filter
- [ ] Create image detail view
- [ ] Add image download functionality

#### 2.3. Quota Management UI
- [ ] Create quota display component
- [ ] Implement quota usage indicators
- [ ] Add quota upgrade prompts
- [ ] Create quota history view

### 3. Database Schema

#### 3.1. Images Table
- [ ] Create images table with metadata
- [ ] Add user image quota columns
- [ ] Implement proper indexes for performance
- [ ] Add foreign key relationships

### 4. Integration & Testing

#### 4.1. API Integration Testing
- [ ] Test DALL-E 3 API integration
- [ ] Test Stable Diffusion API fallback
- [ ] Test image storage and retrieval
- [ ] Test quota management system

#### 4.2. Performance Testing
- [ ] Test image generation performance
- [ ] Test image delivery via CDN
- [ ] Optimize image loading and caching

---

## Milestone 5: Advanced Learning Features

### Overview
Implement bedtime story generation, advanced flashcard features, and interactive learning modes.

### 1. Bedtime Story Generation

#### 1.1. Backend Implementation
- [ ] Implement story generation service with Gemini API
- [ ] Create specialized prompts for educational storytelling
- [ ] Add story personalization using user preferences
- [ ] Implement story storage and retrieval
- [ ] Add story sharing capabilities

#### 1.2. Story Generation API
- [ ] Implement `/api/stories/generate` endpoint
- [ ] Implement `/api/stories` endpoint for user's stories
- [ ] Implement `/api/stories/{id}` PUT/DELETE endpoints
- [ ] Add story customization options

#### 1.3. Frontend Implementation
- [ ] Create story generation interface
- [ ] Implement story customization controls
- [ ] Add story display and reading interface
- [ ] Create story sharing features
- [ ] Add story library management

### 2. Flashcard Enhancements

#### 2.1. Advanced Organization
- [ ] Implement hashtag system for flashcards
- [ ] Add bulk operations for flashcard management
- [ ] Create advanced search with hashtag filtering
- [ ] Implement AI-powered tag suggestions

#### 2.2. Export & Printing
- [ ] Implement PDF generation for flashcards
- [ ] Add CSV export functionality
- [ ] Create professional printing templates
- [ ] Implement batch export capabilities

#### 2.3. Interactive Learning Modes
- [ ] Create slideshow mode for studying
- [ ] Implement quiz mode with multiple choice questions
- [ ] Add progress tracking and statistics
- [ ] Implement spaced repetition algorithm

### 3. API Endpoints

#### 3.1. Story Generation
- [ ] Implement story generation endpoints
- [ ] Add story management endpoints
- [ ] Implement story sharing endpoints

#### 3.2. Flashcard Enhancements
- [ ] Implement bulk tag operations
- [ ] Add export endpoints
- [ ] Create quiz generation endpoints
- [ ] Implement progress tracking endpoints

### 4. Frontend Implementation

#### 4.1. Story Features
- [ ] Create story generation UI
- [ ] Implement story customization interface
- [ ] Add story library and management
- [ ] Create story sharing interface

#### 4.2. Enhanced Flashcard UI
- [ ] Create hashtag management interface
- [ ] Implement bulk operations UI
- [ ] Add export and printing interface
- [ ] Create interactive learning modes UI

---

## Milestone 6: Community Features & Advanced Platform

### Overview
Implement community features, premium functionality, and advanced platform capabilities.

### 1. Community Features

#### 1.1. Community Forums
- [ ] Implement discussion board system
- [ ] Create user profile enhancements
- [ ] Add content sharing capabilities
- [ ] Implement moderation tools

#### 1.2. Gamification System
- [ ] Create achievement system
- [ ] Implement progress tracking
- [ ] Add leaderboards
- [ ] Create points system

### 2. Premium Features

#### 2.1. Subscription Management
- [ ] Implement tiered subscription plans
- [ ] Add feature gating system
- [ ] Integrate payment processing
- [ ] Create usage analytics

#### 2.2. Advanced Content Generation
- [ ] Implement audio generation
- [ ] Add video clip generation
- [ ] Create custom prompt system
- [ ] Implement multi-language UI

### 3. Administrative Features

#### 3.1. Analytics Dashboard
- [ ] Create user analytics dashboard
- [ ] Implement content analytics
- [ ] Add system health monitoring
- [ ] Create business metrics tracking

#### 3.2. Content Moderation
- [ ] Implement automated content filtering
- [ ] Create manual review queue
- [ ] Add user reporting system
- [ ] Implement policy enforcement

### 4. Technical Implementation

#### 4.1. Scalability Enhancements
- [ ] Implement microservices architecture
- [ ] Add Redis caching layer
- [ ] Optimize CDN configuration
- [ ] Implement database sharding

#### 4.2. Security Enhancements
- [ ] Add multi-factor authentication
- [ ] Implement rate limiting
- [ ] Enhance content security
- [ ] Improve privacy controls

---

## Implementation Checklist (MVP Scope)

### 1. Development Environment & Repository
1. [x] Set up monorepo (client + server) for project structure
2. [x] Configure GitHub repository with branch protection and code review rules
3. [x] Add .gitignore, README, and contribution guidelines
4. [x] Set up Prettier and ESLint for code formatting and linting (frontend); Black and flake8 for backend
5. [x] Configure basic testing frameworks (Jest, Vue Testing Library for frontend; Pytest for backend)

### 2. GCP & Cloud Setup
1. [x] Register GCP account and configure IAM users/roles
2. [x] Set up Google Cloud DNS for domain management
3. [x] Set up Google Cloud Storage (GCS) and Cloud CDN for static asset hosting (frontend)
4. [x] Set up Cloud Run for backend container hosting
5. [x] Set up Secret Manager for API keys and JWT secrets
6. [x] Set up Cloud Monitoring and Error Reporting for logging and monitoring
7. [x] Set up Google-managed SSL/TLS certificates

### 3. CI/CD Pipeline
1. [x] Configure GitHub Actions for automated build, test, and deploy
2. [x] Set up environment variables and secrets in CI/CD

### 4. Frontend Implementation
1. [x] Scaffold Vue.js app with TypeScript and Vuetify
2. [x] Implement project branding and remove default Vite/Vue content
3. [x] Set up routing and basic page structure
4. [x] Implement language selection and term input UI
5. [x] Implement form validation and error handling
6. [x] Integrate API calls to backend for translation/explanation
7. [x] Display translation/explanation results
8. [x] Add loading and error states

### 5. Backend Implementation
1. [x] Scaffold Python FastAPI app
2. [x] Set up Poetry for dependency management
3. [x] Implement `/api/translate` endpoint
4. [x] Integrate Gemini API for translation/explanation
5. [x] Add input validation and error handling middleware
6. [x] Add logging (Cloud Monitoring integration)

### 6. Frontend-Backend Integration
1. [x] Scaffold /api/translate endpoint in backend
2. [x] Connect frontend to backend /api/translate endpoint
3. [x] Display response in frontend UI
4. [x] Implement markdown rendering for explanations
5. [x] Add language selection dropdown with native language names
6. [x] Configure CORS for production domains

### 7. Deployment & Domain
1. [x] Deploy frontend to Firebase Hosting or GCS + Cloud CDN
2. [x] Deploy backend to Cloud Run
3. [x] Configure custom domains via Namecheap DNS (vocabloom.app, api.vocabloom.app)
4. [x] Set up SSL/TLS certificates via Google-managed certificates
5. [x] Test HTTPS and domain routing
6. [x] Complete Firebase domain verification (DNS propagation completed)

**Note:** Custom domain vocabloom.app is fully configured and working. Both Firebase Hosting and custom domain are operational.

### 8. Security & Configuration
1. [x] Set up environment-based API key management (local .env, production Secret Manager)
2. [x] Configure CORS policy for allowed domains
3. [x] Implement proper error handling and validation
4. [x] Secure API key storage and access
5. [x] Update documentation to reflect GCP technology stack

### 9. Public Launch Preparation
1. [x] Monitor logs and metrics in Cloud Monitoring
2. [ ] Ensure privacy policy and terms of service are available
3. [x] Open public access to the product

---

## Nice-to-Have Features

### Authentication & User Management
- [x] Implement user authentication system (Firebase Auth)
- [x] Add user registration and login functionality
- [ ] Implement user profiles and preferences
- [ ] Add role-based access control

### Testing & Quality Assurance
- [ ] Add comprehensive unit tests for frontend components
- [ ] Add integration tests for API endpoints
- [ ] Add end-to-end tests for user flows
- [ ] Implement automated testing in CI/CD pipeline
- [ ] Add performance testing and monitoring

### UI/UX Polish
- [ ] Add dark mode theme
- [ ] Implement advanced animations and transitions
- [ ] Add keyboard shortcuts and accessibility features
- [ ] Optimize mobile responsiveness
- [ ] Add progressive web app (PWA) features

---

## Future Enhancements

- [x] Add translation history and favorites
- [ ] Implement audio pronunciation features
- [ ] Add image generation for vocabulary learning
- [ ] Create mobile app version
- [ ] Add offline functionality
- [ ] Implement social features (sharing, community)
- [ ] Add gamification elements (points, badges, streaks)
- [ ] Create teacher/student dashboard for educational use

---

## Milestone 3: Public Content Discovery (Future)

### Overview
Implement public content discovery features allowing users to browse, search, and discover content created by other users.

### Key Features:
- **Discovery Page** - Public flashcard browsing and search
- **Content Sharing** - Public translation and flashcard discovery
- **Community Features** - User-generated content discovery
- **Search & Filtering** - Advanced content discovery tools

### Implementation Tasks:
- [ ] Create `/api/flashcards/discover` endpoint for public flashcard browsing
- [ ] Create `/api/translations/discover` endpoint for public translation browsing
- [ ] Implement `/discover` page with flashcard grid/list view
- [ ] Add search and filter functionality for discovery
- [ ] Create content aggregation and sorting features
- [ ] Add "Save to My Words" functionality for discovered content
