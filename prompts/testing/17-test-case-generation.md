# 17 — Test case generation

**Phase:** testing · **Use when:** writing the tests themselves.

## Role
Test author in this repository's style.

## Inputs
- `tests/conftest.py` (fixtures)
- A neighbouring test file for style
- The behaviour under test

## Task
1. Choose the lowest level that can observe the behaviour (repository > service > handler).
2. Arrange explicitly: create users/conversations/personas with the real repositories.
3. Act with one call.
4. Assert the observable outcome — returned value, rows created/absent, raised error.
5. For AI paths, inject a fake `AIProvider`; never hit the network.
6. Name the test `test_<behaviour>_<condition>`.

## Constraints
- `async def test_...` with no decorator (`asyncio_mode = auto`).
- No `unittest.mock` of SQLAlchemy; use the in-memory DB.
- No assertions on private attributes or log text.
- Include the negative case (wrong owner, missing row) where the behaviour has one.

## Output
Test code + a one-line explanation of what each test proves.

## Verification
```bash
pytest -q tests/<file>::<test> -v
```
Re-run the whole suite once.
