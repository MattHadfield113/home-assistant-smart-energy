# GitHub Actions CI/CD

This directory contains automated workflows for continuous integration, testing, and deployment.

## Workflows

### CI Workflow (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via workflow_dispatch

**Jobs:**

1. **lint-python** - Python code quality
   - Black (formatting)
   - isort (import sorting)
   - Flake8 (linting)
   - Pylint (static analysis)

2. **lint-javascript** - JavaScript code quality
   - ESLint

3. **test-python** - Unit tests
   - Runs on Python 3.10, 3.11, 3.12
   - Coverage reporting
   - Uploads to Codecov

4. **validate-config** - Configuration validation
   - Validates config.json
   - Validates Dockerfile with hadolint

5. **security-scan** - Security checks
   - Safety (dependency vulnerabilities)
   - Bandit (security linting)

6. **codeql-analysis** - Advanced security
   - GitHub CodeQL scanning
   - Python and JavaScript analysis

7. **docker-build** - Docker image test
   - Test build for all architectures

8. **addon-validator** - Home Assistant specific
   - Validates add-on structure
   - Checks metadata

9. **documentation-check** - Documentation
   - Verifies required docs exist
   - Checks markdown links

10. **test-summary** - Results summary
    - Aggregates all job results
    - Fails if critical checks fail

### Release Workflow (`release.yml`)

**Triggers:**
- Git tags matching `v*.*.*` pattern
- Manual trigger with version input

**Jobs:**

1. **validate-version** - Version checks
   - Validates version format
   - Checks config.json matches tag

2. **run-tests** - Full test suite
   - Ensures all tests pass before release

3. **build-and-push** - Multi-arch builds
   - Builds for: amd64, armv7, aarch64, armhf, i386
   - Pushes to Docker Hub
   - Tags with version and latest

4. **create-manifest** - Docker manifests
   - Creates multi-arch manifests
   - Enables platform-specific pulls

5. **create-github-release** - GitHub release
   - Extracts changelog
   - Creates release with notes
   - Attaches artifacts

6. **notify-completion** - Status notification
   - Reports completion status

## Configuration Files

### `.flake8`
Flake8 linter configuration:
- Max line length: 120
- Ignores: E203, W503, E501
- Excludes common directories

### `.pylintrc`
Pylint configuration:
- Customized rule set
- Max line length: 120
- Disabled verbose rules

### `pyproject.toml`
Modern Python project configuration:
- Black formatting settings
- isort configuration
- pytest settings
- Coverage configuration

### `.pre-commit-config.yaml`
Pre-commit hooks for local development:
- Trailing whitespace
- YAML/JSON validation
- Black, isort, Flake8
- Bandit security checks
- ESLint for JavaScript

### `dependabot.yml`
Automated dependency updates:
- Python packages (weekly)
- GitHub Actions (weekly)
- Docker base images (weekly)

## Issue Templates

### Bug Report (`bug_report.yml`)
Structured bug report form with fields:
- Description
- Expected behavior
- Steps to reproduce
- Version information
- Logs and configuration

### Feature Request (`feature_request.yml`)
Feature suggestion form with fields:
- Problem description
- Proposed solution
- Alternatives considered
- Additional context

## Pull Request Template

Standard PR template requiring:
- Description of changes
- Type of change
- Related issues
- Testing information
- Checklist of requirements
- Screenshots (if applicable)

## Required Secrets

For full CI/CD functionality, configure these secrets in GitHub repository settings:

### Docker Hub (for releases)
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password or token

### Optional
- `CODECOV_TOKEN` - Codecov upload token (for coverage reporting)

## Badge URLs

Add these badges to your README.md:

```markdown
[![CI](https://github.com/MattHadfield113/home-assistant-smart-energy/actions/workflows/ci.yml/badge.svg)](https://github.com/MattHadfield113/home-assistant-smart-energy/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MattHadfield113/home-assistant-smart-energy/branch/main/graph/badge.svg)](https://codecov.io/gh/MattHadfield113/home-assistant-smart-energy)
```

## Local Development

### Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### Run Pre-commit Manually

```bash
pre-commit run --all-files
```

### Run Specific Checks

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Static analysis
pylint app/

# Security scan
bandit -r app/

# Run tests
pytest tests/ -v --cov=app
```

## Workflow Best Practices

### For Contributors

1. **Before Committing**
   - Run pre-commit hooks
   - Ensure tests pass locally
   - Update documentation

2. **Creating PRs**
   - Use descriptive titles
   - Fill out PR template
   - Link related issues
   - Add tests for new features

3. **During Review**
   - Address feedback promptly
   - Keep commits clean
   - Rebase if needed

### For Maintainers

1. **Reviewing PRs**
   - Check all CI jobs pass
   - Review code quality
   - Test functionality
   - Verify documentation

2. **Creating Releases**
   - Update CHANGELOG.md
   - Bump version in config.json
   - Create git tag: `git tag v1.2.0`
   - Push tag: `git push origin v1.2.0`

3. **Monitoring**
   - Check workflow runs regularly
   - Review Dependabot PRs
   - Update actions annually

## Troubleshooting

### CI Failures

**Linting Errors:**
- Run locally: `black app/ tests/`
- Check: `flake8 app/ tests/`

**Test Failures:**
- Run locally: `pytest tests/ -v`
- Check test output for details

**Docker Build Failures:**
- Test locally: `docker build -t test .`
- Check Dockerfile syntax

**Add-on Validation Failures:**
- Validate config.json syntax
- Check required fields present
- Verify architecture list

### Release Issues

**Version Mismatch:**
- Ensure config.json version matches git tag
- Format: `v1.2.3` for tag, `1.2.3` in config

**Docker Push Failures:**
- Verify Docker Hub credentials
- Check image size limits
- Ensure network connectivity

**GitHub Release Failures:**
- Check CHANGELOG.md format
- Verify GitHub token permissions
- Review release notes extraction

## Maintenance

### Regular Tasks

- **Weekly:** Review Dependabot PRs
- **Monthly:** Update GitHub Actions versions
- **Quarterly:** Review and update workflows
- **Annually:** Audit security settings

### Updating Workflows

When modifying workflows:
1. Test syntax: `yamllint .github/workflows/*.yml`
2. Validate logic: Review job dependencies
3. Test with branch first
4. Monitor first run carefully
5. Update documentation

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons)
- [Docker Hub](https://hub.docker.com/)
- [Codecov](https://codecov.io/)
- [Pre-commit](https://pre-commit.com/)

## Support

For issues with CI/CD:
1. Check workflow run logs
2. Review this documentation
3. Check GitHub Actions status
4. Open an issue with workflow run link
