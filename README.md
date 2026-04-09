# Fintech Wallet API

A secure fintech wallet REST API built with Django and Django REST Framework.

## Features
- Token based authentication
- Automatic wallet creation on registration
- Age verification (18+) during registration
- Wallet funding and withdrawal with PIN verification
- Peer-to-peer transfers with atomic transactions
- Complete transaction history with audit trail
- Balance frozen at time of each transaction
- Notifications for every wallet activity

## Tech Stack
- Python
- Django
- Django REST Framework
- SQLite

## Setup

```bash
git clone https://github.com/lfgSammy/fintech-wallet-api.git
cd fintech-wallet-api
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/register/ | Register and create wallet | No |
| POST | /api/auth/login/ | Login and get token | No |

### Wallet
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/wallet/ | Get wallet balance | Yes |
| POST | /api/wallet/deposit/ | Fund wallet | Yes |
| POST | /api/wallet/withdraw/ | Withdraw funds | Yes + PIN |
| POST | /api/wallet/transfer/ | Send money to user | Yes + PIN |
| GET | /api/wallet/transactions/ | Transaction history | Yes |

### Notifications
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/notifications/ | Get notifications | Yes |
| PATCH | /api/notifications/ | Mark all as read | Yes |

## Key Design Decisions
- Every financial operation uses `transaction.atomic()` — if anything fails, everything rolls back
- `balance_after` is recorded on every transaction — creates a permanent audit trail
- Transfers create two transaction records — one for sender, one for receiver
- PIN is required for withdrawals and transfers — deposits don't need PIN
- Wallet is created automatically on registration — users can never be without a wallet
- UUIDs used for transaction IDs — impossible to duplicate or guess
