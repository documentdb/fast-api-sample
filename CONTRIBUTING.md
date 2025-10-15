# Contributing to FastAPI + DocumentDB E-commerce Demo

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites

- Docker Desktop (Windows, macOS, or Linux)
- Git
- Basic knowledge of Python, FastAPI, and MongoDB/DocumentDB

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/documentdb/fastapi-documentdb-demo.git
   cd fastapi-documentdb-demo
   ```

2. **Create environment file**
   ```bash
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # Linux/macOS
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Load sample data** (optional)
   ```bash
   docker-compose exec backend python scripts/load_sample_data.py
   ```

## Development Setup

### Running the Application

Start all services:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f backend
```

Stop services:
```bash
docker-compose down
```

### Accessing Services

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **DocumentDB**: localhost:27017 (user: `docdb_user`, password: `docdb_password`)

### Development Workflow

1. **Make changes** to the code
2. Changes are automatically reloaded (hot reload enabled)
3. **Test your changes** using the interactive docs or automated tests
4. **Run tests** before committing

## Project Structure

```
fastapi-vscode/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration and database
│   │   ├── models/         # Beanie document models
│   │   ├── schemas/        # Pydantic schemas for API
│   │   ├── routers/        # API route handlers
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Pytest test files
│   ├── Dockerfile
│   └── requirements.txt
├── scripts/                # Utility scripts
├── docker-compose.yml
├── .env.example
└── README.md
```

### Key Components

- **Models** (`backend/app/models/`): Beanie Document models representing MongoDB collections
- **Schemas** (`backend/app/schemas/`): Pydantic models for request/response validation
- **Routers** (`backend/app/routers/`): FastAPI route handlers with business logic
- **Tests** (`backend/tests/`): Pytest test files

## Coding Standards

### Python Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- Line length: 100 characters
- Use type hints for function parameters and return values
- Use docstrings for all public functions and classes

### Code Formatting

Format code with Black and isort:
```bash
docker-compose exec backend black backend/app backend/tests
docker-compose exec backend isort backend/app backend/tests
```

Check formatting:
```bash
docker-compose exec backend black --check backend/app backend/tests
docker-compose exec backend isort --check-only backend/app backend/tests
```

### Type Checking

Run mypy for type checking:
```bash
docker-compose exec backend mypy backend/app
```

### Naming Conventions

- **Files**: lowercase with underscores (`product_service.py`)
- **Classes**: PascalCase (`ProductService`)
- **Functions**: lowercase with underscores (`get_product_by_id`)
- **Constants**: UPPERCASE with underscores (`MAX_PAGE_SIZE`)
- **API endpoints**: kebab-case (`/api/v1/products/by-category`)

## Testing

### Running Tests

Run all tests:
```bash
docker-compose exec backend pytest
```

Run tests with coverage:
```bash
docker-compose exec backend pytest --cov=backend/app --cov-report=term-missing
```

Run specific test file:
```bash
docker-compose exec backend pytest backend/tests/test_products.py
```

Run specific test:
```bash
docker-compose exec backend pytest backend/tests/test_products.py::TestProductEndpoints::test_create_product
```

### Writing Tests

- Place tests in `backend/tests/`
- Name test files `test_*.py`
- Use fixtures from `conftest.py`
- Write clear test names that describe what is being tested
- Use AAA pattern: Arrange, Act, Assert

Example test:
```python
async def test_create_product(client: AsyncClient):
    """Test creating a new product."""
    # Arrange
    product_data = {
        "name": "Test Product",
        "price": 99.99,
        "sku": "TEST-001",
        "category": "Test",
    }
    
    # Act
    response = await client.post("/api/v1/products", json=product_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == product_data["name"]
```

### Test Coverage

Maintain at least 80% code coverage. Check coverage report:
```bash
docker-compose exec backend pytest --cov=backend/app --cov-report=html
```

Open `htmlcov/index.html` in a browser to view detailed coverage.

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   docker-compose exec backend pytest
   docker-compose exec backend black --check backend/app backend/tests
   docker-compose exec backend isort --check-only backend/app backend/tests
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a PR from your branch
   - Fill in the PR template with details about your changes
   - Link any related issues

### Commit Messages

Write clear commit messages:

- Use present tense ("Add feature" not "Added feature")
- First line: brief description (50 chars or less)
- Optional: detailed description after blank line
- Reference issues/PRs when relevant

Examples:
```
Add product search functionality

Implements search by name and description with case-insensitive
regex matching. Includes tests and updates to documentation.

Fixes #123
```

### Code Review

- All PRs require review before merging
- Address reviewer feedback promptly
- Keep PRs focused and reasonably sized
- Update your PR based on feedback

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Beanie Documentation](https://beanie-odm.dev/)
- [DocumentDB Documentation](https://github.com/documentdb/documentdb)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

## Questions?

If you have questions or need help:

1. Check existing issues on GitHub
2. Review the project README and documentation
3. Ask in discussions or create a new issue

Thank you for contributing! 🎉
