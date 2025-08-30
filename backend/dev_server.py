#!/usr/bin/env python3
"""
Development server launcher for the AI Data Platform Backend
"""
import os
import sys
import subprocess
import signal
import time
from concurrent.futures import ThreadPoolExecutor

# Service configurations
SERVICES = {
    'legacy_flask': {
        'port': 8000,
        'path': 'apps/legacy_flask/main.py',
        'name': 'Legacy Flask API'
    },
    'data_service': {
        'port': 8001,
        'path': 'apps/data_service/main.py',
        'name': 'Data Service'
    },
    # Add other services as they are implemented
}

def run_service(service_name, config):
    """Run a single service"""
    print(f"🚀 Starting {config['name']} on port {config['port']}...")
    
    env = os.environ.copy()
    env['PORT'] = str(config['port'])
    
    try:
        if service_name == 'legacy_flask':
            # Flask service
            cmd = [sys.executable, config['path']]
        else:
            # FastAPI service with uvicorn
            module_path = config['path'].replace('/', '.').replace('.py', '')
            cmd = [
                sys.executable, '-m', 'uvicorn', 
                f"{module_path}:app",
                '--host', '0.0.0.0',
                '--port', str(config['port']),
                '--reload',
                '--reload-dir', '.'
            ]
        
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Wait for process to finish or be interrupted
        process.wait()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping {config['name']}...")
        if 'process' in locals():
            process.terminate()
            process.wait()
    except Exception as e:
        print(f"❌ Error running {config['name']}: {str(e)}")

def main():
    """Main development server launcher"""
    print("🌟 AI Data Platform Backend Development Server")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_file):
        env_example = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.example')
        if os.path.exists(env_example):
            print("⚠️  No .env file found. Please copy .env.example to .env and configure it.")
            print(f"   cp {env_example} {env_file}")
        else:
            print("⚠️  No .env file found. Please create one with the required configuration.")
        return
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    except ImportError:
        print("⚠️  python-dotenv not installed. Please install requirements.txt")
        return
    
    services_to_run = []
    
    if len(sys.argv) > 1:
        # Run specific services
        requested_services = sys.argv[1:]
        for service in requested_services:
            if service in SERVICES:
                services_to_run.append((service, SERVICES[service]))
            else:
                print(f"❌ Unknown service: {service}")
                print(f"Available services: {', '.join(SERVICES.keys())}")
                return
    else:
        # Run all services
        services_to_run = list(SERVICES.items())
    
    if not services_to_run:
        print("No services to run.")
        return
    
    print(f"🎯 Running {len(services_to_run)} service(s):")
    for service_name, config in services_to_run:
        print(f"   - {config['name']} → http://localhost:{config['port']}")
    print()
    
    # Run services concurrently
    try:
        with ThreadPoolExecutor(max_workers=len(services_to_run)) as executor:
            futures = []
            for service_name, config in services_to_run:
                future = executor.submit(run_service, service_name, config)
                futures.append(future)
            
            # Wait for all services to complete
            for future in futures:
                future.result()
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        # The individual service handlers will clean up
    
    print("✅ All services stopped.")

if __name__ == "__main__":
    main()