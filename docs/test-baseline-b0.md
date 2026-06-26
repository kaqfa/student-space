# Test Baseline — B0 Phase

Date: 2026-06-26

## Environment

- Python: 3.12 (system, `/home/kaqfa/.local/lib/python3.12`)
- Django: 5.x
- Settings used for check: `config.settings.base`
- Settings in `pytest.ini`: `config.settings.development`

## Django System Check

```
DJANGO_SETTINGS_MODULE=config.settings.base python3 manage.py check
→ System check identified no issues (0 silenced).
```

Note: `config.settings.development` fails because `debug_toolbar` and `django_extensions`
are not installed in the current venv.

## Test Suite State

- **No unit tests exist** as of B0.
- `tests/` contains only E2E tests (Playwright).
- `pytest` cannot run: root `conftest.py` pulls in `tests.conftest` which imports `playwright`
  — not installed in venv.
- `pytest.ini` targets both `tests/` and `apps/` but no `test_*.py` files found in `apps/`.

## Blocking Missing Packages (not in venv)

| Package | Required by |
|---|---|
| `playwright` | `tests/conftest.py` (E2E tests) |
| `debug_toolbar` | `config.settings.development` |
| `django_extensions` | `config.settings.development` |
| `celery` | `config/celery.py` (worker only, guarded) |
| `redis` | Celery broker (worker only) |
| `django-celery-results` | Optional results backend |

## Conclusion

Baseline: **0 unit tests, 0 passing, 0 failing** (no unit tests written yet).
Django check passes with `config.settings.base`.
E2E suite requires `playwright` install and a running server.

Next step B1: write first unit tests alongside academic app models.
