import sys
import os

# ============================================
# Passenger WSGI Configuration - Docker
# Simple version matching Domainesia cPanel style
# ============================================

# Path configuration
PROJECT_ROOT = '/var/www/student-space'
VENV_PATH = '/var/www/venv/bin/python3.12'

# Activate virtual environment
if sys.executable != VENV_PATH:
    os.execl(VENV_PATH, VENV_PATH, *sys.argv)

# Add project to Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Get WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Log error untuk debugging
    import traceback
    log_file = os.path.join(PROJECT_ROOT, 'passenger_error.log')
    with open(log_file, 'w') as f:
        f.write(f"Error loading WSGI application:\n{traceback.format_exc()}")
        f.write(f"\n\nPython executable: {sys.executable}")
        f.write(f"\nProject root: {PROJECT_ROOT}")
        f.write(f"\nEnvironment file: {env_path}")
    raise
