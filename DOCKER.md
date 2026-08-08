# BMK School App — Docker

## Quick start

```bash
cd BMK-SCHOOL-APP
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

docker compose up --build
```

Then open:

- Platform picker: http://localhost:8080/
- Balamukundam: http://balamukundam.localhost:8080/
- Balavikas: http://balavikas.localhost:8080/
- Django admin (via UI proxy): http://localhost:8080/admin/
  - If you mapped `WEB_PORT=80`: http://localhost/admin/
- API direct (optional): http://127.0.0.1:8000/api/public/schools/

If admin returns **400 Bad Request**, Django rejected the `Host` header. In `.env` set:

```env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.localhost,api,web,<YOUR-VM-PUBLIC-IP>
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://<YOUR-VM-PUBLIC-IP>,http://localhost:8080
```

Then recreate API: `docker compose up -d --build api`

Demo admins: `bmk_admin` / `bv_admin` — password `Demo@12345`

## Services

| Service | Role |
|---------|------|
| `db` | Postgres 16 |
| `api` | Django + Gunicorn + WhiteNoise |
| `web` | Nginx (React build) + `/api` reverse proxy |

## Notes

- Frontend calls same-origin `/api` (no CORS needed in the browser for school subdomains).
- Set `VITE_APP_DOMAIN` when deploying under a real domain (e.g. `schools.example.com`).
- For production, set a strong `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=false`.
