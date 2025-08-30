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
        },
        {
            "name": "Weather API",
            "type": "api",
            "description": "External weather data for correlation analysis",
            "tags": ["weather", "external", "api"],
            "config": {
                "url": "https://api.openweathermap.org/data/2.5/current",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "auth_token": "your_weather_api_key"
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
        db.session.rollback()\n\ndef create_indexes_and_constraints():\n    \"\"\"Create additional database indexes and constraints\"\"\"\n    print(\"Creating database indexes and constraints...\")\n    \n    from sqlalchemy import text\n    \n    indexes_and_constraints = [\n        # Performance indexes\n        \"CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active);\",\n        \"CREATE INDEX IF NOT EXISTS idx_users_org_dept ON users(organization, department);\",\n        \"CREATE INDEX IF NOT EXISTS idx_data_sources_user_type ON data_sources(user_id, type);\",\n        \"CREATE INDEX IF NOT EXISTS idx_data_sources_status_active ON data_sources(status, is_active);\",\n        \"CREATE INDEX IF NOT EXISTS idx_audit_logs_user_date ON audit_logs(user_id, created_at);\",\n        \"CREATE INDEX IF NOT EXISTS idx_audit_logs_action_resource ON audit_logs(action, resource);\",\n        \"CREATE INDEX IF NOT EXISTS idx_user_sessions_user_active ON user_sessions(user_id, is_active);\",\n        \"CREATE INDEX IF NOT EXISTS idx_integrations_provider_user ON integrations(provider, user_id);\",\n        \n        # Partial indexes for better performance\n        \"CREATE INDEX IF NOT EXISTS idx_users_active_only ON users(id) WHERE is_active = true;\",\n        \"CREATE INDEX IF NOT EXISTS idx_data_sources_active_only ON data_sources(id) WHERE is_active = true;\",\n        \"CREATE INDEX IF NOT EXISTS idx_sessions_active_only ON user_sessions(session_id) WHERE is_active = true;\",\n        \n        # Text search indexes (if supported)\n        \"CREATE INDEX IF NOT EXISTS idx_data_sources_name_search ON data_sources USING gin(to_tsvector('english', name));\",\n        \"CREATE INDEX IF NOT EXISTS idx_data_sources_desc_search ON data_sources USING gin(to_tsvector('english', description));\"\n    ]\n    \n    created_count = 0\n    \n    for sql in indexes_and_constraints:\n        try:\n            db.session.execute(text(sql))\n            db.session.commit()\n            created_count += 1\n            print(f\"✓ Created: {sql.split()[5] if len(sql.split()) > 5 else 'constraint'}\")\n        except Exception as e:\n            # Some indexes might already exist or not be supported\n            db.session.rollback()\n            if \"already exists\" not in str(e).lower() and \"does not exist\" not in str(e).lower():\n                print(f\"⚠ Warning: {str(e)}\")\n    \n    print(f\"✓ Successfully created {created_count} indexes/constraints\")\n\ndef display_setup_summary(users, data_sources):\n    \"\"\"Display setup summary\"\"\"\n    print(\"\\n\" + \"=\" * 60)\n    print(\"📋 Database Setup Summary\")\n    print(\"=\" * 60)\n    \n    print(f\"\\n👥 Users Created: {len(users)}\")\n    for user in users:\n        print(f\"   - {user.email} ({user.role}) - Password: {'AdminPass123!' if user.role == 'admin' else 'AnalystPass123!' if user.role == 'analyst' else 'ViewerPass123!'}\")\n    \n    print(f\"\\n🗃️  Data Sources Created: {len(data_sources)}\")\n    for ds in data_sources:\n        print(f\"   - {ds.name} ({ds.type})\")\n    \n    print(f\"\\n📊 Database Tables:\")\n    from sqlalchemy import inspect\n    inspector = inspect(db.engine)\n    tables = inspector.get_table_names()\n    \n    for table in sorted(tables):\n        print(f\"   - {table}\")\n    \n    print(f\"\\n🚀 Setup Complete! You can now:\")\n    print(f\"   1. Start the server: python main.py\")\n    print(f\"   2. Test the API: python test_saas_api.py\")\n    print(f\"   3. Access the admin panel with admin@example.com\")\n    print(f\"   4. Create and test data source connections\")\n\ndef main():\n    \"\"\"Main initialization function\"\"\"\n    print(\"=\" * 60)\n    print(\"🚀 SaaS Data Analysis Platform - Database Initialization\")\n    print(\"=\" * 60)\n    \n    with app.app_context():\n        try:\n            # Test database connection\n            db.session.execute(text('SELECT 1'))\n            print(\"✓ Database connection successful\")\n            \n            # Create all tables\n            print(\"\\n📋 Creating database tables...\")\n            db.create_all()\n            print(\"✓ All database tables created\")\n            \n            # Create sample data\n            users = []\n            \n            # Create admin user\n            admin_user = create_sample_admin_user()\n            if admin_user:\n                users.append(admin_user)\n            \n            # Create sample users\n            sample_users = create_sample_users()\n            users.extend(sample_users)\n            \n            # Create data sources\n            data_sources = create_sample_data_sources(users)\n            \n            # Create audit logs\n            create_sample_audit_logs(users)\n            \n            # Create indexes and constraints\n            create_indexes_and_constraints()\n            \n            # Display summary\n            display_setup_summary(users, data_sources)\n            \n            print(\"\\n\" + \"=\" * 60)\n            print(\"✅ Database initialization completed successfully!\")\n            print(\"=\" * 60)\n            \n        except Exception as e:\n            print(f\"\\n❌ Database initialization failed: {str(e)}\")\n            db.session.rollback()\n            sys.exit(1)\n\nif __name__ == \"__main__\":\n    from sqlalchemy import text\n    main()