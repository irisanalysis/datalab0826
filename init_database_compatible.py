#!/usr/bin/env python3
"""
Database Initialization - Backend Compatible Version
Updated to work with new backend architecture while maintaining compatibility
"""

import os
import sys
import json
import datetime

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

def get_backend_imports():
    """Get database models and functions from backend"""
    try:
        # Try new FastAPI architecture first
        from backend.shared.database.connections.postgres import SessionLocal, init_database
        from backend.shared.database.models.user import User
        from backend.shared.database.models.dataset import DataSource, UserSession
        from backend.shared.utils.security import hash_password
        
        return {
            'architecture': 'fastapi',
            'session_factory': SessionLocal,
            'init_db_func': init_database,
            'User': User,
            'DataSource': DataSource,
            'UserSession': UserSession,
            'hash_password': hash_password
        }
    except ImportError:
        try:
            # Fallback to legacy Flask architecture
            from backend.apps.legacy_flask.main import app, db, User, DataSource, UserSession, hash_password
            
            return {
                'architecture': 'flask',
                'app': app,
                'db': db,
                'User': User,
                'DataSource': DataSource,
                'UserSession': UserSession,
                'hash_password': hash_password
            }
        except ImportError as e:
            print(f"❌ Cannot import from backend: {str(e)}")
            print("💡 Please run from project root directory and ensure backend is properly set up")
            sys.exit(1)

def create_sample_admin_user(backend):
    """Create a sample admin user for testing"""
    print("Creating sample admin user...")
    
    admin_email = "admin@example.com"
    
    if backend['architecture'] == 'fastapi':
        try:
            # FastAPI version
            db_session = backend['session_factory']()
            existing_admin = db_session.query(backend['User']).filter_by(email=admin_email).first()
            
            if existing_admin:
                print(f"✓ Admin user already exists: {admin_email}")
                db_session.close()
                return existing_admin
            
            # Create admin user
            admin_user = backend['User'](
                email=admin_email,
                password_hash=backend['hash_password']("AdminPass123!"),
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
            db_session.close()
            return admin_user
            
        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
            db_session.rollback()
            db_session.close()
            return None
    else:
        try:
            # Flask version - need application context for all operations
            with backend['app'].app_context():
                db_session = backend['db'].session
                existing_admin = backend['User'].query.filter_by(email=admin_email).first()
                
                if existing_admin:
                    print(f"✓ Admin user already exists: {admin_email}")
                    return existing_admin
                
                # Create admin user
                admin_user = backend['User'](
                    email=admin_email,
                    password_hash=backend['hash_password']("AdminPass123!"),
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
                return admin_user
                
        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
            with backend['app'].app_context():
                backend['db'].session.rollback()
            return None

def create_sample_data_sources(user, backend):
    """Create sample data sources for testing"""
    print("Creating sample data sources...")
    
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
    
    if backend['architecture'] == 'fastapi':
        try:
            db_session = backend['session_factory']()
            created_count = 0
            
            for source_data in sample_sources:
                # Check if data source already exists
                existing = db_session.query(backend['DataSource']).filter_by(
                    user_id=user.id, name=source_data["name"]
                ).first()
                
                if not existing:
                    data_source = backend['DataSource'](
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
            
            db_session.close()
            
        except Exception as e:
            print(f"❌ Error creating sample data sources: {str(e)}")
            db_session.rollback()
            db_session.close()
    else:
        try:
            with backend['app'].app_context():
                db_session = backend['db'].session
                created_count = 0
                
                for source_data in sample_sources:
                    # Check if data source already exists
                    existing = backend['DataSource'].query.filter_by(
                        user_id=user.id, name=source_data["name"]
                    ).first()
                    
                    if not existing:
                        data_source = backend['DataSource'](
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
                
        except Exception as e:
            print(f"❌ Error creating sample data sources: {str(e)}")
            with backend['app'].app_context():
                backend['db'].session.rollback()

def initialize_database(backend):
    """Initialize database with tables"""
    print("Initializing database tables...")
    
    try:
        if backend['architecture'] == 'fastapi':
            backend['init_db_func']()
            print("✓ Database tables initialized (FastAPI architecture)")
        else:
            with backend['app'].app_context():
                backend['db'].create_all()
                print("✓ Database tables initialized (Flask architecture)")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False

def main():
    """Main initialization function"""
    print("🚀 AI Data Platform Database Initialization (Compatible Version)")
    print("=" * 60)
    
    # Get backend imports
    backend = get_backend_imports()
    print(f"✅ Using {backend['architecture'].upper()} architecture")
    
    # Initialize database
    if not initialize_database(backend):
        sys.exit(1)
    
    # Create admin user
    admin_user = create_sample_admin_user(backend)
    if not admin_user:
        sys.exit(1)
    
    # Create sample data sources
    create_sample_data_sources(admin_user, backend)
    
    print("\n✅ Database initialization completed successfully!")
    print(f"Admin user: admin@example.com / AdminPass123!")
    print("You can now start the backend server and begin using the platform.")
    print("\nNext steps:")
    print("  - Start backend: ./start_backend.sh")
    print("  - Test API: cd backend && python tests/integration/test_api.py")

if __name__ == "__main__":
    main()