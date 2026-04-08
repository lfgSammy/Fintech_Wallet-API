from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('wallet/deposit/', views.DepositView.as_view(), name='depost'),
    path('wallet/withdraw/', views.WithdrawView.as_view(), name= 'withdraw'),
    path('wallet/transfer/', views.TransferView.as_view(), name= 'transfer'),
    path('wallet/transaction/', views.TransactionHistoryView.as_view(), name='transaction-history'),
    path('wallet/notifications/', views.NotificationView.as_view(), name='notifications')
]
