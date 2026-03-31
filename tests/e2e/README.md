# E2E Testing with Playwright

This directory contains end-to-end tests for the Bank Soal Django application using Playwright.

## Setup

### 1. Install Dependencies
```bash
pip install pytest-playwright pytest-django
playwright install chromium
```

### 2. Prepare Test Data
Make sure you have test data in your database:
```bash
python manage.py setup_test_data
```

This creates:
- **Parent user:** `orangtua` / `parent123`
- **Students:** `siswa3`, `siswa4`, `siswa5`, `siswa6` / `siswa123`
- **Admin:** `admin` / `admin123`
- Sample quizzes, questions, and quiz sessions

### 3. Run Development Server
Tests expect the server to be running on `http://127.0.0.1:8000`:
```bash
python manage.py runserver
```

## Running Tests

### Run All E2E Tests
```bash
pytest tests/e2e/ -v
```

### Run Specific Test Categories
```bash
# Parent flow tests only
pytest tests/e2e/ -m parent -v

# Student flow tests only
pytest tests/e2e/ -m student -v

# Quiz-related tests only
pytest tests/e2e/ -m quiz -v
```

### Run Specific Test File
```bash
# Parent tests
pytest tests/e2e/test_parent_flow.py -v

# Student tests
pytest tests/e2e/test_student_flow.py -v
```

### Run Single Test
```bash
pytest tests/e2e/test_student_flow.py::test_student_can_see_quiz_options -v
```

### Run with Browser Visible (Headed Mode)
By default, tests run in headless mode. To see the browser:
```bash
pytest tests/e2e/ --headed -v
```

### Run with Slow Motion (for debugging)
```bash
pytest tests/e2e/ --headed --slowmo 1000 -v
```
This adds 1 second delay between actions.

### Generate Test Report
```bash
pytest tests/e2e/ --html=report.html --self-contained-html
```

## Test Structure

### Test Files
- `test_parent_flow.py` - Tests for parent user scenarios
- `test_student_flow.py` - Tests for student user scenarios

### Common Fixtures (in `tests/conftest.py`)
- `base_url` - Application base URL
- `test_users` - Dictionary of test user credentials
- `login_as_parent` - Helper to log in as parent
- `login_as_student` - Helper to log in as student
- `logged_in_parent_page` - Pre-authenticated parent page
- `logged_in_student_page` - Pre-authenticated student page

## Test Markers

Custom pytest markers for organizing tests:

- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.parent` - Parent user flow tests
- `@pytest.mark.student` - Student user flow tests
- `@pytest.mark.quiz` - Quiz functionality tests

## Writing New Tests

### Example Test Structure
```python
@pytest.mark.e2e
@pytest.mark.student
@pytest.mark.quiz
def test_student_can_answer_quiz(logged_in_student_page: Page, base_url: str):
    """Test that student can answer quiz questions"""
    page = logged_in_student_page
    
    # Navigate to quiz
    page.goto(f"{base_url}/quizzes/student/")
    
    # Interact with page
    page.click("a:has-text('Mulai')")
    
    # Assert expected behavior
    expect(page.locator("input[type='radio']")).to_be_visible()
```

## Debugging Failed Tests

### 1. Take Screenshots
```python
page.screenshot(path="debug_screenshot.png")
```

### 2. Enable Trace Recording
```bash
pytest tests/e2e/ --tracing on
```

### 3. Use Playwright Inspector
```bash
PWDEBUG=1 pytest tests/e2e/test_student_flow.py::test_name -v
```

### 4. Check Browser Console Logs
```python
page.on("console", lambda msg: print(msg.text))
```

## CI/CD Integration

For GitHub Actions or similar:

```yaml
- name: Install Playwright
  run: |
    pip install pytest-playwright
    playwright install --with-deps chromium

- name: Run E2E Tests
  run: |
    python manage.py setup_test_data
    python manage.py runserver &
    sleep 5
    pytest tests/e2e/ -v
```

## Best Practices

1. **Use data-testid attributes** for reliable selectors
2. **Wait for elements** instead of using sleep()
3. **Clean up test data** after tests if needed
4. **Use fixtures** for common setup/teardown
5. **Keep tests independent** - each test should run standalone
6. **Use meaningful test names** that describe the scenario

## Troubleshooting

### Server not running
Make sure Django dev server is running on port 8000.

### Test data missing
Run `python manage.py setup_test_data` to recreate test data.

### Browser not found
Run `playwright install chromium` to download browser binaries.

### Tests timing out
Increase timeout in conftest.py or use `page.wait_for_load_state("networkidle")`.
