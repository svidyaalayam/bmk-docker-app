# BMK School App — Setup on another computer

## What’s in this zip
- `bmk-api` — Django REST API
- `bmk-ui` — React (Vite) frontend
- `docker-compose.yml` — Postgres + API + Nginx UI
- `.env.example` — environment template
- `DOCKER.md` — Docker notes

**Not included:** `venv`, `node_modules`, local `.env`, SQLite DB, Docker volumes (install/build on the new machine).

---

## Option A — Docker (recommended)

### Requirements
- Docker Desktop installed and **running**

### Steps (Windows PowerShell)
```powershell
# 1) Unzip, then open the project folder
cd path\to\BMK-SCHOOL-APP

# 2) Create env file
copy .env.example .env

# 3) Build and start
docker compose up --build -d
```

### Open in browser
| Page | URL |
|------|-----|
| School picker | http://localhost:8080/ |
| Balamukundam (Telugu) | http://balamukundam.localhost:8080/ |
| Balavikas (Kannada) | http://balavikas.localhost:8080/ |
| Django admin | http://localhost:8080/admin/ |

### Demo login
- Username: `bmk_admin` or `bv_admin`
- Password: `Demo@12345`

### Useful commands
```powershell
docker compose ps          # status
docker compose logs -f     # logs
docker compose down        # stop
docker compose down -v     # stop and delete DB volume
```

---

## Option B — Local without Docker

### Requirements
- Python 3.12+
- Node.js 20+

### API
```powershell
cd bmk-api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_schools
python manage.py runserver 8000
```

### UI (new terminal)
```powershell
cd bmk-ui
copy .env.example .env
npm install
npm run dev
```

Open:
- Picker: http://localhost:5173/
- Schools: http://balamukundam.localhost:5173/ and http://balavikas.localhost:5173/

Local mode uses **SQLite**. Docker mode uses **Postgres**.

---

## Notes
- Prefer **one** mode at a time (Docker **or** local), not both on the same ports.
- Change `DJANGO_SECRET_KEY` in `.env` before any real deployment.
- School sites use subdomains like `balavikas.localhost` (browsers resolve these to your PC).
