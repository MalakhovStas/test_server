from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserRegisterAdmin(UserAdmin):
    """Регистрация модели User в админке"""
