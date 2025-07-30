# Vocabloom Deployment Guide

## Quick Reference

### Full Deployment (Recommended)
```bash
./deploy.sh
```
Deploys everything: database setup, backend, and frontend.

### Component-Specific Deployments

#### Frontend Only
```bash
./deploy.sh --frontend
# or
./deploy.sh -f
```
Useful for UI changes only.

#### Backend Only
```bash
./deploy.sh --backend
# or
./deploy.sh -b
```
Useful for API changes only.

#### Database Setup Only
```bash
./deploy.sh --database
# or
./deploy.sh -d
```
Safe to run multiple times - only creates if doesn't exist.

#### Frontend + Backend (No Database)
```bash
./deploy.sh -f -b
```
Useful when database is already set up.

### Help
```bash
./deploy.sh --help
```

## What Each Component Does

### Database Setup (`--database`)
- Creates `vocabloom` database in Cloud SQL
- Creates `vocabloom-app` user with secure password
- Sets up SSL connection string
- **Safe**: Won't overwrite existing data

### Backend Deployment (`--backend`)
- Deploys FastAPI app to Cloud Run
- Sets production environment variables
- Connects to production database
- Updates backend URL dynamically

### Frontend Deployment (`--frontend`)
- Builds Vue.js app with production settings
- Gets current backend URL automatically
- Deploys to Firebase Hosting
- Updates custom domain (vocabloom.app)

## Production URLs

After deployment, your app will be available at:
- **Frontend**: https://vocabloom.app
- **Backend**: Dynamically determined (shown in deployment output)
- **API Docs**: `{backend-url}/docs`

## Troubleshooting

### Database Connection Issues
```bash
./deploy.sh --database
```
This will recreate the database connection if needed.

### Backend Not Responding
```bash
./deploy.sh --backend
```
This will redeploy the backend with fresh environment variables.

### Frontend Not Connecting to Backend
```bash
./deploy.sh --frontend
```
This will rebuild the frontend with the current backend URL.

### Complete Reset
```bash
./deploy.sh
```
This will redeploy everything from scratch. 