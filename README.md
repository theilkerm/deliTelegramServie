# Deli Telegram Notification Service

A centralized notification service for Telegram bots built with Flask. This application allows you to manage multiple services and their permissions to send notifications to specific Telegram chats, eliminating the need to configure bot credentials in multiple applications.

> ⚠️ **SECURITY WARNING**: This application is designed for development and testing purposes only. It lacks enterprise-grade security features and should NOT be used in production environments without significant security enhancements. See the [Security Considerations](#-security-considerations) section for details.

## Features

- **Service Management**: Create and manage multiple services with unique API keys
- **Chat Management**: Manage Telegram chats (groups, channels, private chats) and their permissions
- **Secure API**: Cryptographically secure API key generation and authentication
- **Web Interface**: Beautiful Bootstrap-based admin panel for easy management
- **Permission Control**: Granular control over which services can send messages to which chats
- **Asynchronous Notifications**: Non-blocking message delivery to multiple chats
- **Labels & Descriptions**: Add labels and descriptions to services and chats for better organization
- **Admin Authentication**: Secure login system to protect the management panel
- **Direct Telegram API**: Uses direct HTTP requests to Telegram Bot API for reliability
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Project Structure

```
/deliTelegramServie
|-- /app
|   |-- /templates
|   |   |-- index.html          # Dashboard home page
|   |   |-- services.html       # Services listing and management
|   |   |-- add_service.html    # Add new service form
|   |   |-- edit_service.html   # Edit service permissions
|   |   |-- edit_service_details.html # Edit service details
|   |   |-- chats.html          # Chat management
|   |   |-- add_chat.html       # Add new chat form
|   |   |-- edit_chat.html      # Edit chat details
|   |   |-- login.html          # Admin login page
|   |-- /auth.py                # Authentication system
|   |-- /simple_db.py           # JSON-based database system
|   |-- __init__.py             # Flask app factory
|   |-- routes.py               # Web routes and API endpoints
|-- run.py                      # Application entry point
|-- .env                        # Environment variables
|-- requirements.txt            # Python dependencies
|-- Dockerfile                  # Docker container definition
|-- docker-compose.yml          # Docker Compose configuration
|-- debug_message.py            # Debug script for testing
|-- generate_password.py        # Password hash generator
```

## Prerequisites

- Python 3.8 or higher (tested with Python 3.13)
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Docker and Docker Compose (for containerized deployment)

## Quick Start

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd deliTelegramServie
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy .env.example to .env if it exists, or create .env manually
   # Edit .env file with your Telegram bot token and admin credentials
   ```

5. **Generate admin password hash**
   ```bash
   python generate_password.py
   # Copy the generated hash to your .env file
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the web interface**
   Open your browser and go to `http://localhost:5000`

### Option 2: Docker Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd deliTelegramServie
   ```

2. **Configure environment**
   ```bash
   # Edit .env file with your Telegram bot token and admin credentials
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker compose up -d
   ```

4. **Access the web interface**
   Open your browser and go to `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Admin Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_generated_password_hash_here
```

### Getting a Telegram Bot Token

1. Start a conversation with [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided

### Setting Up Admin Authentication

1. Run `python generate_password.py`
2. Enter your desired admin password
3. Copy the generated hash to your `.env` file
4. Use the same username/password to log into the web interface

## Usage

### Web Interface

1. **Dashboard**: Overview of services and chats
2. **Services**: Manage your notification services with labels and descriptions
3. **Chats**: View and refresh Telegram chat list, add manual chats
4. **Add Service**: Create new services with auto-generated API keys
5. **Edit Service Details**: Modify service name, label, and description
6. **Edit Permissions**: Configure which chats each service can notify

### Service Labels and Descriptions

- **Labels**: Short identifiers (e.g., "MON", "ALERT", "SYS") for quick recognition
- **Descriptions**: Detailed explanations of what each service does
- **Chat Labels**: Organize chats with labels like "TEAM", "ADMIN", "ALERTS"

### API Usage

Send notifications using the `/api/notify` endpoint:

```bash
curl -X POST http://your-domain/api/notify \
  -H "X-API-KEY: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"message": "Your notification text"}'
```

**Headers Required:**
- `X-API-KEY`: Your service's API key
- `Content-Type: application/json`

**Request Body:**
```json
{
  "message": "Your notification text here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification sent successfully",
  "recipient_count": 3,
  "successful_sends": 3,
  "failed_sends": 0,
  "responses": [
    {
      "chat_id": 123456789,
      "chat_title": "My Group",
      "success": true,
      "message_id": 987,
      "error": null
    }
  ]
}
```

### Adding Chats

1. Add your bot to Telegram groups, channels, or start private conversations
2. Send a message in the chat
3. Use the "Refresh Chat List" button in the web interface
4. The bot will automatically detect and list available chats
5. Optionally add labels and descriptions to organize your chats

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Dashboard home page |
| `GET` | `/login` | Admin login page |
| `POST` | `/login` | Admin authentication |
| `GET` | `/logout` | Admin logout |
| `GET` | `/services` | List all services |
| `GET` | `/services/add` | Add new service form |
| `POST` | `/services/add` | Create new service |
| `GET` | `/services/<id>/edit` | Edit service permissions |
| `POST` | `/services/<id>/edit` | Update service permissions |
| `GET` | `/services/<id>/edit-details` | Edit service details |
| `POST` | `/services/<id>/edit-details` | Update service details |
| `GET` | `/chats` | List all chats |
| `GET` | `/chats/add` | Add new chat form |
| `POST` | `/chats/add` | Create new chat |
| `GET` | `/chats/<id>/edit` | Edit chat details |
| `POST` | `/chats/<id>/edit` | Update chat details |
| `POST` | `/chats/refresh` | Refresh chat list from Telegram |
| `POST` | `/chats/clear` | Clear all chats |
| `POST` | `/api/notify` | Send notification (API endpoint) |
| `POST` | `/api/test-message` | Test message to specific chat |

### Authentication

The web interface requires admin login, and the `/api/notify` endpoint requires authentication via the `X-API-KEY` header. The API key is automatically generated when you create a service and can be viewed in the services list.

## Database Models

### Service
- `id`: Primary key
- `name`: Service name (unique)
- `label`: Short identifier for quick recognition
- `description`: Detailed description of the service
- `api_key`: Cryptographically secure API key
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `authorized_chat_ids`: List of authorized chat IDs

### Chat
- `id`: Primary key
- `chat_id`: Telegram chat ID
- `title`: Chat title/name
- `username`: Chat username (if available)
- `chat_type`: Type (private, group, supergroup, channel)
- `label`: Short identifier for quick recognition
- `description`: Detailed description of the chat
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Security Features

- **Secure API Keys**: Cryptographically secure random generation
- **Header Authentication**: API key validation via custom HTTP header
- **Admin Login**: Protected web interface with password hashing
- **Input Validation**: Comprehensive request validation and sanitization
- **Error Handling**: Secure error responses without information leakage
- **Non-root Docker**: Application runs as non-root user in container

## ⚠️ Security Considerations

**This application is designed for development and testing purposes. For production use, consider the following security improvements:**

### Current Limitations:
- **JSON Database**: Uses simple file-based storage without encryption
- **Basic Authentication**: Simple username/password with Werkzeug hashing
- **No Rate Limiting**: API endpoints lack rate limiting and brute force protection
- **No HTTPS Enforcement**: No built-in SSL/TLS enforcement
- **Session Management**: Basic Flask session handling without advanced security features

### Production Security Recommendations:
- **Database Security**: Use PostgreSQL with proper access controls and encryption
- **Authentication**: Implement OAuth2, JWT tokens, or integrate with enterprise SSO
- **API Security**: Add rate limiting, request signing, and IP whitelisting
- **Transport Security**: Enforce HTTPS with proper SSL/TLS configuration
- **Monitoring**: Implement security logging, intrusion detection, and audit trails
- **Access Control**: Add role-based access control (RBAC) and multi-factor authentication
- **Secrets Management**: Use proper secrets management (HashiCorp Vault, AWS Secrets Manager, etc.)
- **Network Security**: Deploy behind reverse proxy with WAF protection

## Deployment

### Production Considerations

1. **Environment Variables**: Use strong, unique secret keys
2. **Database**: The JSON-based database is suitable for small to medium deployments
3. **Reverse Proxy**: Use Nginx or Apache as reverse proxy
4. **SSL/TLS**: Enable HTTPS for production deployments
5. **Monitoring**: Implement logging and monitoring solutions

### ⚠️ Production Security Warning

**This application is NOT recommended for production use without significant security enhancements. The current implementation lacks enterprise-grade security features and should only be used in:**

- Development and testing environments
- Internal networks with restricted access
- Proof-of-concept demonstrations
- Learning and educational purposes

**For production deployments, implement the security recommendations listed in the Security Considerations section above.**

### Docker Commands

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild and restart
docker compose up -d --build
```

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check bot token and permissions
2. **No chats appearing**: Ensure bot is added to groups/channels
3. **Permission errors**: Verify bot has send message permissions
4. **API key issues**: Regenerate API key if compromised
5. **Login issues**: Check admin credentials in .env file

### Debug Tools

Use the included debug script to test Telegram API connectivity:

```bash
python debug_message.py
```

This script will:
- Test bot token validity
- Check for available chats
- Test message sending to a specific chat

### Logs

Check application logs for detailed error information:

```bash
# Docker logs
docker compose logs deli-telegram-notifier

# Local development
# Logs appear in console when running python run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the AGPL License - see the [LICENSE](LICENSE.md) file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Use the debug script to test connectivity
4. Open an issue on GitHub
5. Check [Telegram Bot API documentation](https://core.telegram.org/bots/api)

## Changelog

### v2.0.0
- Added labels and descriptions for services and chats
- Enhanced admin authentication system
- Improved chat refresh functionality using direct Telegram API
- Added detailed API response tracking
- Better error handling and debugging tools
- Updated to Python 3.13 compatibility

### v1.0.0
- Initial release
- Service management with secure API keys
- Chat permission management
- Web-based admin interface
- Docker support
- Asynchronous notification delivery
