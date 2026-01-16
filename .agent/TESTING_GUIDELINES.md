# Testing Guidelines for Bank Soal Django

## Overview
This document outlines the testing strategy and best practices for the Bank Soal Django project.

---

## Testing Strategy

### 1. **Functional Testing** → Use E2E with Python Playwright

**When to use:**
- Testing user workflows and interactions
- Verifying application functionality
- Automated regression testing
- Testing forms, navigation, and data flow
- Validating business logic from user perspective

**Why Playwright:**
- ⚡ **Fast:** ~2 seconds per test (vs 30+ seconds manual)
- 🔄 **Repeatable:** Consistent results every time
- 🤖 **Automated:** Can run in CI/CD pipeline
- 🎯 **Reliable:** Headless mode, no UI flakiness
- 📊 **Data-driven:** Uses test data from `setup_test_data.py`

**Example command:**
```bash
# Run specific functional test
pytest tests/e2e/test_student_flow.py::test_student_can_submit_quiz -v

# Run all quiz-related tests
pytest tests/e2e/ -m quiz -v

# Run in headed mode for debugging
pytest tests/e2e/ --headed -v
```

**Test locations:**
- `tests/e2e/test_student_flow.py` - Student scenarios
- `tests/e2e/test_parent_flow.py` - Parent scenarios
- `tests/conftest.py` - Shared fixtures

---

### 2. **Visual/UI Testing** → Use Antigravity Browser Feature

**When to use:**
- Reviewing new UI designs
- Visual inspection of layout/styling
- Checking responsive design
- Verifying CSS changes
- Manual exploration of features
- Demonstrating features to stakeholders

**Why Antigravity Browser:**
- 👁️ **Visual:** See the actual UI rendering
- 🎨 **Design review:** Perfect for CSS/layout checks
- 📸 **Screenshots:** Automatically recorded
- 🎥 **Video recording:** All interactions saved as WebP
- 🖱️ **Interactive:** Real browser experience

**Example usage:**
```
User: "Please check if the new quiz layout looks good on mobile"
Assistant: [Uses browser_subagent to navigate and capture screenshots]
```

---

## Testing Workflow

### For Bug Fixes

1. **Reproduce issue** using E2E test (write failing test first)
2. **Fix the code**
3. **Verify fix** by running the test (should pass)
4. **Commit** both fix and test together

Example:
```bash
# Write test that reproduces bug
pytest tests/e2e/test_student_flow.py::test_quiz_options_visible -v
# Fix code
# Verify fix
pytest tests/e2e/test_student_flow.py::test_quiz_options_visible -v
```

### For New Features

1. **Write E2E tests** for user scenarios first (TDD approach)
2. **Implement feature**
3. **Run tests** to verify implementation
4. **Use browser** for visual review of UI
5. **Iterate** until tests pass and UI looks good

---

## Test Data Management

### Setup Test Data
```bash
python manage.py setup_test_data
```

This creates:
- Test users (parent, students, admin)
- Subjects, topics, questions
- Quizzes and quiz sessions
- Sample analytics data

### Test Credentials
See `tests/E2E_TESTING_SUMMARY.md` for full list.

Quick reference:
- **Parent:** `orangtua` / `parent123`
- **Student Grade 4:** `siswa4` / `siswa123`
- **Admin:** `admin` / `admin123`

---

## Best Practices

### ✅ DO

- **Write E2E tests for critical user flows**
  - Login/logout
  - Quiz taking (full flow)
  - Quiz submission
  - Parent proxy mode
  
- **Use meaningful test names**
  ```python
  def test_student_can_see_quiz_options()  # ✅ Clear
  def test_quiz()                           # ❌ Vague
  ```

- **Keep tests independent**
  - Each test should run standalone
  - Use fixtures for setup/teardown
  
- **Use proper waits**
  ```python
  page.wait_for_load_state("networkidle")  # ✅ Proper wait
  time.sleep(5)                             # ❌ Brittle
  ```

- **Test with realistic data**
  - Use `setup_test_data.py` for consistent test data
  
### ❌ DON'T

- **Don't use browser_subagent for functional testing**
  - Too slow (~30s vs ~2s with Playwright)
  - Not suitable for CI/CD
  
- **Don't test styling with E2E**
  - E2E tests should focus on functionality
  - Use browser for visual review
  
- **Don't hardcode test data inline**
  - Use fixtures and test data setup
  
- **Don't skip error handling in tests**
  - Tests should be robust and clear about failures

---

## Common Testing Scenarios

### Testing Quiz Flow
```bash
# Full quiz flow (login → take → submit → results)
pytest tests/e2e/test_student_flow.py -k "quiz" -v
```

### Testing Parent Proxy Mode
```bash
pytest tests/e2e/test_parent_flow.py -k "proxy" -v
```

### Visual Review of New UI
```
Ask Antigravity: "Please show me the new quiz interface for student siswa4"
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run E2E Tests
  run: |
    python manage.py setup_test_data
    python manage.py runserver &
    sleep 5
    pytest tests/e2e/ -v --maxfail=5
```

---

## Debugging Failed Tests

1. **Run with visible browser:**
   ```bash
   pytest tests/e2e/test_name.py --headed -v
   ```

2. **Slow down execution:**
   ```bash
   pytest tests/e2e/test_name.py --headed --slowmo 1000 -v
   ```

3. **Use Playwright inspector:**
   ```bash
   PWDEBUG=1 pytest tests/e2e/test_name.py::test_function -v
   ```

4. **Add debug screenshots in test:**
   ```python
   page.screenshot(path="debug_screenshot.png")
   ```

---

## Summary

| Task | Use This | Why |
|------|----------|-----|
| **Functional testing** | Playwright E2E | Fast, automated, reliable |
| **Visual review** | Antigravity Browser | Interactive, visual, recorded |
| **Bug reproduction** | Playwright test | Reproducible, automated |
| **UI design review** | Antigravity Browser | See actual rendering |
| **CI/CD pipeline** | Playwright E2E | Headless, fast, stable |
| **Feature demo** | Antigravity Browser | Visual, recorded videos |

---

## Resources

- **E2E Test Documentation:** `tests/e2e/README.md`
- **Test Summary:** `tests/E2E_TESTING_SUMMARY.md`
- **Test Fixtures:** `tests/conftest.py`
- **Test Data Setup:** `apps/core/management/commands/setup_test_data.py`

---

**Last Updated:** 2026-01-15
**Maintained by:** Development Team
