# Comparison: Docker vs Domainesia

Quick reference untuk memahami perbedaan konfigurasi Docker vs Domainesia production.

## File Structure

### Docker (Local Testing)
```
/var/www/student-space/
├── passenger_wsgi.py       ← Di dalam project root
├── public/                 ← Document root (empty directory)
├── config/
├── apps/
├── staticfiles/
└── media/
```

### Domainesia (Production)
```
/home/fahrifir/
├── student-space/          ← Project root (from GitHub)
│   ├── config/
│   ├── apps/
│   └── ...
├── exp.fahrifirdaus.my.id/ ← Document root (domain folder)
│   ├── .htaccess           ← Apache config here
│   ├── public/             ← Empty, Passenger needs this
│   ├── staticfiles/
│   └── media/
└── virtualenv/             ← cPanel-created venv
    └── exp.fahrifirdaus.my.id/3.12/
```

**Key Difference**: In Domainesia, `passenger_wsgi.py` is in project root, but `.htaccess` is in the domain folder (document root).

## Configuration Comparison

### passenger_wsgi.py

Both Docker and Domainesia use **the same simple style**:

```python
import sys
import os

# Path configuration
PROJECT_ROOT = '/path/to/student-space'
VENV_PATH = '/path/to/venv/bin/python'

# Activate venv
if sys.executable != VENV_PATH:
    os.execl(VENV_PATH, VENV_PATH, *sys.argv)

# Add to path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load environment
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Set settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Get WSGI app
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Apache/Passenger Configuration

**Docker (apache-config.conf):**
```apache
<VirtualHost *:80>
    DocumentRoot /var/www/student-space/public

    PassengerEnabled On
    PassengerAppRoot /var/www/student-space
    PassengerPython /var/www/venv/bin/python3.12
    PassengerStartupFile passenger_wsgi.py
    PassengerAppEnv production

    Alias /static /var/www/student-space/staticfiles
    Alias /media /var/www/student-space/media
</VirtualHost>
```

**Domainesia (.htaccess):**
```apache
PassengerEnabled On
PassengerAppRoot /home/fahrifir/student-space
PassengerPython /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/python
PassengerStartupFile passenger_wsgi.py
PassengerAppEnv production

Alias /static /home/fahrifir/exp.fahrifirdaus.my.id/staticfiles
Alias /media /home/fahrifir/exp.fahrifirdaus.my.id/media
```

**Key Points:**
- Docker uses full VirtualHost config (because we control Apache)
- Domainesia uses simple .htaccess (cPanel injects the VirtualHost)
- Both use the same core Passenger directives
- Paths are different, but structure is identical

## Why This Matters

✅ **Simplified Configuration** = Easier to debug
✅ **Match Production** = If it works in Docker, it works in Domainesia
✅ **Less Complexity** = Fewer things to go wrong
✅ **cPanel-style** = Follows Domainesia best practices

## Path Translation

When moving from Docker to Domainesia, just update paths:

| Component | Docker | Domainesia |
|-----------|--------|------------|
| Project Root | `/var/www/student-space` | `/home/fahrifir/student-space` |
| Document Root | `/var/www/student-space/public` | `/home/fahrifir/exp.fahrifirdaus.my.id` |
| Venv Python | `/var/www/venv/bin/python3.12` | `/home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/python` |
| Static Files | `/var/www/student-space/staticfiles` | `/home/fahrifir/exp.fahrifirdaus.my.id/staticfiles` |
| Media Files | `/var/www/student-space/media` | `/home/fahrifir/exp.fahrifirdaus.my.id/media` |

## Testing Workflow

```bash
# 1. Test in Docker (simplified config)
./docker/quick-start.sh

# 2. Verify it works
curl http://localhost:8080

# 3. Deploy to Domainesia with confidence
# (just update paths in .htaccess and passenger_wsgi.py)
```

## Common Mistakes

❌ **DON'T** add extra directives not in cPanel
❌ **DON'T** use complex Apache config in .htaccess
❌ **DON'T** add verbose logging to passenger_wsgi.py

✅ **DO** keep it simple like the examples above
✅ **DO** match the structure in Domainesia
✅ **DO** test in Docker first before deploying
