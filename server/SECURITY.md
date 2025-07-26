# Security Guidelines

## API Key Management

### ⚠️ CRITICAL: Never commit API keys to version control

1. **Environment Variables**: Always use environment variables for API keys
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```

2. **Local Testing**: Use the template file `test_local_template.py` and copy it to `test_local.py`
   - The `test_local.py` file is gitignored to prevent accidental commits
   - Always check that your API key is not hardcoded before committing

3. **Production**: Use Google Cloud Secret Manager
   - The application automatically uses Secret Manager when `GOOGLE_CLOUD_PROJECT` is set
   - Store your API key in Secret Manager for production deployments

## CORS Configuration

### Current Configuration
The API is configured to allow requests from:
- `http://localhost:5173` - Vite development server
- `http://localhost:3000` - Alternative development port
- `https://vocabloom-467020.web.app` - Firebase Hosting
- `https://vocabloom-467020.firebaseapp.com` - Firebase Hosting alternative

### Development
- Local development servers are allowed for testing
- This enables frontend development without CORS issues

### Production
- Only Firebase Hosting domains are allowed
- This prevents unauthorized cross-origin requests
- If you deploy to a custom domain, add it to the `allow_origins` list

## Input Validation

- All user inputs are validated and sanitized
- Empty terms and languages are rejected
- Input is stripped of leading/trailing whitespace

## Error Handling

- API errors are logged but don't expose sensitive information
- Generic error messages are returned to clients
- Detailed error information is only logged server-side

## Best Practices

1. **Regular Security Audits**: Regularly review the code for security issues
2. **Dependency Updates**: Keep all dependencies updated
3. **Environment Separation**: Use different API keys for development and production
4. **Monitoring**: Monitor API usage for unusual patterns
5. **Rate Limiting**: Consider implementing rate limiting for production use 