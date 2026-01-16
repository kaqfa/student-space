# Testing Quick Reference

## Decision Tree

```
Need to test something?
│
├─ Is it about FUNCTIONALITY?
│  └─ ✅ Use Playwright E2E
│     └─ pytest tests/e2e/ -v
│
└─ Is it about VISUAL/UI?
   └─ ✅ Use Antigravity Browser
      └─ browser_subagent tool
```

## When to Use What

### Use Playwright E2E ⚡
- ✅ Testing user workflows
- ✅ Verifying form submissions
- ✅ Testing navigation flows
- ✅ Automated regression testing
- ✅ CI/CD pipelines
- ✅ Reproducing bugs

**Speed:** ~2 sec/test  
**Mode:** Headless (can run --headed for debugging)  
**Output:** Pass/Fail + logs

### Use Antigravity Browser 👁️
- ✅ Reviewing new designs
- ✅ Checking CSS/layout
- ✅ Visual inspection
- ✅ Responsive testing
- ✅ Demo to stakeholders
- ✅ Exploring UI manually

**Speed:** ~30 sec interaction  
**Mode:** Visual browser  
**Output:** Screenshots + videos

## Common Commands

```bash
# Playwright E2E
pytest tests/e2e/ -v                                    # All tests
pytest tests/e2e/ -m student -v                        # Student tests
pytest tests/e2e/ --headed -v                          # See browser
pytest tests/e2e/test_student_flow.py::test_name -v  # Single test

# Setup test data
python manage.py setup_test_data
```

## Test Credentials

```python
Parent:     orangtua / parent123
Student 4:  siswa4 / siswa123
Admin:      admin / admin123
```

## Remember

❌ **DON'T** use browser_subagent for functional testing (too slow)  
✅ **DO** use Playwright for functional testing (fast, reliable)

❌ **DON'T** use Playwright for visual review (no visual output in headless)  
✅ **DO** use browser_subagent for visual review (see actual UI)
