from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from datetime import date

class User(AbstractUser):
    STATUS_CHOICES = [
        ('unverified', 'UNVERIFIED'),
        ('active', 'ACTIVE'),
        ('suspended', 'SUSPENDED'),
    ]
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, unique=True, null = True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bvn = models.CharField(max_length=11, unique=True, blank=True, null= True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unverified')
    address = models.TextField(blank=True)
    transaction_pin = models.CharField(max_length=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
    def is_adult(self):
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year
            return age >= 18
        return False