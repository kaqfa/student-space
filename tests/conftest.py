"""
Pytest configuration and fixtures for E2E testing.
"""
import os
import django

# Setup Django before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pytest
from playwright.sync_api import Page, Browser, BrowserContext


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return "http://127.0.0.1:8000"


@pytest.fixture
def test_users():
    """Return test user credentials from setup_test_data"""
    return {
        'admin': {'username': 'admin', 'password': 'admin123'},
        'parent': {'username': 'orangtua', 'password': 'parent123'},
        'student_grade3': {'username': 'siswa3', 'password': 'siswa123'},
        'student_grade4': {'username': 'siswa4', 'password': 'siswa123'},
        'student_grade5': {'username': 'siswa5', 'password': 'siswa123'},
        'student_grade6': {'username': 'siswa6', 'password': 'siswa123'},
    }


@pytest.fixture
def login_as_parent(page: Page, base_url: str, test_users: dict):
    """Helper fixture to login as parent"""
    def _login():
        page.goto(f"{base_url}/accounts/login/")
        page.fill("input[name='username']", test_users['parent']['username'])
        page.fill("input[name='password']", test_users['parent']['password'])
        page.click("button[type='submit']")
        page.wait_for_url(f"{base_url}/**")  # Wait for redirect after login
        return page
    return _login


@pytest.fixture
def login_as_student(page: Page, base_url: str, test_users: dict):
    """Helper fixture to login as student (default: grade 4)"""
    def _login(grade: int = 4):
        page.goto(f"{base_url}/accounts/login/")
        page.fill("input[name='username']", test_users[f'student_grade{grade}']['username'])
        page.fill("input[name='password']", test_users[f'student_grade{grade}']['password'])
        page.click("button[type='submit']")
        page.wait_for_url(f"{base_url}/**")  # Wait for redirect after login
        return page
    return _login


@pytest.fixture
def logged_in_parent_page(page: Page, login_as_parent):
    """Fixture that returns a page already logged in as parent"""
    login_as_parent()
    return page


@pytest.fixture
def logged_in_student_page(page: Page, login_as_student):
    """Fixture that returns a page already logged in as student (grade 4)"""
    login_as_student(grade=4)
    return page
