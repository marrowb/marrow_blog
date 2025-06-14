# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses a custom `./run` script for common development tasks:

### Essential Commands
- `./run` - Show all available commands
- `./run flask db reset --with-testdb` - Setup initial database with test data
- `./run test` - Run the test suite with pytest
- `./run lint` - Lint Python code with ruff
- `./run format` - Format Python code with ruff
- `./run quality` - Run all linting and formatting checks together
- `./run shell` - Start a bash session in the web container
- `./run flask` - Run any Flask CLI commands
- `./run admin` - Run Flask admin CLI commands

### Docker Development
- `docker compose up --build` - Build and start all services
- `docker compose down` - Stop all services
- `./run deps:install` - Install Python dependencies (rebuilds container)

### Environment Setup
1. Copy `.env.example` to `.env` for local development
2. Run `docker compose up --build` to start services
3. Run `./run flask db reset --with-testdb` to initialize database

## Application Architecture

### Flask Application Structure
- **App Factory Pattern**: `marrow_blog/app.py` contains `create_app()` function
- **Blueprint Organization**: Modular design with separate blueprints for different functionality
- **Extensions**: Centralized in `marrow_blog/extensions.py` (SQLAlchemy, login manager, etc.)

### Key Blueprints
- `admin` - Admin interface with authentication and post management (`/login`, `/dashboard`)
- `page` - Public-facing pages (`/`, `/blog/<id>`)
- `up` - Health check endpoints
- `api/v1` - RESTful API endpoints using Flask-Classful

### Database & Models
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Migrations**: Alembic (managed via `flask db` commands)
- **Models**: Located in respective blueprint directories (e.g., `marrow_blog/blueprints/posts/models.py`)
- **Database Location**: SQLite at `/app/data/marrow_blog.db` (in Docker)

### Authentication System
- **Flask-Login** for session management
- **AdminUser** model with password hashing and optional MFA (PyOTP)
- **Login required** decorator protects admin routes

### Content Management
- **Markdown Support**: Flask-FlatPages with Pygments syntax highlighting
- **Post System**: Database-backed blog posts with publish/draft states
- **File Uploads**: Admin interface supports document uploads (`.md` files)

### Frontend Assets
- **Static Files**: Served from `public/` directory (mapped to root URL path)
- **TinyMDE**: Markdown editor integration for admin interface
- **Custom CSS**: Global styles and component-specific styling

### Configuration
- **Environment-based**: `config/settings.py` reads from environment variables
- **Development vs Production**: Controlled via `FLASK_DEBUG` environment variable
- **Database URL**: Configurable via `DATABASE_URL` (defaults to SQLite)

## Testing & Quality

### Code Quality Tools
- **Ruff**: Used for both linting and formatting (replaces flake8/black)
- **pytest**: Test framework with coverage reporting
- **Line Length**: 79 characters (configured in pyproject.toml)

### Test Structure
- Tests located in `test/` directory
- Blueprint-specific test modules mirror application structure
- Use `conftest.py` for shared test fixtures

## Docker & Deployment

### Container Structure
- **Multi-service**: PostgreSQL, Redis, web application, and worker containers
- **Development**: Volume mounts for live code reloading
- **Production**: Built assets and optimized configuration

### Key Files
- `Dockerfile` - Application container definition
- `compose.yaml` - Multi-service orchestration
- `run` script - Development task automation
- `.env` - Environment configuration (copy from `.env.example`)

## Database Operations

### Common Patterns
- Use Flask-SQLAlchemy ORM for database operations
- Models should extend `db.Model`
- Use Alembic migrations for schema changes: `flask db migrate -m "description"`
- Reset database: `./run flask db reset --with-testdb`

### Migrations
- Migration files in `db/versions/`
- Generate new migrations: `flask db migrate`
- Apply migrations: `flask db upgrade`