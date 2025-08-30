#!/usr/bin/env python3
"""
SaaS Data Analysis Platform - Database Initialization
Complete database setup with sample data for development and testing
"""

import os
import sys
import json
import datetime
# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from apps.legacy_flask.main import app, db, User, DataSource, UserSession, Integration, AuditLog
from apps.legacy_flask.main import hash_password, encrypt_config
from sqlalchemy import text

def create_sample_admin_user():
    """Create a sample admin user for testing"""
    print("Creating sample admin user...")
    
    try:
        # Check if admin user already exists
        admin_email = "admin@example.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print(f"✓ Admin user already exists: {admin_email}")
            return existing_admin
        
        # Create admin user
        admin_user = User(
            email=admin_email,
            password_hash=hash_password("AdminPass123!"),
            first_name="Admin",
            last_name="User", 
            role="admin",
            department="IT",
            organization="SaaS Platform",
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
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✓ Created admin user: {admin_email} (Password: AdminPass123!)")
        return admin_user
        
    except Exception as e:
        print(f"✗ Failed to create admin user: {str(e)}")
        db.session.rollback()
        return None

def create_sample_users():
    """Create sample users for testing"""
    print("Creating sample users...")
    
    sample_users = [
        {
            "email": "analyst@example.com",
            "password": "AnalystPass123!",
            "first_name": "Jane",
            "last_name": "Smith",
            "role": "analyst",
            "department": "Data Analytics",
            "organization": "SaaS Platform"
        },
        {
            "email": "viewer@example.com", 
            "password": "ViewerPass123!",
            "first_name": "Bob",
            "last_name": "Johnson",
            "role": "viewer",
            "department": "Marketing",
            "organization": "SaaS Platform"
        }
    ]
    
    created_users = []
    
    for user_data in sample_users:
        try:
            existing_user = User.query.filter_by(email=user_data["email"]).first()
            
            if existing_user:
                print(f"✓ User already exists: {user_data['email']}")
                created_users.append(existing_user)
                continue
            
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                department=user_data["department"],
                organization=user_data["organization"],
                is_active=True,
                timezone="UTC",
                language="en",
                preferences=json.dumps({
                    "theme": "light",
                    "notifications": True,
                    "default_chart_type": "line"
                })
            )
            
            db.session.add(user)
            db.session.commit()
            
            created_users.append(user)
            print(f"✓ Created user: {user_data['email']} (Password: {user_data['password']})")
            
        except Exception as e:
            print(f"✗ Failed to create user {user_data['email']}: {str(e)}")
            db.session.rollback()
    
    return created_users

def create_sample_data_sources(users):
    """Create sample data sources"""
    print("Creating sample data sources...")
    
    if not users:
        print("✗ No users available for data sources")
        return []
    
    admin_user = next((u for u in users if u.role == 'admin'), users[0])
    
    sample_data_sources = [
        {
            "name": "Sales Database",
            "type": "postgresql",
            "description": "Main sales database with customer and transaction data",
            "tags": ["sales", "customers", "transactions"],
            "config": {
                "host": "localhost",
                "port": 5432,
                "database": "sales_db",
                "username": "sales_user",
                "password": "sales_password"
            },
            "status": "pending"
        },
        {
            "name": "Marketing Analytics",
            "type": "mysql",
            "description": "Marketing campaign performance data",
            "tags": ["marketing", "campaigns", "analytics"],
            "config": {
                "host": "mysql.example.com",
                "port": 3306,
                "database": "marketing",
                "username": "marketing_user",
                "password": "marketing_password"
            },
            "status": "pending"
        },
        {
            "name": "Customer Survey Data",
            "type": "csv",
            "description": "Monthly customer satisfaction surveys",
            "tags": ["survey", "customer", "satisfaction"],
            "config": {
                "file_path": "/data/surveys/customer_survey_2024.csv",
                "delimiter": ",",
                "encoding": "utf-8"
            },
            "status": "pending"
        }
    ]
    
    created_sources = []
    
    for ds_data in sample_data_sources:
        try:
            # Encrypt configuration
            encrypted_config = encrypt_config(ds_data["config"])
            
            data_source = DataSource(
                user_id=admin_user.id,
                name=ds_data["name"],
                type=ds_data["type"],
                config=encrypted_config,
                description=ds_data["description"],
                tags=json.dumps(ds_data["tags"]),
                status=ds_data["status"],
                is_active=True
            )
            
            db.session.add(data_source)
            db.session.commit()
            
            created_sources.append(data_source)
            print(f"✓ Created data source: {ds_data['name']} (Type: {ds_data['type']})")
            
        except Exception as e:
            print(f"✗ Failed to create data source {ds_data['name']}: {str(e)}")
            db.session.rollback()
    
    return created_sources

def create_sample_audit_logs(users):
    """Create sample audit log entries"""
    print("Creating sample audit log entries...")
    
    if not users:
        print("✗ No users available for audit logs")
        return
    
    sample_actions = [
        ("login_success", "user", "User logged in successfully"),
        ("create_data_source", "data_source", "Created new data source"),
        ("update_profile", "user", "Updated user profile"),
        ("query_data_source", "data_source", "Queried data from source"),
        ("logout", "user", "User logged out")
    ]
    
    created_logs = 0
    
    for i, user in enumerate(users):
        for j, (action, resource, description) in enumerate(sample_actions):
            try:
                log_entry = AuditLog(
                    user_id=user.id,
                    action=action,
                    resource=resource,
                    resource_id=str(user.id) if resource == "user" else str(j+1),
                    ip_address=f"192.168.1.{100+i}",
                    user_agent="Mozilla/5.0 (Test Browser)",
                    endpoint=f"/api/{resource}",
                    method="POST" if "create" in action else "GET",
                    details=json.dumps({"description": description, "test_data": True}),
                    status="success",
                    created_at=datetime.datetime.utcnow() - datetime.timedelta(days=j, hours=i)
                )
                
                db.session.add(log_entry)
                created_logs += 1
                
            except Exception as e:
                print(f"✗ Failed to create audit log: {str(e)}")
                db.session.rollback()
                continue
    
    try:
        db.session.commit()
        print(f"✓ Created {created_logs} sample audit log entries")
    except Exception as e:
        print(f"✗ Failed to commit audit logs: {str(e)}")
        db.session.rollback()

def display_setup_summary(users, data_sources):
    """Display setup summary"""
    print("\n" + "=" * 60)
    print("📋 Database Setup Summary")
    print("=" * 60)
    
    print(f"\n👥 Users Created: {len(users)}")
    for user in users:
        password_hint = {
            'admin': 'AdminPass123!',
            'analyst': 'AnalystPass123!',
            'viewer': 'ViewerPass123!'
        }.get(user.role, 'Unknown')
        print(f"   - {user.email} ({user.role}) - Password: {password_hint}")
    
    print(f"\n🗃️  Data Sources Created: {len(data_sources)}")
    for ds in data_sources:
        print(f"   - {ds.name} ({ds.type})")
    
    print(f"\n📊 Database Tables:")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    for table in sorted(tables):
        print(f"   - {table}")
    
    print(f"\n🚀 Setup Complete! You can now:")
    print(f"   1. Start the server: python main.py")
    print(f"   2. Test the API: python test_saas_api.py")
    print(f"   3. Access the admin panel with admin@example.com")
    print(f"   4. Create and test data source connections")

def main():
    """Main initialization function"""
    print("=" * 60)
    print("🚀 SaaS Data Analysis Platform - Database Initialization")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Create all tables
            print("\n📋 Creating database tables...")
            db.create_all()
            print("✓ All database tables created")
            
            # Create sample data
            users = []
            
            # Create admin user
            admin_user = create_sample_admin_user()
            if admin_user:
                users.append(admin_user)
            
            # Create sample users
            sample_users = create_sample_users()
            users.extend(sample_users)
            
            # Create data sources
            data_sources = create_sample_data_sources(users)
            
            # Create audit logs
            create_sample_audit_logs(users)
            
            # Display summary
            display_setup_summary(users, data_sources)
            
            print("\n" + "=" * 60)
            print("✅ Database initialization completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Database initialization failed: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    main()