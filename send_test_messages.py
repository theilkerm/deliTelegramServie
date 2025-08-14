#!/usr/bin/env python3
"""
Send test lorem ipsum messages to existing chats
This script helps test the notification service with real data
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
LOREM_IPSUM_TEXTS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.",
    "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur.",
    "Magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum.",
    "Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur?",
    "Vel illum qui dolorem eum fugiat quo voluptas nulla pariatur? At vero eos et accusamus et iusto odio.",
    "Dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias."
]

def send_test_message(api_key, message):
    """Send a test message using the API."""
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'message': message
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/notify",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Success: {result.get('message')}")
            print(f"  📊 Recipients: {result.get('recipient_count')}")
            print(f"  ✅ Successful: {result.get('successful_sends')}")
            print(f"  ❌ Failed: {result.get('failed_sends')}")
            
            if result.get('responses'):
                print("  📝 Responses:")
                for resp in result['responses']:
                    status = "✅" if resp['success'] else "❌"
                    print(f"    {status} {resp['chat_title']}: {resp.get('error', 'Sent successfully')}")
        else:
            print(f"  ❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Network error: {str(e)}")
    except Exception as e:
        print(f"  ❌ Unexpected error: {str(e)}")
    
    print()

def main():
    """Main function to send test messages."""
    print("🧪 Deli Telegram Notification Service - Test Message Sender")
    print("=" * 70)
    
    # Check if service is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Service not responding properly (status: {response.status_code})")
            return
        print("✅ Service is running")
    except:
        print("❌ Cannot connect to service. Make sure it's running on http://localhost:5000")
        return
    
    print("\n📝 Enter the API key for your service:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    print(f"\n🎯 Sending {len(LOREM_IPSUM_TEXTS)} test messages...")
    print("=" * 70)
    
    for i, text in enumerate(LOREM_IPSUM_TEXTS, 1):
        print(f"📤 Message {i}/{len(LOREM_IPSUM_TEXTS)}")
        print(f"   Content: {text[:50]}...")
        send_test_message(api_key, text)
        
        # Small delay between messages
        if i < len(LOREM_IPSUM_TEXTS):
            time.sleep(1)
    
    print("🎉 Test message sending completed!")
    print("\n💡 Check the Event History page in the admin panel to see the results.")
    print("   You can also check your Telegram chats for the received messages.")

if __name__ == "__main__":
    main()
