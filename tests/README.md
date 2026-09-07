# Run tests with

### All tests:
```bash
docker compose run --rm app pytest
docker compose run --rm app python -m pytest
docker compose run --rm app python -m pytest -v
```

### Specific file:
```bash
docker compose run --rm app \
    python -m pytest -v tests/services/ualosses/test_crawler.py
```

### Specific tesst:
```bash
docker compose run --rm app \
    python -m pytest -v \
    tests/services/ualosses/test_crawler.py::test_next_prefix
```
