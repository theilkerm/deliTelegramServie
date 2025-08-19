# Deli Telegram Notification Service

A centralized notification service for Telegram bots built with Flask. This service allows multiple applications to send notifications through a single Telegram bot without sharing bot credentials.

## 🚀 Features

### Core Functionality
- **Centralized Notifications**: Single endpoint for all applications to send messages
- **Service Management**: Create and manage multiple services with unique API keys
- **Chat Management**: Control which Telegram chats each service can send messages to
- **Admin Panel**: Web-based management interface for services and permissions

### Advanced Features
- **Event History**: Track all message sends with detailed statistics
- **Tester Chats**: Mark specific chats for testing scenarios
- **Labels & Descriptions**: Add context to services and chats for better management
- **Real-time Chat Refresh**: Fetch current chat list from Telegram API
- **Comprehensive Logging**: Track all operations and message delivery status

### Security Features
- **Admin Authentication**: Protected admin panel with login system
- **API Key Authentication**: Secure service identification via X-API-KEY header
- **Session Management**: Secure admin sessions with configurable timeouts

## 🏗️ Architecture

- **Backend**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite with proper relational schema
- **Authentication**: Session-based admin login with password hashing
- **API**: RESTful notification endpoint with JSON payloads
- **Telegram Integration**: Direct Bot API calls for reliable message delivery

## 📋 Prerequisites

- Python 3.13+
- Telegram Bot Token
- Admin credentials

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/theilkerm/deliTelegramServie
cd deliTelegramServie
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_hashed_password_here
```

**Generate Password Hash:**
```bash
python generate_password.py
```

### 5. Database Setup
```bash
python setup.py
```

### 6. Run the Application
```bash
python run.py
```

The service will be available at `http://localhost:5000`

## 🚀 Quick Start

### 1. Access Admin Panel
- Navigate to `http://localhost:5000/login`
- Login with your admin credentials

### 2. Add Telegram Chats
- Go to "Chats" section
- Click "Refresh Chats" to fetch from Telegram
- Or manually add chats with labels and descriptions

### 3. Create Services
- Go to "Services" section
- Add new service with name, label, and description
- Copy the generated API key

### 4. Configure Permissions
- Edit each service to select authorized chats
- Use checkboxes to grant/revoke access

### 5. Send Notifications
```bash
curl -X POST http://localhost:5000/api/notify \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_api_key_here" \
  -d '{"message": "Hello from your service!"}'
```

## 📊 API Reference

### Notification Endpoint

**POST** `/api/notify`

**Headers:**
- `Content-Type: application/json`
- `X-API-KEY: <service_api_key>`

**Request Body:**
```json
{
  "message": "Your notification message here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Messages sent successfully",
  "results": [
    {
      "chat_id": 123456789,
      "chat_title": "Test Group",
      "success": true,
      "telegram_message_id": 456,
      "error": null
    }
  ]
}
```

## 🗄️ Database Schema

### Services Table
- `id`: Primary key
- `name`: Service identifier
- `label`: Human-readable label
- `description`: Service description
- `api_key`: Unique API key for authentication
- `created_at`, `updated_at`: Timestamps

### Chats Table
- `id`: Primary key
- `chat_id`: Telegram chat ID
- `title`: Chat title
- `username`: Chat username (if available)
- `chat_type`: Type (private, group, supergroup, channel)
- `label`: Human-readable label
- `description`: Chat description
- `is_tester`: Boolean for test scenarios
- `created_at`, `updated_at`: Timestamps

### Message Events Table
- `id`: Primary key
- `service_id`: Reference to service
- `chat_id`: Reference to chat
- `message_content`: Message text sent
- `telegram_message_id`: Telegram's message ID
- `success`: Delivery status
- `error_message`: Error details if failed
- `sent_at`: Timestamp

## 🔧 Configuration

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key for sessions
- `ADMIN_USERNAME`: Admin login username
- `ADMIN_PASSWORD_HASH`: Hashed admin password

### Flask Configuration
- Session lifetime: 24 hours
- Secure cookies in production
- SQLite database in instance folder

## 🧪 Testing

### Run Test Suite
```bash
python test.py
```

### Send Test Messages
```bash
python send_test_messages.py
```

## 🐳 Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

### Environment Variables
Create `.env` file for Docker:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_hashed_password
```

## 📁 Project Structure

```
deliTelegramServie/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # Web routes and API endpoints
│   ├── auth.py              # Authentication logic
│   └── templates/           # HTML templates
│       ├── base.html        # Base template
│       ├── index.html       # Dashboard
│       ├── login.html       # Admin login
│       ├── services.html    # Service management
│       ├── chats.html       # Chat management
│       └── event_history.html # Message history
├── config.py                # Configuration classes
├── requirements.txt         # Python dependencies
├── setup.py                 # Database initialization
├── run.py                   # Application entry point
├── test.py                  # Comprehensive test suite
├── send_test_messages.py    # Test message sender
├── generate_password.py     # Password hash generator
├── Dockerfile               # Docker container
├── docker-compose.yml       # Docker orchestration
└── README.md                # This file
```

## 🔒 Security Considerations

⚠️ **Important Security Note**: This implementation is designed for development and internal use. For production deployment, consider:

- **HTTPS**: Always use HTTPS in production
- **Strong Passwords**: Use complex admin passwords
- **API Key Rotation**: Regularly rotate service API keys
- **Rate Limiting**: Implement rate limiting for API endpoints
- **Input Validation**: Additional input sanitization
- **Audit Logging**: Enhanced security event logging
- **Database Security**: Consider using PostgreSQL with proper access controls
- **Environment Isolation**: Separate production and development environments

## 🚨 Troubleshooting

### Common Issues

**Database Schema Errors**
- Run `python setup.py` to recreate database
- Delete `instance/telegram_notifier.db` and restart

**Telegram API Errors**
- Verify bot token is correct
- Ensure bot has permission to send messages
- Check chat permissions and bot membership

**Authentication Issues**
- Verify admin credentials in `.env`
- Check password hash generation
- Clear browser cookies/sessions

### Logs
Check application logs for detailed error information. The service logs all database operations and API calls.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Verify configuration settings
4. Create an issue with detailed error information

---

**Deli Telegram Notification Service** - Centralized, secure, and reliable Telegram notifications for your applications.
