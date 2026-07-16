# Mechanic Shop Advanced API

A Flask REST API for managing mechanic-shop customers, mechanics, service tickets, and inventory parts. This project completes the Advanced API Development assignment requirements, including token authentication, role-protected routes, rate limiting, caching, pagination, advanced SQLAlchemy queries, many-to-many relationships, automated tests, and an exported Postman collection.

## Included assignment features

- Flask application-factory structure with separate blueprints
- Customer JWT login using `python-jose`
- `@token_required` customer authorization wrapper
- Protected `GET /customers/my-tickets`
- Optional mechanic login and role-specific mechanic token wrapper
- Flask-Limiter default limits plus stricter login limits
- Flask-Caching on frequently requested list/query routes
- Paginated customer list using `page` and `per_page`
- Service-ticket mechanic editing with `add_ids` and `remove_ids`
- Mechanic ranking by number of assigned tickets
- Inventory model and full CRUD blueprint
- Many-to-many service-ticket/inventory relationship
- Add-part and remove-part service-ticket routes
- Password hashing with Werkzeug
- Six automated pytest tests
- Postman collection with collection variables and token-saving scripts

## Correct project structure

```text
mechanic-shop-advanced-api/
├── app/
│   ├── blueprints/
│   │   ├── customers/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── inventory/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── mechanics/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   └── service_tickets/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── schemas.py
│   ├── __init__.py
│   ├── auth.py
│   ├── extensions.py
│   └── models.py
├── postman/
│   └── Mechanic_Shop_Advanced_API.postman_collection.json
├── tests/
│   ├── conftest.py
│   └── test_advanced_api.py
├── .env.example
├── .gitignore
├── config.py
├── flask_app.py
├── requirements.txt
├── run.py
├── seed.py
└── SUBMISSION_CHECKLIST.md
```

Do not copy the files one at a time into GitHub's website. Extract the ZIP and push the complete folder with Git or GitHub Desktop so the folders remain intact.

## Run locally on Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py seed.py
py run.py
```

Open:

```text
http://127.0.0.1:5000/health
```

The expected health response is:

```json
{"status":"healthy"}
```

## Seeded demonstration accounts

```text
Customer email: customer@example.com
Customer password: password123

Mechanic email: mechanic@example.com
Mechanic password: wrench123
```

## Run the tests

Stop the Flask server, then run:

```powershell
py -m pytest -q
```

Expected result:

```text
6 passed
```

## Authentication

Customer login:

```http
POST /customers/login
Content-Type: application/json
```

```json
{
  "email": "customer@example.com",
  "password": "password123"
}
```

Use the returned token on protected customer routes:

```text
Authorization: Bearer YOUR_CUSTOMER_TOKEN
```

Mechanic login:

```http
POST /mechanics/login
```

Use the returned mechanic token for inventory changes and service-ticket management.

## Important endpoints

### Customers

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| POST | `/customers/` | None | Create customer |
| POST | `/customers/login` | None | Customer login; rate limited |
| GET | `/customers/?page=1&per_page=5` | None | Paginated customer list; cached |
| GET | `/customers/my-tickets` | Customer token | Get logged-in customer's tickets |
| PUT | `/customers/<id>` | Same customer | Update account |
| DELETE | `/customers/<id>` | Same customer | Delete account |

### Mechanics

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| POST | `/mechanics/` | None | Create mechanic |
| POST | `/mechanics/login` | None | Mechanic login; rate limited |
| GET | `/mechanics/` | None | List mechanics; cached |
| GET | `/mechanics/ranked` | None | Rank mechanics by ticket count |
| PUT | `/mechanics/<id>` | Same mechanic | Update mechanic |
| DELETE | `/mechanics/<id>` | Same mechanic | Delete mechanic |

### Service tickets

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| POST | `/service-tickets/` | Customer token | Create ticket for logged-in customer |
| GET | `/service-tickets/` | None | List/filter tickets; cached |
| GET | `/service-tickets/<id>` | None | Read one ticket |
| PUT | `/service-tickets/<id>` | Mechanic token | Update ticket details |
| PUT | `/service-tickets/<id>/edit` | Mechanic token | Add/remove mechanics |
| PUT | `/service-tickets/<id>/add-part/<part_id>` | Mechanic token | Attach inventory part |
| PUT | `/service-tickets/<id>/remove-part/<part_id>` | Mechanic token | Remove inventory part |
| DELETE | `/service-tickets/<id>` | Mechanic token | Delete ticket |

Mechanic-edit payload:

```json
{
  "add_ids": [1, 2],
  "remove_ids": [3]
}
```

### Inventory

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| POST | `/inventory/` | Mechanic token | Create part |
| GET | `/inventory/` | None | List parts; cached |
| GET | `/inventory/<id>` | None | Read part |
| PUT | `/inventory/<id>` | Mechanic token | Update part |
| DELETE | `/inventory/<id>` | Mechanic token | Delete part |

## Postman

Import:

```text
postman/Mechanic_Shop_Advanced_API.postman_collection.json
```

Run the requests in order. Login requests automatically store customer and mechanic tokens as collection variables.

## Push the complete folder to GitHub

Create an empty GitHub repository named `mechanic-shop-advanced-api`. Do not initialize it with another README or `.gitignore`.

Open PowerShell inside the extracted project folder:

```powershell
git init
git add .
git status
git commit -m "Complete advanced mechanic shop API"
git branch -M main
git remote add origin https://github.com/camerondrewswann-arch/mechanic-shop-advanced-api.git
git push -u origin main
```

Before submitting, verify that GitHub shows `app/`, `app/blueprints/`, `tests/`, and `postman/` as folders.
