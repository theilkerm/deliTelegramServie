#!/usr/bin/env python3
"""
Debug script to test Telegram message sending directly
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_direct_message():
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        return
    
    print(f"🤖 Testing direct message sending with token: {bot_token[:10]}...")
    
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
    
    # Test 2: Get updates to find chat IDs
    print("\n2️⃣ Getting recent updates to find chat IDs...")
    updates_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        updates_response = requests.get(updates_url, timeout=10)
        if updates_response.status_code == 200:
            updates_data = updates_response.json()
            if updates_data.get('ok'):
                updates = updates_data.get('result', [])
                print(f"   ✅ Found {len(updates)} updates")
                
                if updates:
                    print("   📝 Available chats:")
                    chat_ids = set()
                    for update in updates:
                        if 'message' in update and 'chat' in update['message']:
                            chat = update['message']['chat']
                            chat_id = chat.get('id')
                            chat_ids.add(chat_id)
                            print(f"      Chat ID: {chat_id} - Type: {chat.get('type')} - Title: {chat.get('title', chat.get('first_name', 'Unknown'))}")
                        elif 'channel_post' in update and 'chat' in update['channel_post']:
                            chat = update['channel_post']['chat']
                            chat_id = chat.get('id')
                            chat_ids.add(chat_id)
                            print(f"      Channel ID: {chat_id} - Type: {chat.get('type')} - Title: {chat.get('title', 'Unknown')}")
                    
                    if chat_ids:
                        # Test 3: Send a test message to the first chat
                        test_chat_id = list(chat_ids)[0]
                        print(f"\n3️⃣ Testing message sending to chat ID: {test_chat_id}")
                        
                        test_message = "🔧 This is a test message from the debug script!"
                        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        payload = {
                            'chat_id': test_chat_id,
                            'text': test_message,
                            'parse_mode': 'HTML'
                        }
                        
                        send_response = requests.post(send_url, json=payload, timeout=30)
                        print(f"   Send response status: {send_response.status_code}")
                        
                        if send_response.status_code == 200:
                            send_data = send_response.json()
                            if send_data.get('ok'):
                                print(f"   ✅ Message sent successfully!")
                                print(f"   ✅ Message ID: {send_data['result']['message_id']}")
                                print(f"   ✅ Chat ID: {send_data['result']['chat']['id']}")
                                print(f"   ✅ Date: {send_data['result']['date']}")
                            else:
                                print(f"   ❌ Telegram API error: {send_data.get('description')}")
                        else:
                            print(f"   ❌ HTTP error: {send_response.status_code}")
                            print(f"   ❌ Response: {send_response.text}")
                    else:
                        print("   ❌ No chat IDs found in updates")
                else:
                    print("   ℹ️  No updates found. Send a message to your bot first.")
            else:
                print(f"   ❌ API Error: {updates_data.get('description')}")
        else:
            print(f"   ❌ HTTP Error: {updates_response.status_code}")
    except Exception as e:
        print(f"   ❌ Updates test failed: {e}")
    
    print("\n🎯 Debug test completed!")

if __name__ == '__main__':
    test_direct_message()
