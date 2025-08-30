#!/usr/bin/env python3
"""
Database Migration Script for SaaS Data Analysis Platform
Handles schema updates and data migrations for existing installations
"""

import os
import sys
import datetime
from sqlalchemy import text, inspect
# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from apps.legacy_flask.main import app, db, User

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def migrate_user_table():
    """Migrate the users table to add new enterprise fields"""
    print("Migrating users table...")
    
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
    
    for migration in migrations:
        try:
            db.session.execute(text(migration))
            db.session.commit()
            print(f"✓ Executed: {migration}")
        except Exception as e:
            print(f"✗ Failed: {migration} - {str(e)}")
            db.session.rollback()

def create_new_tables():
    """Create new tables for the SaaS platform"""
    print("Creating new tables...")
    
    # Create all tables defined in models
    db.create_all()
    print("✓ All tables created/updated")

def update_refresh_tokens_table():
    """Update refresh_tokens table to add session_id column"""
    print("Updating refresh_tokens table...")
    
    try:
        if not check_column_exists('refresh_tokens', 'session_id'):
            db.session.execute(text("ALTER TABLE refresh_tokens ADD COLUMN session_id VARCHAR(128);"))
            db.session.execute(text("ALTER TABLE refresh_tokens ADD FOREIGN KEY (session_id) REFERENCES user_sessions(session_id);"))
            db.session.commit()
            print("✓ Added session_id column to refresh_tokens")
        else:
            print("✓ session_id column already exists in refresh_tokens")
    except Exception as e:
        print(f"✗ Failed to update refresh_tokens table: {str(e)}")
        db.session.rollback()

def create_indexes():
    """Create database indexes for performance"""
    print("Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
        "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_data_sources_user_id ON data_sources(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_data_sources_type ON data_sources(type);",
        "CREATE INDEX IF NOT EXISTS idx_data_sources_status ON data_sources(status);",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_integrations_user_id ON integrations(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_integrations_provider ON integrations(provider);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_refresh_tokens_session_id ON refresh_tokens(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);"
    ]
    
    for index in indexes:
        try:
            db.session.execute(text(index))
            db.session.commit()
            print(f"✓ Created index: {index.split()[5]}")
        except Exception as e:
            print(f"✗ Failed to create index: {str(e)}")
            db.session.rollback()

def update_existing_users():
    """Update existing users with default values for new fields"""
    print("Updating existing users with default values...")
    
    try:
        users = User.query.all()
        for user in users:
            if user.is_active is None:
                user.is_active = True
            if user.role is None:
                user.role = 'user'
            if user.timezone is None:
                user.timezone = 'UTC'
            if user.language is None:
                user.language = 'en'
        
        db.session.commit()
        print(f"✓ Updated {len(users)} existing users")
    except Exception as e:
        print(f"✗ Failed to update existing users: {str(e)}")
        db.session.rollback()

def main():
    """Main migration function"""
    print("=" * 60)
    print("SaaS Data Analysis Platform - Database Migration")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check database connection
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Run migrations in order
            migrate_user_table()
            create_new_tables()
            update_refresh_tokens_table()
            create_indexes()
            update_existing_users()
            
            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Migration failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()