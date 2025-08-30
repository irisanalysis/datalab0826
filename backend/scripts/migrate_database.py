#!/usr/bin/env python3
"""
Backend Database Migration Script
Migrated and adapted from root migrate_database.py
"""

import os
import sys
import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try importing from new architecture
    from shared.database.connections.postgres import SessionLocal, engine
    from shared.database.models.user import User
    from sqlalchemy import text, inspect
    NEW_ARCHITECTURE = True
    print("✅ Using new FastAPI architecture")
except ImportError:
    # Fallback to legacy Flask app
    try:
        from apps.legacy_flask.main import app, db, User
        from sqlalchemy import text, inspect
        NEW_ARCHITECTURE = False
        print("⚠️  Using legacy Flask architecture")
    except ImportError:
        print("❌ Cannot import database models. Please run from backend directory.")
        sys.exit(1)

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    if NEW_ARCHITECTURE:
        inspector = inspect(engine)
    else:
        inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    if NEW_ARCHITECTURE:
        inspector = inspect(engine)
    else:
        inspector = inspect(db.engine)
    
    try:
        columns = inspector.get_columns(table_name)
        return any(col['name'] == column_name for col in columns)
    except Exception:
        return False

def migrate_user_table():
    """Migrate the users table to add new enterprise fields"""
    print("Migrating users table...")
    
    if NEW_ARCHITECTURE:
        session = SessionLocal()
    else:
        session = db.session
    
    migrations = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(50);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(50);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user';",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR(100);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS organization VARCHAR(100);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en';",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences TEXT;"
    ]
    
    success_count = 0
    for migration in migrations:
        try:
            session.execute(text(migration))
            session.commit()
            print(f"✓ Executed: {migration}")
            success_count += 1
        except Exception as e:
            print(f"⚠️  Skipped (already exists or failed): {migration}")
            session.rollback()
    
    if NEW_ARCHITECTURE:
        session.close()
    
    print(f"✓ User table migration completed: {success_count} changes applied")

def migrate_data_sources_table():
    """Create or migrate data_sources table"""
    print("Migrating data_sources table...")
    
    if NEW_ARCHITECTURE:
        session = SessionLocal()
    else:
        session = db.session
    
    # Create data_sources table if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS data_sources (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        name VARCHAR(100) NOT NULL,
        type VARCHAR(50) NOT NULL,
        config TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        last_test TIMESTAMP,
        error_message TEXT,
        description TEXT,
        tags TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        session.execute(text(create_table_sql))
        session.commit()
        print("✓ Data sources table created/verified")
    except Exception as e:
        print(f"⚠️  Data sources table migration: {str(e)}")
        session.rollback()
    
    if NEW_ARCHITECTURE:
        session.close()

def migrate_sessions_table():
    """Create user_sessions table for session management"""
    print("Migrating user_sessions table...")
    
    if NEW_ARCHITECTURE:
        session = SessionLocal()
    else:
        session = db.session
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        session_id VARCHAR(128) UNIQUE NOT NULL,
        device_info TEXT,
        ip_address VARCHAR(45),
        user_agent VARCHAR(500),
        location VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
    CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
    """
    
    try:
        session.execute(text(create_table_sql))
        session.commit()
        print("✓ User sessions table created/verified")
    except Exception as e:
        print(f"⚠️  User sessions table migration: {str(e)}")
        session.rollback()
    
    if NEW_ARCHITECTURE:
        session.close()

def create_indexes():
    """Create database indexes for better performance"""
    print("Creating database indexes...")
    
    if NEW_ARCHITECTURE:
        session = SessionLocal()
    else:
        session = db.session
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
        "CREATE INDEX IF NOT EXISTS idx_data_sources_user_id ON data_sources(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_data_sources_type ON data_sources(type);",
        "CREATE INDEX IF NOT EXISTS idx_data_sources_status ON data_sources(status);"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            session.execute(text(index_sql))
            session.commit()
            print(f"✓ Created index: {index_sql}")
            success_count += 1
        except Exception as e:
            print(f"⚠️  Index already exists or failed: {index_sql}")
            session.rollback()
    
    if NEW_ARCHITECTURE:
        session.close()
    
    print(f"✓ Index creation completed: {success_count} indexes created")

def check_migration_status():
    """Check current database schema status"""
    print("Checking migration status...")
    
    tables_to_check = ['users', 'data_sources', 'user_sessions']
    
    for table in tables_to_check:
        if check_table_exists(table):
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' missing")
    
    # Check specific columns
    user_columns = ['first_name', 'last_name', 'role', 'is_active']
    for column in user_columns:
        if check_column_exists('users', column):
            print(f"✅ Column 'users.{column}' exists")
        else:
            print(f"❌ Column 'users.{column}' missing")

def main():
    """Main migration function"""
    print("🔄 AI Data Platform Database Migration")
    print("=" * 50)
    
    # Check current status
    check_migration_status()
    
    print("\nStarting migrations...")
    
    # Run migrations
    try:
        migrate_user_table()
        migrate_data_sources_table() 
        migrate_sessions_table()
        create_indexes()
        
        print("\n✅ All database migrations completed successfully!")
        
        # Final status check
        print("\nFinal migration status:")
        check_migration_status()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()