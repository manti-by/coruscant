# AGENTS.md

## Project Overview

Coruscant is a Raspberry Pi–based IoT satellite for the ODIN server.
It reads DS18B20 temperature sensors, controls pumps, valves, relays and servos, 
and synchronizes relay states with ODIN via Redis pub/sub messages.

## Project Structure

- `coruscant/settings.py`: Core configuration, paths, logging setup and external API URLs
- `coruscant/sensors.py`: Reading DS18B20 temperature sensors
- `coruscant/pumps.py`, `coruscant/servos.py`, `coruscant/valve.py`: Hardware control logic
- `coruscant/services/redis_bus.py`: Relay status management using Redis
- `coruscant/services/gpio.py`: GPIO helpers for Raspberry Pi
- `coruscant/tests/`: Pytest tests for services and core logic
- `utils/`: Crontab and consumer service configuration

## Git Workflow

This project adheres strictly to the Git Flow branching model. AI agents must follow these guidelines:

### Main Branch:

- The `master` branch always contains production-ready, stable code.
- Never commit directly to `master`.
- Do not use `git push --force` on the `master` branch.
- Do not merge branches into `master` without explicit approval.

### Feature Branches:

- Create feature branches using the naming convention `feature/<issue-id>-<descriptive-name>` 
(e.g., `feature/ODIN-10-add-user-authentication`).
- Use the [Conventional Commits](https://www.conventionalcommits.org) specification for commit messages (e.g., `feat:`, `fix:`, `docs:`).
- Ensure all local tests pass before committing.
- Ensure all linting errors are fixed before committing.
- Use `git push --force-with-lease` if needed on your feature branch, but never on `master`.

### Pull Requests (PRs):

- Open a Pull Request for every completed feature branch.
- PRs must be reviewed and pass all CI checks before merging.
- The PR title should follow the Conventional Commits specification.

## Development Commands

### Package Management

```bash
# Install dependencies (including dev extras)
uv sync --extra dev

# Upgrade dependencies and pre-commit hooks
uv sync --upgrade --extra dev
uv run pre-commit autoupdate
```

### Makefile Targets

```bash
make setup   # Create /var/log/coruscant and /var/lib/coruscant, initialize SQLite DB
make install # Install dev dependencies via uv
make update  # Upgrade dev dependencies and pre-commit hooks
make check   # Run pre-commit on all files (linter checks)
make test    # Run pytest (LOG_PATH=/tmp/odin.log, inside coruscant/)
make ci      # Shorthand: install check test
make deploy  # Deploy latest changes
```

### Running Modules

From the project root, after creating a virtualenv and installing dependencies:

```bash
uv run python -m coruscant.sensors
uv run python -m coruscant.pumps
uv run python -m coruscant.servos
uv run python -m coruscant.valve
```

NOTE: Do not use `run.sh` in any environments as it only works on Raspberry Pi.

### Testing

```bash
# Run full test suite
make test

# Equivalent without Makefile (from project root)
export LOG_PATH=/tmp/odin.log
cd coruscant/
uv run pytest
```

## Language & Environment

- Python 3.13 (see `pyproject.toml`)
- Follow PEP 8 style guidelines, with Ruff enforcing style and linting (120 char line length)
- Use type hints for functions and complex code paths
- Always use f-strings over `.format()` or `%`
- Use list/dict/set comprehensions instead of `map`/`filter` where it improves readability
- Prefer `pathlib.Path` over `os.path` for filesystem paths
- Follow PEP 257 for docstrings where docstrings are used
- Prefer EAFP (try/except) over LBYL (if checks) in Python code

## Code Style & Tooling

Configured in `pyproject.toml`:

- **Ruff** for linting and import management (`[tool.ruff]`, `[tool.ruff.lint]`)
- **Bandit** for basic security checks (`[tool.bandit]`)
- **pre-commit** is used to run the tools before commits

Run manually:

```bash
uv run pre-commit run --all-files
uv run ruff check .
uv run bandit -c pyproject.toml .
```

## Testing Guidelines

- Use `pytest` for tests (`coruscant/tests/`)
- Focus tests on:
  - External integrations (e.g. `services.gpio`)
  - Hardware control logic (`pumps`, `servos`, `valve`)
- Use mocks for:
  - GPIO access
  - Real redis for unit-level tests
- Write descriptive test names with `__` separating scenario parts (e.g. `test_update_relay_state__failed`)
- Test both success, failure and exception paths

## Logging and Error Handling

- Use Python’s `logging` module (see `coruscant/settings.LOGGING`)
- Create loggers at module level: `logger = logging.getLogger(__name__)`
- Use appropriate log levels:
  - `DEBUG`: Detailed internal information
  - `INFO`: Normal operational messages
  - `WARNING`: Recoverable or unexpected situations
  - `ERROR`: Failures that need attention
- Log exceptions with context before re-raising or returning fallback values
- Keep hardware-related exceptions contained and logged, avoid crashing long-running cron jobs

## Environment & Configuration

Environment is controlled primarily via `coruscant/settings.py`:

- `REDIS_URL`: Redis URL for relay status messages
- `LOG_PATH`, `LOGS_API_URL`: Local log file and remote log collector URL
- Hardware-related constants for sensor IDs, relay pins, and servo mapping

Operational notes:

- Expect to run on Raspberry Pi 2 Model B (or similar)
- DS18B20 sensors must be wired and configured according to `TEMP_SENSORS` and `VALVE_SENSOR_ID`
- Ensure `/var/log/coruscant/` exist and are writable by the `coruscant` user (see `make setup`)

## Security Guidelines

- Never commit secrets, passwords, or API tokens
- Configure sensitive values via environment variables
- Run `bandit` periodically or in CI
- Validate any external input before using it in system calls or network operations

## AI Behavior

Response style – concise and minimal:

- Provide minimal, working code without unnecessary explanation
- Omit comments unless essential for understanding
- Skip boilerplate and obvious patterns unless requested
- Use type inference and shorthand syntax where possible
- Focus on the core solution, skip tangential suggestions
- Assume familiarity with language idioms and patterns
- Let code speak for itself through clear naming and structure
- Avoid over-explaining standard patterns and conventions
- Provide just enough context to understand the solution
- Trust the developer to handle obvious cases independently
