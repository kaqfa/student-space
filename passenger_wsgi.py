import sys
import os

# ============================================
# Passenger WSGI Configuration
# Berlaku untuk: Docker lokal & Domainesia cPanel
# ============================================

# ============================================
# 1. PATH CONFIGURATION
# ============================================
# Auto-detect lokasi project dari posisi file ini
# Docker:      /var/www/student-space
# Domainesia:  /home/<user>/student-space
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ============================================
# 2. ADD PROJECT TO PATH
# ============================================
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================================
# 3. LOAD ENVIRONMENT VARIABLES
# ============================================
# Load .env dari direktori project
from dotenv import load_dotenv
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path)

# ============================================
# 4. DJANGO SETTINGS MODULE
# ============================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# ============================================
# 5. WSGI APPLICATION
# ============================================
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    import traceback
    error_msg = f"Error loading WSGI application:\n{traceback.format_exc()}"

    error_log = os.path.join(PROJECT_ROOT, 'passenger_error.log')
    with open(error_log, 'w') as f:
        f.write(error_msg)
        f.write(f"\n\nPython executable: {sys.executable}")
        f.write(f"\nPython version: {sys.version}")
        f.write(f"\nPython path: {sys.path}")
        f.write(f"\nProject root: {PROJECT_ROOT}")
        f.write(f"\nEnvironment file: {env_path}")

    raise
