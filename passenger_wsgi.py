import sys
import os

# ============================================
# Passenger WSGI Configuration - Domainesia
# Untuk: exp.fahrifirdaus.my.id
# ============================================
# File ini di: /home/fahrifir/exp.fahrifirdaus.my.id/passenger_wsgi.py

# ============================================
# 1. PATH CONFIGURATION
# ============================================
# Document root (di mana file ini berada)
DOCUMENT_ROOT = '/home/fahrifir/exp.fahrifirdaus.my.id'

# Path ke source code Django (yang di-clone dari GitHub)
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
# Tambahkan source code Django ke Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================================
# 4. LOAD ENVIRONMENT VARIABLES
# ============================================
# Load .env dari source code directory
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
    
    # Log di document root
    error_log = os.path.join(DOCUMENT_ROOT, 'passenger_error.log')
    with open(error_log, 'w') as f:
        f.write(error_msg)
        f.write(f"\n\nPython executable: {sys.executable}")
        f.write(f"\nPython version: {sys.version}")
        f.write(f"\nPython path: {sys.path}")
        f.write(f"\nProject root: {PROJECT_ROOT}")
        f.write(f"\nDocument root: {DOCUMENT_ROOT}")
        f.write(f"\nEnvironment file: {env_path}")
    
    raise
