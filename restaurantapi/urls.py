from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # ---- Djoser default endpoints ----
    path("auth/", include("djoser.urls")),  
    # /auth/users/                   (POST - register a new user)
    # /auth/users/me/                (GET/PUT/PATCH/DELETE - get/update/delete current user)
    # /auth/users/activation/        (POST - activate account, if enabled)
    # /auth/users/resend_activation/ (POST - resend activation email, if enabled)
    # /auth/users/set_password/      (POST - change password)
    # /auth/users/reset_password/        (POST - request password reset)
    # /auth/users/reset_password_confirm/ (POST - confirm password reset)
    # /auth/users/set_username/          (POST - change username/email)
    # /auth/users/reset_username/        (POST - request username/email reset)
    # /auth/users/reset_username_confirm/ (POST - confirm username/email reset)

    # ---- JWT endpoints ----
    path("auth/", include("djoser.urls.jwt")),  
    # /auth/jwt/create/   (POST - obtain access + refresh tokens)
    # /auth/jwt/refresh/  (POST - refresh the access token using refresh)
    # /auth/jwt/verify/   (POST - verify if access token is valid)
    path('', include(router.urls)),
]
