"""
Root conftest.py for pytest - ensures Django is setup for all tests.
"""
import os
import django

# Setup Django before any tests run
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import pytest

# Import all fixtures from tests/conftest.py
pytest_plugins = ['tests.conftest']

