from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.db import transaction
from decimal import Decimal
from .models import Wallet, Transaction, Transfer, Notification
from .serializers import (WalletSerializer, TransactionSerializer,
                          TransferSerializer, NotificationSerializer)
from users.models import User


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number')
        transaction_pin = request.data.get('transaction_pin')
        date_of_birth = request.data.get('date_of_birth')

        if not username or not email or not password or not transaction_pin or not phone_number:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(phone_number= phone_number):
            return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if date_of_birth:
            from datetime import date
            dob = date.fromisoformat(date_of_birth)
            age = (date.today() - dob).days // 365
            if age < 18:
                return Response({'error': 'You must be 18 or older to register'},
                                status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                phone_number = phone_number,
                password=password,
                date_of_birth=date_of_birth
            )
            user.transaction_pin = transaction_pin
            user.save()
            Wallet.objects.create(user=user)

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = Decimal(request.data.get('amount', 0))
        description = request.data.get('description', 'Deposit')

        # validate amount
        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'},
                            status=status.HTTP_400_BAD_REQUEST)

        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

        if not wallet.is_active:
            return Response({'error': 'Wallet is inactive'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # update balance
            wallet.balance += amount
            wallet.save()

            # record transaction
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='deposit',
                amount=amount,
                status='successful',
                description=description,
                balance_after=wallet.balance
            )

            # notify user
            Notification.objects.create(
                user=request.user,
                message=f'Your wallet has been credited with {wallet.currency} {amount}'
            )

        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = Decimal(request.data.get('amount', 0))
        pin = request.data.get('transaction_pin')
        description = request.data.get('description', 'Withdrawal')

        # validate amount
        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'},
                            status=status.HTTP_400_BAD_REQUEST)

        # validate pin
        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

        if not wallet.is_active:
            return Response({'error': 'Wallet is inactive'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.transaction_pin != pin:
            return Response({'error': 'Invalid transaction PIN'},
                            status=status.HTTP_400_BAD_REQUEST)

        # check sufficient balance
        if wallet.balance < amount:
            return Response({'error': 'Insufficient balance'},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            wallet.balance -= amount
            wallet.save()

            Transaction.objects.create(
                wallet=wallet,
                transaction_type='withdrawal',
                amount=amount,
                status='successful',
                description=description,
                balance_after=wallet.balance
            )

            Notification.objects.create(
                user=request.user,
                message=f'Your wallet has been debited with {wallet.currency} {amount}'
            )

        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = Decimal(request.data.get('amount', 0))
        receiver_username = request.data.get('receiver_username')
        pin = request.data.get('transaction_pin')
        description = request.data.get('description', 'Transfer')

        # validate amount
        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'},
                            status=status.HTTP_400_BAD_REQUEST)

        # validate pin
        if request.user.transaction_pin != pin:
            return Response({'error': 'Invalid transaction PIN'},
                            status=status.HTTP_400_BAD_REQUEST)

        # get sender wallet
        sender_wallet = Wallet.objects.filter(user=request.user).first()
        if not sender_wallet:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)

        if not sender_wallet.is_active:
            return Response({'error': 'Your wallet is inactive'}, status=status.HTTP_400_BAD_REQUEST)

        # check sufficient balance
        if sender_wallet.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        # get receiver
        receiver = User.objects.filter(username=receiver_username).first()
        if not receiver:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        # prevent self transfer
        if receiver == request.user:
            return Response({'error': 'You cannot transfer to yourself'},
                            status=status.HTTP_400_BAD_REQUEST)

        # get receiver wallet
        receiver_wallet = Wallet.objects.filter(user=receiver).first()
        if not receiver_wallet or not receiver_wallet.is_active:
            return Response({'error': 'Receiver wallet is inactive or not found'},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # debit sender
            sender_wallet.balance -= amount
            sender_wallet.save()

            # credit receiver
            receiver_wallet.balance += amount
            receiver_wallet.save()

            # create transfer record
            transfer = Transfer.objects.create(
                sender_wallet=sender_wallet,
                receiver_wallet=receiver_wallet,
                amount=amount,
                status='successful',
                description=description
            )

            # record sender transaction
            Transaction.objects.create(
                wallet=sender_wallet,
                transaction_type='transfer_out',
                amount=amount,
                status='successful',
                description=f'Transfer to {receiver_username}',
                balance_after=sender_wallet.balance
            )

            # record receiver transaction
            Transaction.objects.create(
                wallet=receiver_wallet,
                transaction_type='transfer_in',
                amount=amount,
                status='successful',
                description=f'Transfer from {request.user.username}',
                balance_after=receiver_wallet.balance
            )

            # notify both parties
            Notification.objects.create(
                user=request.user,
                message=f'You sent {sender_wallet.currency} {amount} to {receiver_username}'
            )
            Notification.objects.create(
                user=receiver,
                message=f'You received {receiver_wallet.currency} {amount} from {request.user.username}'
            )

        serializer = TransferSerializer(transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def patch(self, request):
        # mark all notifications as read
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})