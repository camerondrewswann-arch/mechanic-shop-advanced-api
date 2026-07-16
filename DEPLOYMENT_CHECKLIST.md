# GitHub and Render Deployment Checklist

## 1. Push the intact folder with Git

Do not upload the files one at a time through the GitHub website. Extract the ZIP, open PowerShell inside the `mechanic-shop-advanced-api` folder, and run:

```powershell
git init
git add .
git commit -m "Fix project structure and Render deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL.git
git push -u origin main
```

For an existing repository that already has the broken upload, clone it first or replace its contents locally while preserving the `.git` folder, then run:

```powershell
git add -A
git commit -m "Restore Flask project structure and CI/CD"
git push origin main
```

Confirm GitHub displays these paths exactly:

```text
app/
app/blueprints/customers/
app/blueprints/mechanics/
app/blueprints/service_tickets/
app/blueprints/inventory/
tests/
.github/workflows/main.yaml
flask_app.py
render.yaml
```

## 2. Create the Render service

The included `render.yaml` can create a Flask web service and PostgreSQL database as a Render Blueprint.

1. In Render, create a new Blueprint from the corrected GitHub repository.
2. Confirm the build command is `pip install -r requirements.txt`.
3. Confirm the pre-deploy command is `flask --app flask_app.py init-db`.
4. Confirm the start command is `gunicorn flask_app:app`.
5. Keep Render automatic deploys disabled because GitHub Actions handles deployment.
6. After creation, copy the service ID. It begins with `srv-` and is visible in the service URL/settings.
7. Create a Render API key in Render Account Settings. Do not put it in the repository.

## 3. Add GitHub repository secrets

In GitHub, open **Settings → Secrets and variables → Actions → New repository secret** and add:

- `RENDER_SERVICE_ID`: the Render service ID beginning with `srv-`
- `RENDER_API_KEY`: the private Render API key

The deploy job in `.github/workflows/main.yaml` runs only after the test job succeeds because it contains `needs: test`.

## 4. Verify the deployment

After the GitHub Actions workflow succeeds, open:

```text
https://YOUR-RENDER-HOSTNAME.onrender.com/health
https://YOUR-RENDER-HOSTNAME.onrender.com/docs
https://YOUR-RENDER-HOSTNAME.onrender.com/swagger.json
```

The health route should return:

```json
{"status":"healthy"}
```

Render automatically provides `RENDER_EXTERNAL_HOSTNAME`. The application uses that hostname in Swagger without `https://`, and Swagger's scheme is set to `https`.

## 5. Submit

Submit both:

- Corrected GitHub repository URL
- Working Render deployment URL

Upload the under-five-minute presentation directly to Disco.
