#!/usr/bin/env python3
"""
Test script to verify Telegram Bot API connectivity
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_telegram_api():
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        return
    
    print(f"🤖 Testing Telegram Bot API with token: {bot_token[:10]}...")
    
    # Test 1: Get bot information
    print("\n1️⃣ Testing getMe...")
    me_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        me_response = requests.get(me_url, timeout=10)
        print(f"   Status: {me_response.status_code}")
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            if me_data.get('ok'):
                bot_info = me_data['result']
                print(f"   ✅ Bot name: {bot_info.get('first_name')}")
                print(f"   ✅ Username: @{bot_info.get('username')}")
                print(f"   ✅ Bot ID: {bot_info.get('id')}")
            else:
                print(f"   ❌ API Error: {me_data.get('description')}")
                return
        else:
            print(f"   ❌ HTTP Error: {me_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return
    
    # Test 2: Get updates
    print("\n2️⃣ Testing getUpdates...")
    updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        updates_response = requests.get(updates_url, timeout=10)
        print(f"   Status: {updates_response.status_code}")
        
        if updates_response.status_code == 200:
            updates_data = updates_response.json()
            if updates_data.get('ok'):
                updates = updates_data.get('result', [])
                print(f"   ✅ Found {len(updates)} updates")
                
                if updates:
                    print("   📝 Recent updates:")
                    for i, update in enumerate(updates[:3]):  # Show first 3 updates
                        if 'message' in update:
                            msg = update['message']
                            chat = msg.get('chat', {})
                            print(f"      Update {i+1}: Chat ID {chat.get('id')} - Type: {chat.get('type')} - Title: {chat.get('title', chat.get('first_name', 'Unknown'))}")
                        elif 'channel_post' in update:
                            post = update['channel_post']
                            chat = post.get('chat', {})
                            print(f"      Update {i+1}: Channel ID {chat.get('id')} - Type: {chat.get('type')} - Title: {chat.get('title', 'Unknown')}")
                else:
                    print("   ℹ️  No updates found. Send a message to your bot first.")
            else:
                print(f"   ❌ API Error: {updates_data.get('description')}")
        else:
            print(f"   ❌ HTTP Error: {updates_response.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Test a specific chat ID if we found one
    print("\n3️⃣ Testing getChat with a found chat ID...")
    try:
        updates_response = requests.get(updates_url, timeout=10)
        if updates_response.status_code == 200:
            updates_data = updates_response.json()
            if updates_data.get('ok'):
                updates = updates_data.get('result', [])
                if updates:
                    # Get the first chat ID we find
                    chat_id = None
                    for update in updates:
                        if 'message' in update and 'chat' in update['message']:
                            chat_id = update['message']['chat']['id']
                            break
                        elif 'channel_post' in update and 'chat' in update['channel_post']:
                            chat_id = update['channel_post']['chat']['id']
                            break
                    
                    if chat_id:
                        print(f"   Testing getChat with chat ID: {chat_id}")
                        chat_url = f"https://api.telegram.org/bot{bot_token}/getChat"
                        chat_response = requests.post(chat_url, json={'chat_id': chat_id}, timeout=10)
                        
                        if chat_response.status_code == 200:
                            chat_data = chat_response.json()
                            if chat_data.get('ok'):
                                chat_info = chat_data['result']
                                print(f"   ✅ Chat info retrieved:")
                                print(f"      ID: {chat_info.get('id')}")
                                print(f"      Type: {chat_info.get('type')}")
                                print(f"      Title: {chat_info.get('title', chat_info.get('first_name', 'Unknown'))}")
                                if chat_info.get('username'):
                                    print(f"      Username: @{chat_info.get('username')}")
                            else:
                                print(f"   ❌ Failed to get chat info: {chat_data.get('description')}")
                        else:
                            print(f"   ❌ HTTP Error getting chat: {chat_response.status_code}")
                    else:
                        print("   ℹ️  No chat ID found in updates")
                else:
                    print("   ℹ️  No updates to test with")
    except Exception as e:
        print(f"   ❌ Chat test failed: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == '__main__':
    test_telegram_api()
