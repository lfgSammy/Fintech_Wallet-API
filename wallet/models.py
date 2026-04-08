from django.db import models
from users.models import User
import uuid

class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ('NGN', 'NIGERIAN NAIRA'),
        ('USD', 'US DOLLAR'),
        ('GDP', 'BRITISH POUNDS')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='NGN')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} : {self.currency} {self.balance}"
    
class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('deposit', 'DEPOSIT'),
        ('withdrawal', 'WITHDRAWAL'),
        ('transfer_in', 'TRANSFER_IN'),
        ('transfer_out', 'TRANSFER_OUT')
    ]
    STATUS_CHOICE = [
        ('pending', 'PENDING'),
        ('successful', 'SUCCESSFUL'),
        ('failed', 'FAILED')
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transaction')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default= 'pending')
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    description = models.TextField(blank=True)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_tYPE}: {self.amount} ({self.status})"
    
class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'PENDING'),
        ('successful', 'SUCCESSFUL'),
        ('failed', 'FAILED')
    ]
    sender_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sent_transfer')
    receiver_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, 
                                        related_name='recieved_transfers')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer {self.amount} from {self.sender_wallet.user.username} to {self.reciever_wallet.user.username}"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
