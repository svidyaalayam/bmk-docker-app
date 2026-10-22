# bmk-docker-app

## Word Garden vocabulary module

The vocabulary learning module is implemented directly in the existing Django/DRF application at `bmk-api/vocabulary`, with its React entry point at `/vocabulary`. It reuses the existing JWT authentication, `ADMIN`/`TEACHER`/`STUDENT` permissions, PostgreSQL database, and Docker deployment.

After the normal application deployment, run `python manage.py migrate` and `python manage.py seed_vocabulary` inside the API container to create the schema and sample words. The Word Garden APIs are rooted at `/api/vocabulary/`; signed-in students can browse active vocabulary and their own assessment attempts, while teachers and administrators manage content and assessment endpoints.
