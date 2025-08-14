"""
Telegram Bot Utility Functions
"""

import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from app.models import Chat, db

logger = logging.getLogger(__name__)

async def fetch_bot_chats(bot_token):
    """
    Fetch all chats where the bot is a member.
    This is a placeholder implementation as the python-telegram-bot library
    doesn't provide a direct method to get all chats.
    """
    try:
        bot = Bot(token=bot_token)
        
        # Get bot information
        bot_info = await bot.get_me()
        logger.info(f"Bot info: {bot_info.first_name} (@{bot_info.username})")
        
        # Note: The python-telegram-bot library doesn't provide a direct way
        # to get all chats where the bot is a member. This would typically
        # require webhook updates or manual tracking.
        
        # For now, return an empty list - in a real implementation,
        # you would need to implement webhook handling to track chats
        logger.warning("Chat fetching requires webhook implementation for automatic detection")
        return []
        
    except TelegramError as e:
        logger.error(f"Telegram API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def refresh_chats_from_database(bot_token):
    """
    Refresh chat list from database and validate with Telegram API.
    This is a synchronous wrapper around the async function.
    """
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            chats = loop.run_until_complete(fetch_bot_chats(bot_token))
            return chats
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error refreshing chats: {e}")
        return []

def add_chat_manually(chat_id, title, username, chat_type):
    """
    Manually add a chat to the database.
    Useful when automatic detection doesn't work.
    """
    try:
        # Check if chat already exists
        existing_chat = Chat.query.filter_by(chat_id=chat_id).first()
        if existing_chat:
            # Update existing chat
            existing_chat.title = title
            existing_chat.username = username
            existing_chat.chat_type = chat_type
            db.session.commit()
            logger.info(f"Updated existing chat: {title} (ID: {chat_id})")
            return existing_chat
        else:
            # Create new chat
            new_chat = Chat(
                chat_id=chat_id,
                title=title,
                username=username,
                chat_type=chat_type
            )
            db.session.add(new_chat)
            db.session.commit()
            logger.info(f"Added new chat: {title} (ID: {chat_id})")
            return new_chat
            
    except Exception as e:
        logger.error(f"Error adding chat manually: {e}")
        db.session.rollback()
        raise

def validate_chat_access(bot_token, chat_id):
    """
    Validate if the bot can access a specific chat.
    """
    try:
        bot = Bot(token=bot_token)
        
        # Try to get chat information
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            chat = loop.run_until_complete(bot.get_chat(chat_id))
            return {
                'valid': True,
                'chat': chat,
                'can_send_messages': True  # Assume yes if we can get chat info
            }
        finally:
            loop.close()
            
    except TelegramError as e:
        if "Chat not found" in str(e):
            return {'valid': False, 'error': 'Chat not found'}
        elif "Forbidden" in str(e):
            return {'valid': False, 'error': 'Bot not allowed in chat'}
        else:
            return {'valid': False, 'error': str(e)}
    except Exception as e:
        logger.error(f"Error validating chat access: {e}")
        return {'valid': False, 'error': 'Unknown error'}
