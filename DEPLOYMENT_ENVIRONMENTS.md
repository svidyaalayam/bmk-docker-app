# Environment deployments

The project uses one Django settings module. Each deployment supplies its own
environment file, which defines the app domain and the matching host, CSRF, and
CORS restrictions.

1. Copy the appropriate committed template to its ignored deployment file:

   `Copy-Item .env.test.example .env.test`

2. Replace every secret and database placeholder in that file.

3. Start that deployment with its environment file:

   `docker compose --env-file .env.test up --build -d`

Use `.env.staging` or `.env.production` in the same way. `APP_DOMAIN` and
`VITE_APP_DOMAIN` must remain identical because the API resolves school hosts
and the frontend generates those hosts.

Each environment file permits its apex domain and all one-label school
subdomains. For example, the test environment accepts
`uk-telugu.test.balamukundam.com`.
