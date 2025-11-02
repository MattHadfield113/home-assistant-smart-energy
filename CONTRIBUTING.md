# Contributing to Smart Energy Controller

Thank you for your interest in contributing to the Smart Energy Controller add-on!

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Docker (for testing builds)
- Home Assistant instance for testing

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/MattHadfield113/home-assistant-smart-energy.git
   cd home-assistant-smart-energy
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks** (recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Code Quality

### Running Tests

Run all tests:
```bash
python -m pytest tests/ -v
```

Run tests with coverage:
```bash
python -m pytest tests/ -v --cov=app --cov-report=html
```

Run specific test file:
```bash
python -m pytest tests/test_energy_manager.py -v
```

### Linting and Formatting

**Black** (code formatting):
```bash
black app/ tests/
```

**isort** (import sorting):
```bash
isort app/ tests/
```

**Flake8** (linting):
```bash
flake8 app/ tests/ --max-line-length=120
```

**Pylint** (static analysis):
```bash
pylint app/ --max-line-length=120
```

**Bandit** (security):
```bash
bandit -r app/
```

### Pre-commit Checks

All checks at once:
```bash
pre-commit run --all-files
```

## Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new functionality

3. **Run tests and linters**
   ```bash
   python -m pytest tests/ -v
   black app/ tests/
   isort app/ tests/
   flake8 app/ tests/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commit messages:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `test:` - Test additions/changes
   - `chore:` - Maintenance tasks
   - `refactor:` - Code refactoring
   - `perf:` - Performance improvements

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] Imports are sorted with isort
- [ ] No linting errors from Flake8
- [ ] Added tests for new functionality
- [ ] Updated documentation if needed
- [ ] Updated CHANGELOG.md

### PR Description

Include:
- Clear description of changes
- Related issue number (if applicable)
- Testing steps
- Screenshots (for UI changes)
- Breaking changes (if any)

### Review Process

1. Automated checks run via GitHub Actions
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Testing

### Unit Tests

- Test files in `tests/` directory
- Use `unittest.mock` for mocking
- Aim for >80% code coverage

### Writing Tests

```python
import unittest
from unittest.mock import Mock
from app.energy_manager import EnergyManager

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.mock_ha = Mock()
        self.manager = EnergyManager(self.mock_ha, {})
    
    def test_feature(self):
        result = self.manager.new_feature()
        self.assertEqual(result, expected_value)
```

### Integration Testing

Test with real Home Assistant:
1. Build Docker image
2. Install in HA Supervisor
3. Test functionality manually
4. Check logs for errors

## Documentation

### Code Documentation

- Add docstrings to all functions/classes
- Include type hints where possible
- Comment complex logic

### User Documentation

Update when adding features:
- `README.md` - Overview and quick start
- `DOCS.md` - Detailed usage guide
- `FEATURES.md` - Feature descriptions
- `CHANGELOG.md` - Version history

## Security

### Reporting Vulnerabilities

Report security issues privately to the maintainers. Do not create public issues.

### Security Best Practices

- Never commit secrets or credentials
- Validate all user inputs
- Use parameterized queries
- Keep dependencies updated
- Follow OWASP guidelines

## CI/CD

### GitHub Actions Workflows

**CI Workflow** (`ci.yml`):
- Runs on every push and PR
- Lints Python and JavaScript
- Runs all tests
- Validates configuration
- Security scanning
- Docker build test
- Add-on validation

**Release Workflow** (`release.yml`):
- Triggers on version tags
- Builds multi-arch Docker images
- Creates GitHub release
- Updates documentation

### Workflow Triggers

CI runs on:
- Push to `main` or `develop`
- Pull requests
- Manual trigger

Release runs on:
- Git tags matching `v*.*.*`
- Manual trigger with version input

## Add-on Specific Guidelines

### Configuration Schema

When adding config options:
1. Update `config.json` schema
2. Add default value
3. Document in DOCS.md
4. Update config examples

### Home Assistant Integration

- Use HA REST API
- Follow HA naming conventions
- Include proper entity attributes
- Handle HA unavailability gracefully

### Docker Best Practices

- Keep image size small
- Use multi-stage builds if needed
- Pin base image versions
- Don't run as root if possible

## Getting Help

- Check existing issues
- Read documentation
- Ask in pull request comments
- Create a discussion for questions

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be:
- Listed in release notes
- Acknowledged in commits
- Added to contributors list

Thank you for contributing! 🎉
