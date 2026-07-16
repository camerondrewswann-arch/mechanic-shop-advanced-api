from pathlib import Path


def test_swagger_uses_configured_host_and_scheme(client):
    response = client.get("/swagger.json")
    data = response.get_json()

    assert response.status_code == 200
    assert data["host"] == "localhost"
    assert data["schemes"] == ["http"]
    assert data["securityDefinitions"]["BearerAuth"]["name"] == "Authorization"


def test_expected_deployment_files_and_workflow_dependency():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "main.yaml").read_text()
    requirements = (root / "requirements.txt").read_text().lower()
    gitignore = (root / ".gitignore").read_text().splitlines()
    flask_app = (root / "flask_app.py").read_text()

    assert "needs: test" in workflow
    assert "RENDER_SERVICE_ID" in workflow
    assert "RENDER_API_KEY" in workflow
    assert "gunicorn" in requirements
    assert "psycopg2-binary" in requirements
    assert "python-dotenv" not in requirements
    assert ".env" in gitignore
    assert "create_app(ProductionConfig)" in flask_app
    assert "app.run(" not in flask_app
