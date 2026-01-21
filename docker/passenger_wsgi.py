import sys
import os

# ============================================
# Passenger WSGI Configuration - Docker Local Testing
# Simulates Domainesia cPanel environment
# ============================================

# ============================================
# 1. PATH CONFIGURATION
# ============================================
# Project root (where Django app lives)
PROJECT_ROOT = '/var/www/student-space'

# Virtual environment Python path
VENV_PATH = '/var/www/venv/bin/python3.12'

# ============================================
# 2. ACTIVATE VIRTUAL ENVIRONMENT
# ============================================
# This simulates cPanel's virtualenv activation
if sys.executable != VENV_PATH:
    os.execl(VENV_PATH, VENV_PATH, *sys.argv)

# ============================================
# 3. ADD PROJECT TO PATH
# ============================================
# Add Django project to Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ============================================
# 4. LOAD ENVIRONMENT VARIABLES
# ============================================
# Load .env file from project root
from dotenv import load_dotenv

env_path = os.path.join(PROJECT_ROOT, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}", file=sys.stderr)
else:
    print(f"⚠ Warning: .env file not found at {env_path}", file=sys.stderr)
    print("  Using default/system environment variables", file=sys.stderr)

# ============================================
# 5. DJANGO SETTINGS MODULE
# ============================================
# Use production settings (as in Domainesia)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# ============================================
# 6. DEBUGGING INFORMATION
# ============================================
# Print startup info (will appear in Passenger logs)
print("=" * 60, file=sys.stderr)
print("Student Space - Passenger Startup", file=sys.stderr)
print("=" * 60, file=sys.stderr)
print(f"Python executable: {sys.executable}", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Project root: {PROJECT_ROOT}", file=sys.stderr)
print(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
print(f"Environment file: {env_path}", file=sys.stderr)
print(f"Debug mode: {os.environ.get('DEBUG', 'False')}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# ============================================
# 7. WSGI APPLICATION
# ============================================
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✓ WSGI application loaded successfully", file=sys.stderr)

except Exception as e:
    import traceback
    error_msg = f"ERROR loading WSGI application:\n{traceback.format_exc()}"

    print("=" * 60, file=sys.stderr)
    print("FATAL ERROR", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(error_msg, file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("Python path:", file=sys.stderr)
    for p in sys.path:
        print(f"  - {p}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Also log to file for persistence
    log_file = os.path.join(PROJECT_ROOT, 'logs', 'passenger_error.log')
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            f.write(error_msg)
            f.write(f"\n\nPython executable: {sys.executable}")
            f.write(f"\nPython version: {sys.version}")
            f.write(f"\nProject root: {PROJECT_ROOT}")
            f.write(f"\nSettings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
            f.write("\n\nPython path:\n")
            for p in sys.path:
                f.write(f"  - {p}\n")
        print(f"Error details written to: {log_file}", file=sys.stderr)
    except Exception as log_error:
        print(f"Could not write error log: {log_error}", file=sys.stderr)

    raise
