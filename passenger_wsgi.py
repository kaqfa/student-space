import sys
import os

# ============================================
# Passenger WSGI Configuration - Domainesia
# Untuk: exp.fahrifirdaus.my.id
# ============================================

# ============================================
# 1. PATH CONFIGURATION
# ============================================
# Path ke aplikasi Django (folder dengan manage.py)
PROJECT_ROOT = '/home/fahrifir/student-space'

# Path ke Python di virtual environment (yang dibuat cPanel)
VENV_PATH = '/home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/python'

# ============================================
# 2. ACTIVATE VIRTUAL ENVIRONMENT
# ============================================
if sys.executable != VENV_PATH:
    os.execl(VENV_PATH, VENV_PATH, *sys.argv)

# ============================================
# 3. ADD PROJECT TO PATH
# ============================================
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================================
# 4. LOAD ENVIRONMENT VARIABLES
# ============================================
from dotenv import load_dotenv
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path)

# ============================================
# 5. DJANGO SETTINGS MODULE
# ============================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# ============================================
# 6. WSGI APPLICATION
# ============================================
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Log error untuk debugging
    import traceback
    error_msg = f"Error loading WSGI application:\n{traceback.format_exc()}"
    
    error_log = os.path.join(PROJECT_ROOT, 'passenger_error.log')
    with open(error_log, 'w') as f:
        f.write(error_msg)
        f.write(f"\n\nPython executable: {sys.executable}")
        f.write(f"\nPython version: {sys.version}")
        f.write(f"\nPython path: {sys.path}")
        f.write(f"\nProject root: {PROJECT_ROOT}")
    
    raise
