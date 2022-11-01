from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class AccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password, **other_fields):
        if not email:
            raise ValueError("Users must have email address")
        if not username:
            raise ValueError("Users must have username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **other_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password, **other_fields):
        
        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_active',True)
        other_fields.setdefault('is_superuser',True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.'
            )
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.'
            )
        return self.create_user(email, username, first_name, last_name, password, **other_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=30)
    about_me = models.CharField(max_length=200)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']

    objects = AccountManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    


