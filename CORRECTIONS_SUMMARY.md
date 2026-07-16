# Instructor Feedback Corrections

| Instructor request | Corrected location |
|---|---|
| Restore intact project folders | `app/`, `app/blueprints/`, `tests/`, `.github/workflows/` |
| Add working `ProductionConfig` using `os.getenv()` | `config.py` |
| Add Gunicorn and PostgreSQL driver | `requirements.txt` |
| Remove `python-dotenv` | Not present in `requirements.txt` |
| Ignore `.env` and keep secrets out of Git | `.gitignore` and `.env.example` |
| Use `create_app(ProductionConfig)` without `app.run()` | `flask_app.py` |
| Add build, test, and deploy jobs | `.github/workflows/main.yaml` |
| Make deploy depend on tests | `deploy` contains `needs: test` |
| Use Render GitHub secrets | Workflow reads `RENDER_SERVICE_ID` and `RENDER_API_KEY` |
| Correct Render service configuration | `render.yaml` |
| Use Render hostname without `https://` in Swagger | `config.py` and `app/swagger.py` |
| Use HTTPS Swagger scheme | `ProductionConfig.SWAGGER_SCHEMES = ["https"]` inherited from `Config` |
| Provide deployment instructions | `DEPLOYMENT_CHECKLIST.md` |

The only steps that cannot be completed inside the source archive are account-level actions: pushing to the user's GitHub repository, creating the Render service, adding private repository secrets, and submitting the final live URLs.
