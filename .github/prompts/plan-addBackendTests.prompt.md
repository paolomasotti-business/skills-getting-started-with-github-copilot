## Plan: Add backend FastAPI tests (AAA pattern)

TL;DR: Create a new `tests/` directory with pytest-based FastAPI tests covering the existing API routes, using the AAA (Arrange-Act-Assert) pattern for every test. Ensure tests isolate and restore the in-memory `activities` state between runs.

Steps
1. Create `tests/` directory.
2. Add `tests/test_app.py` with tests for:
   - root redirect from `/` to `/static/index.html`
   - `GET /activities` returning activity data
   - `POST /activities/{activity_name}/signup` registering a new participant
   - duplicate signup returning `400` with the existing duplicate-check behavior
   - `DELETE /activities/{activity_name}/participants` removing a participant
   - deleting a missing participant returning `404`
3. Structure each test using the AAA pattern (Arrange, Act, Assert). For example:
   - Arrange: set up `TestClient(app)`, prepare any test data, and ensure `activities` initial state is known (use `copy.deepcopy` of a module-level snapshot).
   - Act: call the API route (`client.post(...)` / `client.delete(...)`).
   - Assert: verify HTTP status and response body, and that `activities` state was updated as expected.
4. Add a pytest fixture `reset_activities` that saves a deep copy of the original `activities` (imported from `src.app`) before each test and restores it after the test to keep tests isolated.
5. Use FastAPI's `TestClient` from `fastapi.testclient` and import the `app` instance from `src.app` in tests.
6. Update `requirements.txt` to include `pytest` so tests run in CI/local environments.

Verification
- Run `pytest` from repository root and confirm tests pass.
- Confirm redirected route and participant add/remove behavior are covered and tests are isolated (no state leak between tests).

Notes
- Keep tests synchronous using `TestClient` and fixture-based state reset rather than async test runners.
- Optionally add a `Makefile` or `scripts/` entry to run `pytest -q` for convenience.
