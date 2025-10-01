# 🍋 Little Lemon – Restaurant App

This project is a **Django web application** with two main parts:  

1. **Frontend (Web pages)** – Customers can browse menus, learn about the restaurant, and make bookings through forms.  
2. **Backend API (Django REST Framework)** – Provides authentication, menus, and reservations via JSON endpoints.

It also includes **JWT authentication**, Docker support, and can be deployed on **Google Cloud**.

---

## 🌐 Frontend (Web Views)

| URL                | Description                                |
|--------------------|--------------------------------------------|
| `/`                | Homepage                                   |
| `/about/`          | About page                                 |
| `/menu/`           | List all menu items                        |
| `/menu/<id>/`      | Display a single menu item                 |
| `/reservations/`   | Show user’s reservations (login required)  |
| `/book/`           | Make a new booking via form (login required) |

---

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/users/` – Register  
- `POST /api/auth/jwt/create/` – Login (get tokens)  
- `POST /api/auth/jwt/refresh/` – Refresh token  
- `POST /api/auth/jwt/verify/` – Verify token  
- `GET /api/auth/users/me/` – Current user  

### Menus
- `GET /api/menus/` – List menus (public)  
- `GET /api/menus/<id>/` – Retrieve one menu  
- `POST /api/menus/` – Create (admin only)  
- `PUT /api/menus/<id>/` – Update (admin only)  
- `DELETE /api/menus/<id>/` – Delete (admin only)  

### Bookings
- `GET /api/bookings/` – List user’s bookings (admin sees all)  
- `POST /api/bookings/` – Create/Update booking  
- `GET /api/bookings/<id>/` – Retrieve booking  
- `PUT /api/bookings/<id>/` – Update booking  
- `DELETE /api/bookings/<id>/` – Cancel booking  

**Booking Example:**
```http
POST /api/bookings/
Authorization: Bearer <token>
Content-Type: application/json
```
```json
{
  "first_name": "Alice",
  "reservation_date": "2025-09-10",
  "reservation_slot": 2
}
```

## 🐳 Run with Docker

1. Clone repo:

   ```bash
   git clone https://github.com/VoranReygetov/Little-Lemon-Web-Application.git
   cd Little-Lemon-Web-Application
   ```

2. Create `.env.prod`:

   ```env
   DJANGO_SECRET_KEY=your_secret
   DJANGO_DEBUG=Fasle
   DJANGO_ALLOWED_HOSTS=*
   DJANGO_CSRF_TRUSTED_ORIGINS=*

   # Database settings (shared by MySQL + Django)
   DATABASE_ENGINE=mysql
   MYSQL_DATABASE=reservations
   MYSQL_USER=user
   MYSQL_PASSWORD=mypassword
   MYSQL_ROOT_PASSWORD=mypassword
   MYSQL_HOST=db
   MYSQL_PORT=3306
   ```

3. Start services:

   ```bash
   docker-compose up --build
   ```

4. Access:

   * Web app: [http://localhost:8000/](http://localhost:8000/)
   * API: [http://localhost:8000/api/](http://localhost:8000/api/)

---
