from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, session
from app.models import db, Service, Chat, MessageEvent
import asyncio
import threading
import logging
from telegram import Bot
from telegram.error import TelegramError
import json
import secrets
import string
from app.auth import login_required, authenticate_user, logout_user, get_current_user

main_bp = Blueprint('main', __name__)

def generate_api_key(length=32):
    """Generate a cryptographically secure API key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def send_telegram_message_async(chat_id, message, bot_token):
    """Send Telegram message asynchronously in a separate thread."""
    try:
        import requests
        
        # Use direct HTTP request to Telegram API
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'  # Allow basic HTML formatting
        }
        
        response = requests.post(send_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logging.info(f"Message sent successfully to chat {chat_id}")
                return {'success': True, 'chat_id': chat_id, 'message_id': result['result']['message_id']}
            else:
                logging.error(f"Telegram API error for chat {chat_id}: {result.get('description')}")
                return {'success': False, 'chat_id': chat_id, 'error': result.get('description')}
        else:
            logging.error(f"HTTP error sending to chat {chat_id}: {response.status_code}")
            return {'success': False, 'chat_id': chat_id, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        logging.error(f"Unexpected error sending message to chat {chat_id}: {e}")
        return {'success': False, 'chat_id': chat_id, 'error': str(e)}

@main_bp.route('/')
def index():
    """Home page."""
    current_user = get_current_user()
    
    # Safely query database, handle case when tables don't exist yet
    try:
        services = Service.query.all() if current_user and current_user['authenticated'] else []
        total_chats = Chat.query.count() if current_user and current_user['authenticated'] else 0
    except Exception as e:
        # If database tables don't exist yet, provide empty data
        logging.warning(f"Database query failed on homepage: {e}")
        services = []
        total_chats = 0
    
    return render_template('index.html', services=services, total_chats=total_chats, current_user=current_user)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if authenticate_user(username, password):
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', current_user=get_current_user())

@main_bp.route('/logout')
def logout():
    """Admin logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/services')
@login_required
def services():
    """List all services."""
    try:
        services = Service.query.all()
    except Exception as e:
        logging.warning(f"Database query failed on services page: {e}")
        services = []
        flash('Database not ready yet. Please wait a moment and try again.', 'warning')
    
    return render_template('services.html', services=services, current_user=get_current_user())

@main_bp.route('/services/add', methods=['GET', 'POST'])
@login_required
def add_service():
    """Add a new service."""
    if request.method == 'POST':
        name = request.form.get('name')
        label = request.form.get('label', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Service name is required', 'error')
            return render_template('add_service.html', current_user=get_current_user())
        
        # Check if service name already exists
        if Service.query.filter_by(name=name).first():
            flash('Service with this name already exists', 'error')
            return render_template('add_service.html', current_user=get_current_user())
        
        # Create new service
        service = Service(
            name=name,
            label=label,
            description=description,
            api_key=generate_api_key()
        )
        
        db.session.add(service)
        db.session.commit()
        
        flash(f'Service "{name}" created successfully! API Key: {service.api_key}', 'success')
        return redirect(url_for('main.services'))
    
    return render_template('add_service.html', current_user=get_current_user())

@main_bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    """Edit service chat permissions."""
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        # Get selected chat IDs from form
        selected_chat_ids = [int(chat_id) for chat_id in request.form.getlist('chats')]
        
        # Get chat objects
        selected_chats = Chat.query.filter(Chat.id.in_(selected_chat_ids)).all()
        
        # Update service permissions
        service.authorized_chats = selected_chats
        db.session.commit()
        
        flash(f'Chat permissions updated for service "{service.name}"', 'success')
        return redirect(url_for('main.services'))
    
    # Get all chats and current permissions
    all_chats = Chat.query.all()
    authorized_chat_ids = [chat.id for chat in service.authorized_chats]
    
    return render_template('edit_service.html', 
                         service=service, 
                         all_chats=all_chats, 
                         authorized_chat_ids=authorized_chat_ids,
                         current_user=get_current_user())

@main_bp.route('/services/<int:service_id>/edit-details', methods=['GET', 'POST'])
@login_required
def edit_service_details(service_id):
    """Edit service details (name, label, description)."""
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        label = request.form.get('label', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Service name is required', 'error')
            return render_template('edit_service_details.html', service=service, current_user=get_current_user())
        
        # Check if service name already exists (excluding current service)
        existing_service = Service.query.filter_by(name=name).first()
        if existing_service and existing_service.id != service_id:
            flash('Service with this name already exists', 'error')
            return render_template('edit_service_details.html', service=service, current_user=get_current_user())
        
        # Update service details
        service.name = name
        service.label = label
        service.description = description
        db.session.commit()
        
        flash(f'Service "{name}" updated successfully!', 'success')
        return redirect(url_for('main.services'))
    
    return render_template('edit_service_details.html', service=service, current_user=get_current_user())

@main_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service(service_id):
    """Delete a service."""
    service = Service.query.get_or_404(service_id)
    service_name = service.name
    
    try:
        # Delete the service (this will also remove the association table entries)
        db.session.delete(service)
        db.session.commit()
        
        flash(f'Service "{service_name}" has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting service "{service_name}": {str(e)}', 'error')
    
    return redirect(url_for('main.services'))

@main_bp.route('/chats')
@login_required
def chats():
    """List all Telegram chats."""
    try:
        chats = Chat.query.all()
    except Exception as e:
        logging.warning(f"Database query failed on chats page: {e}")
        chats = []
        flash('Database not ready yet. Please wait a moment and try again.', 'warning')
    
    return render_template('chats.html', chats=chats, current_user=get_current_user())

@main_bp.route('/chats/add', methods=['GET', 'POST'])
@login_required
def add_chat():
    """Manually add a chat."""
    if request.method == 'POST':
        chat_id = request.form.get('chat_id')
        title = request.form.get('title')
        username = request.form.get('username')
        chat_type = request.form.get('chat_type')
        
        if not chat_id or not title:
            flash('Chat ID and title are required', 'error')
            return render_template('add_chat.html', current_user=get_current_user())
        
        try:
            chat_id = int(chat_id)
            label = request.form.get('label', '').strip()
            description = request.form.get('description', '').strip()
            
            # Check if chat already exists
            if Chat.query.filter_by(chat_id=chat_id).first():
                flash('Chat with this ID already exists', 'error')
                return render_template('add_chat.html', current_user=get_current_user())
            
            chat = Chat(
                chat_id=chat_id,
                title=title,
                username=username or '',
                chat_type=chat_type or 'private',
                label=label,
                description=description
            )
            
            db.session.add(chat)
            db.session.commit()
            
            flash(f'Chat "{title}" added successfully!', 'success')
            return redirect(url_for('main.chats'))
        except ValueError:
            flash('Chat ID must be a valid number', 'error')
        except Exception as e:
            flash(f'Error adding chat: {str(e)}', 'error')
    
    return render_template('add_chat.html', current_user=get_current_user())

@main_bp.route('/chats/<int:chat_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_chat(chat_id):
    """Edit chat details."""
    chat = Chat.query.get_or_404(chat_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        username = request.form.get('username', '').strip()
        chat_type = request.form.get('chat_type')
        label = request.form.get('label', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title:
            flash('Chat title is required', 'error')
            return render_template('edit_chat.html', chat=chat, current_user=get_current_user())
        
        # Update chat details
        chat.title = title
        chat.username = username
        chat.chat_type = chat_type
        chat.label = label
        chat.description = description
        db.session.commit()
        
        flash(f'Chat "{title}" updated successfully!', 'success')
        return redirect(url_for('main.chats'))
    
    return render_template('edit_chat.html', chat=chat, current_user=get_current_user())

@main_bp.route('/chats/clear', methods=['POST'])
@login_required
def clear_chats():
    """Clear all chats from database."""
    try:
        # Clear all chats
        Chat.query.delete()
        db.session.commit()
        flash('All chats have been cleared from the database.', 'success')
    except Exception as e:
        flash(f'Error clearing chats: {str(e)}', 'error')
    
    return redirect(url_for('main.chats'))

@main_bp.route('/history')
@login_required
def event_history():
    """Show message event history and statistics."""
    try:
        # Get all message events with pagination
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        events = MessageEvent.query.order_by(MessageEvent.sent_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_events = MessageEvent.query.count()
        successful_events = MessageEvent.query.filter_by(success=True).count()
        failed_events = MessageEvent.query.filter_by(success=False).count()
        
        # Service statistics
        service_stats = db.session.query(
            Service.name,
            db.func.count(MessageEvent.id).label('total_messages'),
            db.func.sum(db.case((MessageEvent.success == True, 1), else_=0)).label('successful_messages'),
            db.func.sum(db.case((MessageEvent.success == False, 1), else_=0)).label('failed_messages')
        ).join(MessageEvent).group_by(Service.name).all()
        
        # Chat statistics
        chat_stats = db.session.query(
            Chat.title,
            db.func.count(MessageEvent.id).label('total_messages'),
            db.func.sum(db.case((MessageEvent.success == True, 1), else_=0)).label('successful_messages'),
            db.func.sum(db.case((MessageEvent.success == False, 1), else_=0)).label('failed_messages')
        ).join(MessageEvent).group_by(Chat.title).all()
        
        return render_template('event_history.html', 
                             events=events,
                             total_events=total_events,
                             successful_events=successful_events,
                             failed_events=failed_events,
                             service_stats=service_stats,
                             chat_stats=chat_stats,
                             current_user=get_current_user())
    except Exception as e:
        logging.warning(f"Database query failed on event history page: {e}")
        flash('Database not ready yet. Please wait a moment and try again.', 'warning')
        # Return empty data
        return render_template('event_history.html', 
                             events=None,
                             total_events=0,
                             successful_events=0,
                             failed_events=0,
                             service_stats=[],
                             chat_stats=[],
                             current_user=get_current_user())

@main_bp.route('/chats/<int:chat_id>/toggle-tester', methods=['POST'])
@login_required
def toggle_chat_tester(chat_id):
    """Toggle the tester status of a chat."""
    chat = Chat.query.get_or_404(chat_id)
    chat.is_tester = not chat.is_tester
    db.session.commit()
    
    status = "tester" if chat.is_tester else "regular"
    flash(f'Chat "{chat.title}" marked as {status}', 'success')
    return redirect(url_for('main.chats'))

@main_bp.route('/chats/refresh', methods=['POST'])
@login_required
def refresh_chats():
    """Refresh chat list from Telegram API."""
    bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        flash('Telegram bot token not configured', 'error')
        return redirect(url_for('main.chats'))
    
    try:
        import requests
        
        # First, test if the bot token is valid by calling getMe
        me_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        me_response = requests.get(me_url, timeout=10)
        logging.info(f"Bot info response status: {me_response.status_code}")
        
        if me_response.status_code != 200:
            flash(f'Failed to connect to Telegram API: {me_response.status_code}. Check your bot token.', 'error')
            return redirect(url_for('main.chats'))
        
        me_data = me_response.json()
        if not me_data.get('ok'):
            flash(f'Invalid bot token: {me_data.get("description", "Unknown error")}', 'error')
            return redirect(url_for('main.chats'))
        
        bot_info = me_data['result']
        logging.info(f"Bot info: {bot_info}")
        
        # Get updates to find recent chats
        updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        logging.info(f"Fetching updates from: {updates_url}")
        
        updates_response = requests.get(updates_url, timeout=10)
        logging.info(f"Updates response status: {updates_response.status_code}")
        
        if updates_response.status_code != 200:
            flash(f'Failed to get updates from Telegram API: {updates_response.status_code}', 'error')
            return redirect(url_for('main.chats'))
        
        updates_data = updates_response.json()
        logging.info(f"Updates data: {updates_data}")
        
        if not updates_data.get('ok'):
            flash(f'Telegram API error: {updates_data.get("description", "Unknown error")}', 'error')
            return redirect(url_for('main.chats'))
        
        updates = updates_data.get('result', [])
        logging.info(f"Found {len(updates)} updates")
        
        if not updates:
            flash('No recent updates found. Send a message to your bot first.', 'info')
            return redirect(url_for('main.chats'))
        
        # Extract unique chat IDs from updates
        chat_ids = set()
        for update in updates:
            if 'message' in update and 'chat' in update['message']:
                chat_ids.add(update['message']['chat']['id'])
                logging.info(f"Found chat ID from message: {update['message']['chat']['id']}")
            elif 'edited_message' in update and 'chat' in update['edited_message']:
                chat_ids.add(update['edited_message']['chat']['id'])
                logging.info(f"Found chat ID from edited message: {update['edited_message']['chat']['id']}")
            elif 'channel_post' in update and 'chat' in update['channel_post']:
                chat_ids.add(update['channel_post']['chat']['id'])
                logging.info(f"Found chat ID from channel post: {update['channel_post']['chat']['id']}")
        
        logging.info(f"Extracted {len(chat_ids)} unique chat IDs: {chat_ids}")
        
        if not chat_ids:
            flash('No chat information found in updates.', 'info')
            return redirect(url_for('main.chats'))
        
        # Get detailed information for each chat
        new_chats = 0
        existing_chat_ids = {chat.chat_id for chat in Chat.query.all()}
        
        for chat_id in chat_ids:
            if chat_id not in existing_chat_ids:
                # Get detailed chat information
                chat_url = f"https://api.telegram.org/bot{bot_token}/getChat"
                chat_response = requests.post(chat_url, json={'chat_id': chat_id}, timeout=10)
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    if chat_data.get('ok'):
                        chat_info = chat_data['result']
                        
                        # Extract chat information
                        title = chat_info.get('title') or chat_info.get('first_name', '') or chat_info.get('username', '')
                        username = chat_info.get('username', '')
                        chat_type = chat_info.get('type', 'private')
                        
                        # Add chat to database
                        chat = Chat(
                            chat_id=chat_id,
                            title=title,
                            username=username,
                            chat_type=chat_type,
                            label="",
                            description=""
                        )
                        db.session.add(chat)
                        new_chats += 1
                    else:
                        logging.warning(f"Failed to get chat {chat_id}: {chat_data.get('description')}")
                else:
                    logging.warning(f"Failed to get chat {chat_id}: HTTP {chat_response.status_code}")
        
        if new_chats > 0:
            db.session.commit()
            flash(f'Successfully refreshed chat list! Found {new_chats} new chat(s).', 'success')
        else:
            flash('No new chats found. All chats are already in the database.', 'info')
        
        return redirect(url_for('main.chats'))
        
    except requests.exceptions.RequestException as e:
        flash(f'Network error connecting to Telegram API: {str(e)}', 'error')
        return redirect(url_for('main.chats'))
    except Exception as e:
        flash(f'Error refreshing chats: {str(e)}', 'error')
        return redirect(url_for('main.chats'))

@main_bp.route('/api/notify', methods=['POST'])
def notify():
    """API endpoint for sending notifications."""
    # First validate request format and content
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing JSON in request body'}), 400
        
        if 'message' not in data:
            return jsonify({'error': 'Missing message in request body'}), 400
        
        message = data['message']
        if not message or not message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON in request body'}), 400
    except Exception:
        # Handle any other parsing errors (like invalid content type)
        return jsonify({'error': 'Invalid request format'}), 400
    
    # Then validate API key
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        return jsonify({'error': 'Missing API key'}), 401
    
    service = Service.query.filter_by(api_key=api_key).first()
    if not service:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Format message with service name
    formatted_message = f"{service.name}: {message.strip()}"
    
    # Get bot token
    bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logging.error('Telegram bot token not configured')
        return jsonify({'error': 'Bot not configured'}), 500
    
    # Get authorized chats for this service
    authorized_chats = service.authorized_chats
    if not authorized_chats:
        logging.warning(f'Service "{service.name}" has no authorized chats')
        return jsonify({'error': 'No authorized chats for this service'}), 400
    
    # Send messages to all authorized chats and collect responses
    import concurrent.futures
    
    responses = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all message sending tasks
        future_to_chat = {
            executor.submit(send_telegram_message_async, chat.chat_id, formatted_message, bot_token): chat
            for chat in authorized_chats
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_chat):
            chat = future_to_chat[future]
            try:
                result = future.result()
                
                # Log message event
                event = MessageEvent(
                    service_id=service.id,
                    chat_id=chat.id,
                    message_content=formatted_message,
                    telegram_message_id=result.get('message_id'),
                    success=result['success'],
                    error_message=result.get('error')
                )
                db.session.add(event)
                
                responses.append({
                    'chat_id': chat.chat_id,
                    'chat_title': chat.title or chat.username or f"Chat {chat.chat_id}",
                    'success': result['success'],
                    'message_id': result.get('message_id'),
                    'error': result.get('error')
                })
            except Exception as e:
                # Log failed event
                event = MessageEvent(
                    service_id=service.id,
                    chat_id=chat.id,
                    message_content=formatted_message,
                    success=False,
                    error_message=str(e)
                )
                db.session.add(event)
                
                responses.append({
                    'chat_id': chat.chat_id,
                    'chat_title': chat.title or chat.username or f"Chat {chat.chat_id}",
                    'success': False,
                    'error': str(e)
                })
        
        # Commit all events
        db.session.commit()
    
    # Count successful sends
    successful_sends = sum(1 for r in responses if r['success'])
    failed_sends = len(responses) - successful_sends
    
    logging.info(f'Service "{service.name}" sent notification to {len(authorized_chats)} chats. Success: {successful_sends}, Failed: {failed_sends}')
    
    return jsonify({
        'success': True,
        'message': 'Notification sent successfully',
        'recipient_count': len(authorized_chats),
        'successful_sends': successful_sends,
        'failed_sends': failed_sends,
        'responses': responses
    }), 200

@main_bp.route('/api/test-message', methods=['POST'])
@login_required
def test_message():
    """Test endpoint to send a message to a specific chat ID."""
    try:
        data = request.get_json()
        if not data or 'chat_id' not in data or 'message' not in data:
            return jsonify({'error': 'Missing chat_id or message in request body'}), 400
        
        chat_id = data['chat_id']
        message = data['message']
        bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        
        if not bot_token:
            return jsonify({'error': 'Bot token not configured'}), 500
        
        # Send test message
        result = send_telegram_message_async(chat_id, message, bot_token)
        
        return jsonify({
            'success': result['success'],
            'chat_id': chat_id,
            'message': message,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
