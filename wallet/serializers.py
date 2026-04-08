from rest_framework import serializers
from .models import Wallet, Transaction, Transfer, Notification
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'date_of_birth', 'bvn',
                  'status','address', 'created_at']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id','user', 'balance', 'currency', 'is_active','created_at']
        read_only_fields = ['balance', 'user']
    
class TransactionSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only= True)
    class Meta:
        model = Transaction
        fields = ['id','wallet','transaction_type', 'amount', 'status',
                  'transaction_id', 'description','balance_after']
        
class TransferSerializer(serializers.ModelSerializer):
    sender_wallet = WalletSerializer(read_only= True)
    receiver_wallet = WalletSerializer(read_only= True)
    class Meta:
        model = Transfer
        fields = ['id','amount','sender_wallet','receiver_wallet',
                    'status', 'transaction_id', 'description','created_at']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']