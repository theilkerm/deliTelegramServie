#!/usr/bin/env python3
"""
Database migration script for Deli Telegram Notification Service
This script adds the missing is_tester column and MessageEvent table to existing databases.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the existing database to add new fields and tables."""
    db_path = "telegram_notifier.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. This script is for migrating existing databases.")
        print("   If this is a fresh installation, just run the application normally.")
        return False
    
    print("🔧 Starting database migration...")
    print(f"📁 Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current database structure
        cursor.execute("PRAGMA table_info(chat)")
        chat_columns = [col[1] for col in cursor.fetchall()]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📊 Current chat columns: {chat_columns}")
        print(f"📋 Existing tables: {existing_tables}")
        
        # Add is_tester column to chat table if it doesn't exist
        if 'is_tester' not in chat_columns:
            print("➕ Adding is_tester column to chat table...")
            cursor.execute("ALTER TABLE chat ADD COLUMN is_tester BOOLEAN DEFAULT 0")
            print("✅ is_tester column added successfully")
        else:
            print("✅ is_tester column already exists")
        
        # Create MessageEvent table if it doesn't exist
        if 'message_event' not in existing_tables:
            print("➕ Creating MessageEvent table...")
            cursor.execute("""
                CREATE TABLE message_event (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    message_content TEXT NOT NULL,
                    telegram_message_id INTEGER,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (service_id) REFERENCES service (id),
                    FOREIGN KEY (chat_id) REFERENCES chat (id)
                )
            """)
            print("✅ MessageEvent table created successfully")
        else:
            print("✅ MessageEvent table already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(chat)")
        new_chat_columns = [col[1] for col in cursor.fetchall()]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        new_tables = [table[0] for table in cursor.fetchall()]
        
        print("\n🔍 Migration verification:")
        print(f"📊 New chat columns: {new_chat_columns}")
        print(f"📋 New tables: {new_tables}")
        
        # Check if migration was successful
        if 'is_tester' in new_chat_columns and 'message_event' in new_tables:
            print("\n🎉 Database migration completed successfully!")
            print("✅ All new fields and tables are now available")
            return True
        else:
            print("\n❌ Migration verification failed!")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ SQLite error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def backup_database():
    """Create a backup of the current database before migration."""
    db_path = "telegram_notifier.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"telegram_notifier_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
            return None
    return None

def main():
    """Main migration function."""
    print("🚀 Deli Telegram Notification Service - Database Migration")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("run.py"):
        print("❌ Error: run.py not found. Please run this script from the project root directory.")
        return False
    
    # Check if database exists
    if not os.path.exists("telegram_notifier.db"):
        print("❌ No existing database found. This script is for migrating existing databases.")
        print("   If this is a fresh installation, just run the application normally.")
        return False
    
    # Create backup
    backup_path = backup_database()
    
    # Confirm migration
    print("\n⚠️  This will modify your existing database.")
    if backup_path:
        print(f"   A backup has been created at: {backup_path}")
    
    response = input("\nDo you want to continue with the migration? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Migration cancelled.")
        return False
    
    # Run migration
    success = migrate_database()
    
    if success:
        print("\n🎯 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. The new features should now work properly")
        print("   3. Check the Event History page and tester chat functionality")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        if backup_path:
            print(f"   You can restore from backup: {backup_path}")
    
    return success

if __name__ == "__main__":
    main()
