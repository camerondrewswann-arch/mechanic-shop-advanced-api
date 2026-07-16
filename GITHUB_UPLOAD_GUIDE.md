# Upload the Project Without Breaking Its Structure

## GitHub Desktop

1. Extract `Mechanic_Shop_Advanced_API_GitHub_Ready.zip`.
2. Open GitHub Desktop.
3. Select **File → Add local repository**.
4. Choose the extracted `mechanic-shop-advanced-api` folder.
5. Create the repository when prompted.
6. Name it `mechanic-shop-advanced-api`.
7. Commit all files.
8. Select **Publish repository**.
9. Open the repository in your browser and verify that `app/`, `tests/`, and `postman/` are still folders.

## PowerShell

```powershell
git init
git add .
git status
git commit -m "Complete advanced mechanic shop API"
git branch -M main
git remote add origin https://github.com/camerondrewswann-arch/mechanic-shop-advanced-api.git
git push -u origin main
```

Do not create or paste `flask_app.py`, `render.yaml`, `config.py`, workflow files, or tests manually in GitHub. Upload the complete repository structure from the extracted folder.
