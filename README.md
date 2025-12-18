# Library API
**Online Library Management System**  
Modern REST API built with **Django REST Framework**, featuring JWT authentication, book inventory management, borrowing tracking, Stripe payments, Telegram notifications, and interactive documentation.  

[![Django](https://img.shields.io/badge/Django-5.2.9%2B-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16%2B-A30000?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![DRF Spectacular](https://img.shields.io/badge/DRF_Spectacular-0.29-6C4AB6?style=for-the-badge&logo=swagger&logoColor=white)](https://drf-spectacular.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Celery](https://img.shields.io/badge/Celery-5.6.0-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/en/stable/)
[![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Stripe](https://img.shields.io/badge/Stripe-008CDD?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

## Features  
- User registration & authentication via **JWT**  
- Manage books inventory (CRUD operations with quantity tracking)  
- Borrow and return books with automatic inventory updates  
- View and filter borrowings by user and active status  
- Handle payments for borrowings via **Stripe**  
- Send notifications to administrators via **Telegram** (e.g., new borrowings, overdue, successful payments)  
- Full OpenAPI documentation (Swagger + ReDoc)

---  
### Authentication (JWT)  
| Endpoint | Method | Description |  
|---------------------|----------|------------------------------------------|  
| `/users/` | POST | Register a new user |  
| `/users/token/` | POST | Obtain access & refresh tokens |  
| `/users/token/refresh/` | POST | Refresh access token |  
| `/users/me/` | GET/PUT/PATCH | View and update current user profile |  

### Main API Endpoints  
| Endpoint | Methods | Description |  
|----------------------|--------------------------|--------------------------------------------------|  
| `/api/books/` | GET, POST | Books (list, add new) |  
| `/api/books/<id>/` | GET, PUT/PATCH, DELETE | Book details (view, update inventory, delete) |  
| `/api/borrowings/` | GET, POST | Borrowings (list with filters: ?user_id=...&is_active=..., add new — decreases inventory) |  
| `/api/borrowings/<id>/` | GET | Get specific borrowing details |  
| `/api/borrowings/<id>/return/` | POST | Return book — sets return date and increases inventory |  
| `/api/payments/` | GET | Check own payments |  
| `/api/payments/success/` | GET | Check successful Stripe payment |  
| `/api/payments/cancel/` | GET | Return payment paused message |

> Protected endpoints require header:  
> `Authorization: Bearer <access_token>`  

---  
## Quick Start  

### Create .env file (or copy from .env_sample):
```bash  
SECRET_KEY=secret_key_here
DEBUG=True
STRIPE_PUBLIC=public_key_here
STRIPE_SECRET_KEY=secret_key_here
STRIPE_SUCCESS_URL=http://127.0.0.1:8000/api/payments/success
STRIPE_CANCEL_URL=http://127.0.0.1:8000/api/payments/cancel
TELEGRAM_BOT_TOKEN=tg_token_here
ADMIN_TELEGRAM_CHAT_ID=chat_id_here
CELERY_BROKER_URL=redis://localhost
CELERY_BACKEND_URL=redis://localhost
POSTGRES_DB=POSTGRES_DB
POSTGRES_USER=POSTGRES_USER
POSTGRES_PASSWORD=POSTGRES_PASSWORD
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Docker  
```bash  
git clone https://github.com/bashyrov/library-api.git  
cd library-api  
docker-compose up --build  

# If needed, exec into container to apply migrations and load data
docker exec -it library-api-servise-web-1 sh
python manage.py loaddata library_fixture.json

echo "API is running at http://127.0.0.1:8000"
```

### Registration example:

```bash  
POST /users/  
{  
  "email": "user@example.com",  
  "password": "strongpassword123"  
}  
```
## 📚 API Documentation
Interactive documentation available after server start:

Swagger UI: http://127.0.0.1:8001/api/schema/swagger-ui/

ReDoc: http://127.0.0.1:8001/api/schema/redoc/

OpenAPI Schema: http://127.0.0.1:8001/api/schema/
