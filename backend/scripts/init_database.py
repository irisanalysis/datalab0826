#!/usr/bin/env python3
"""
Backend Database Initialization Script
Migrated from root init_saas_database_fixed.py
"""

import os
import sys
import json
import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try importing from new architecture
    from shared.database.connections.postgres import get_db, init_database
    from shared.database.models.user import User  
    from shared.database.models.dataset import DataSource
    from shared.utils.security import hash_password
    NEW_ARCHITECTURE = True
except ImportError:
    # Fallback to legacy Flask app
    try:
        from apps.legacy_flask.main import app, db, User, DataSource, hash_password
        NEW_ARCHITECTURE = False
        print("⚠️  Using legacy Flask architecture")
    except ImportError:
        print("❌ Cannot import database models. Please run from backend directory.")
        sys.exit(1)

def create_sample_admin_user():
    """Create a sample admin user for testing"""
    print("Creating sample admin user...")
    
    try:
        admin_email = "admin@example.com"
        
        if NEW_ARCHITECTURE:
            # Use SQLAlchemy session directly
            from shared.database.connections.postgres import SessionLocal
            db_session = SessionLocal()
            existing_admin = db_session.query(User).filter_by(email=admin_email).first()
        else:
            # Use Flask-SQLAlchemy
            existing_admin = User.query.filter_by(email=admin_email).first()
            db_session = db.session
        
        if existing_admin:
            print(f"✓ Admin user already exists: {admin_email}")
            if NEW_ARCHITECTURE:
                db_session.close()
            return existing_admin
        
        # Create admin user
        admin_user = User(
            email=admin_email,
            password_hash=hash_password("AdminPass123!"),
            first_name="Admin",
            last_name="User", 
            role="admin",
            department="IT",
            organization="AI Data Platform",
            is_active=True,
            timezone="UTC",
            language="en",
            preferences=json.dumps({
                "theme": "light",
                "notifications": True,
                "dashboard_layout": "grid",
                "auto_save": True
            })
        )
        
        db_session.add(admin_user)
        db_session.commit()
        
        print(f"✓ Created admin user: {admin_email} (Password: AdminPass123!)")
        
        if NEW_ARCHITECTURE:
            db_session.close()
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        if NEW_ARCHITECTURE:
            db_session.rollback()
            db_session.close()
        else:
            db_session.rollback()
        return None

def create_sample_data_sources(user):
    """Create sample data sources for testing"""
    print("Creating sample data sources...")
    
    try:
        if NEW_ARCHITECTURE:
            from shared.database.connections.postgres import SessionLocal
            db_session = SessionLocal()
        else:
            db_session = db.session
        
        sample_sources = [
            {
                "name": "PostgreSQL Demo",
                "type": "postgresql",
                "description": "Sample PostgreSQL database connection",
                "config": json.dumps({
                    "host": "localhost",
                    "port": 5432,
                    "database": "demo_db",
                    "username": "demo_user"
                }),
                "tags": json.dumps(["demo", "postgresql", "database"])
            },
            {
                "name": "CSV Sample Data",
                "type": "csv",
                "description": "Sample CSV file data source",
                "config": json.dumps({
                    "file_path": "/data/sample.csv",
                    "delimiter": ",",
                    "encoding": "utf-8"
                }),
                "tags": json.dumps(["demo", "csv", "file"])
            },
            {
                "name": "API Data Source",
                "type": "api",
                "description": "RESTful API data source",
                "config": json.dumps({
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "auth_type": "bearer"
                }),
                "tags": json.dumps(["demo", "api", "rest"])
            }
        ]
        
        created_count = 0
        for source_data in sample_sources:
            # Check if data source already exists
            existing = db_session.query(DataSource).filter_by(
                user_id=user.id, 
                name=source_data["name"]
            ).first() if NEW_ARCHITECTURE else DataSource.query.filter_by(
                user_id=user.id, 
                name=source_data["name"]
            ).first()
            
            if not existing:
                data_source = DataSource(
                    user_id=user.id,
                    **source_data
                )
                db_session.add(data_source)
                created_count += 1
                print(f"  ✓ Created: {source_data['name']}")
            else:
                print(f"  ⚠️  Already exists: {source_data['name']}")
        
        if created_count > 0:
            db_session.commit()
            print(f"✓ Created {created_count} sample data sources")
        
        if NEW_ARCHITECTURE:
            db_session.close()
            
    except Exception as e:
        print(f"❌ Error creating sample data sources: {str(e)}")
        if NEW_ARCHITECTURE:
            db_session.rollback()
            db_session.close()
        else:
            db_session.rollback()

def initialize_database():
    """Initialize database with tables"""
    print("Initializing database tables...")
    
    try:
        if NEW_ARCHITECTURE:
            init_database()
            print("✓ Database tables initialized (FastAPI architecture)")
        else:
            with app.app_context():
                db.create_all()
                print("✓ Database tables initialized (Flask architecture)")
                
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False
    
    return True

def main():
    """Main initialization function"""
    print("🚀 AI Data Platform Database Initialization")
    print("=" * 50)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Create admin user
    admin_user = create_sample_admin_user()
    if not admin_user:
        sys.exit(1)
    
    # Create sample data sources
    create_sample_data_sources(admin_user)
    
    print("\n✅ Database initialization completed successfully!")
    print(f"Admin user: admin@example.com / AdminPass123!")
    print("You can now start the backend server and begin using the platform.")

if __name__ == "__main__":
    main()