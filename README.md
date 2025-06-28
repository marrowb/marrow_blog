# 📝 Marrow Blog - A Flask Blog Platform

> **Built on the excellent foundation of [Nick Janetakis' docker-flask-example](https://github.com/nickjj/docker-flask-example)**

A complete blog platform built with Flask, featuring admin authentication, markdown editing with [TinyMDE](https://github.com/jefago/tiny-markdown-editor), and SQLite storage. This project transforms Nick's minimal Flask template into a fully-featured content management system.

The blog platform includes admin authentication, post management, RESTful APIs, file uploads, and deployment to Fly.io.

## 🧾 Table of contents

- [Tech stack](#tech-stack)
- [Notable opinions and extensions](#notable-opinions-and-extensions)
- [Running this app](#running-this-app)
- [Files of interest](#files-of-interest)
  - [`.env`](#env)
  - [`run`](#run)
- [Running a script to automate renaming the project](#running-a-script-to-automate-renaming-the-project)
- [Updating dependencies](#updating-dependencies)
- [See a way to improve something?](#see-a-way-to-improve-something)
- [Additional resources](#additional-resources)
  - [Learn more about Docker and Flask](#learn-more-about-docker-and-flask)
  - [Deploy to production](#deploy-to-production)
- [About the author](#about-the-author)

## 🧬 Tech stack

If you don't like some of these choices that's no problem, you can swap them
out for something else on your own.

### Back-end

- [SQLite](https://www.sqlite.org/) with persistent volume storage
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) ORM with Alembic migrations
- [Flask-Login](https://flask-login.readthedocs.io/) for authentication
- [Celery](https://github.com/celery/celery) with SQLite broker backend

### Front-end

- Vanilla CSS & JS inspired by [Plain Vanilla](https://plainvanillaweb.com)

### Content Management

- [TinyMDE](https://github.com/jefago/tiny-markdown-editor) - Lightweight markdown editor
- [Flask-FlatPages](https://flask-flatpages.readthedocs.io/) for markdown processing
- [Pygments](https://pygments.org/) for syntax highlighting
- [Python-Frontmatter](https://python-frontmatter.readthedocs.io/) for metadata parsing

### API & Forms

- [Flask-Classful](https://flask-classful.readthedocs.io/) for RESTful APIs  
- [Marshmallow](https://marshmallow.readthedocs.io/) for serialization
- [Flask-WTF](https://flask-wtf.readthedocs.io/) for form handling

## 🚀 Blog Platform Features

This blog platform extends Flask with a complete content management system while maintaining clean architecture and development best practices.

### 🔐 Authentication & Security
- **Admin Authentication**: Secure login system with session management
- **Two-Factor Authentication**: Optional MFA using TOTP (PyOTP)
- **Password Security**: Werkzeug password hashing with salt
- **Protected Routes**: Login-required decorators for admin functionality

### 📝 Content Management
- **Blog Post System**: Create, edit, and manage blog posts with rich metadata
- **Markdown Editor**: [TinyMDE](https://github.com/jefago/tiny-markdown-editor) integration for intuitive editing
- **Syntax Highlighting**: Pygments-powered code highlighting in posts
- **SEO-Friendly URLs**: Automatic slug generation from titles
- **Tagging System**: Organize posts with comma-separated tags
- **Draft/Publish Workflow**: Preview posts before publishing

### 🔌 RESTful API
- **Post Management**: Full CRUD operations via `/api/v1/post/`
- **File Uploads**: Document upload handling via `/api/v1/upload/`
- **JSON Serialization**: Marshmallow schemas for clean data validation
- **Error Handling**: Consistent API error responses

### 🖥️ Admin Interface
- **Dashboard**: Overview of all posts with management controls
- **Post Editor**: Rich editing interface with markdown preview
- **File Upload**: Support for `.md` file imports with frontmatter
- **User Management**: CLI commands for creating admin users

### 🏗️ Technical Foundation
- **Database**: SQLite with Alembic migrations for schema management
- **Forms**: Flask-WTF with comprehensive validation
- **Static Assets**: esbuild + TailwindCSS with file fingerprinting
- **Testing**: Comprehensive test suite with pytest and coverage
- **Linting**: Ruff for code formatting and quality
- **Development Tools**: Custom `./run` script for common tasks

### 🚢 Production Ready
- **Fly.io Deployment**: Complete configuration for cloud deployment
- **Persistent Storage**: 20GB volume for SQLite database and uploads
- **Auto-scaling**: Configured machine start/stop based on traffic
- **Health Checks**: Monitoring endpoints for service health
- **CI/CD**: GitHub Actions for automated deployment

Besides the Flask app itself:

- [uv](https://github.com/astral-sh/uv) is used for package management instead of `pip3` (builds on my machine are ~10x faster!)
- Docker support has been added which would be any files having `*docker*` in
  its name
- GitHub Actions have been set up

## 🚀 Running this app

You'll need to have [Docker installed](https://docs.docker.com/get-docker/).
It's available on Windows, macOS and most distros of Linux. If you're new to
Docker and want to learn it in detail check out the [additional resources
links](#learn-more-about-docker-and-flask) near the bottom of this
README.

You'll also need to enable Docker Compose v2 support if you're using Docker
Desktop. On native Linux without Docker Desktop you can [install it as a plugin
to Docker](https://docs.docker.com/compose/install/linux/). It's been generally
available for a while now and is stable. This project uses specific [Docker
Compose v2
features](https://nickjanetakis.com/blog/optional-depends-on-with-docker-compose-v2-20-2)
that only work with Docker Compose v2 2.20.2+.

If you're using Windows, it will be expected that you're following along inside
of [WSL or WSL
2](https://nickjanetakis.com/blog/a-linux-dev-environment-on-windows-with-wsl-2-docker-desktop-and-more).
That's because we're going to be running shell commands. You can always modify
these commands for PowerShell if you want.

#### Clone this repo anywhere you want and move into the directory:

```sh
git clone https://github.com/YOUR_USERNAME/blog-sqlite marrow_blog
cd marrow_blog
```

#### Copy an example .env file because the real one is git ignored:

```sh
cp .env.example .env
```

#### Build everything:

*The first time you run this it's going to take 5-10 minutes depending on your
internet connection speed and computer's hardware specs. That's because it's
going to download a few Docker images and build the Python + Yarn dependencies.*

```sh
docker compose up --build
```

Now that everything is built and running we can treat it like any other Flask
app.

Did you receive a `depends_on` "Additional property required is not allowed"
error? Please update to at least Docker Compose v2.20.2+ or Docker Desktop
4.22.0+.

Did you receive an error about a port being in use? Chances are it's because
something on your machine is already running on port 8000. Check out the docs
in the `.env` file for the `DOCKER_WEB_PORT_FORWARD` variable to fix this.

Did you receive a permission denied error? Chances are you're running native
Linux and your `uid:gid` aren't `1000:1000` (you can verify this by running
`id`). Check out the docs in the `.env` file to customize the `UID` and `GID`
variables to fix this.

#### Setup the initial database:

```sh
# You can run this from a 2nd terminal. It will create both a development and
# test database with sample blog posts.
./run flask db reset --with-testdb
```

#### Create an admin user:

```sh
# Create an admin user to access the blog dashboard
./run admin create --username admin --password yourpassword

# Or with MFA enabled
./run admin create --username admin --password yourpassword --enable-mfa
```

*We'll go over that `./run` script in a bit!*

#### Check it out in a browser:

Visit <http://localhost:8000> in your favorite browser to see the blog.  
Visit <http://localhost:8000/login> to access the admin dashboard.

#### Linting the code base:

```sh
# You should get no output (that means everything is operational).
./run lint
```

#### Formatting the code base:

```sh
# You should see that everything is unchanged (it's all already formatted).
./run format
```

*There's also a `./run quality` command to run the above commands together.*

#### Running the test suite:

```sh
# You should see all passing tests. Warnings are typically ok.
./run test
```

#### Stopping everything:

```sh
# Stop the containers and remove a few Docker related resources associated to this project.
docker compose down
```

You can start things up again with `docker compose up` and unlike the first
time it should only take seconds.

## 🔍 Files of interest

I recommend checking out most files and searching the code base for `TODO:`,
but please review the `.env` and `run` files before diving into the rest of the
code and customizing it. Also, you should hold off on changing anything until
we cover how to customize this example app's name with an automated script
(coming up next in the docs).

### `.env`

This file is ignored from version control so it will never be commit. There's a
number of environment variables defined here that control certain options and
behavior of the application. Everything is documented there.

Feel free to add new variables as needed. This is where you should put all of
your secrets as well as configuration that might change depending on your
environment (specific dev boxes, CI, production, etc.).

### `run`

You can run `./run` to get a list of commands and each command has
documentation in the `run` file itself.

It's a shell script that has a number of functions defined to help you interact
with this project. It's basically a `Makefile` except with [less
limitations](https://nickjanetakis.com/blog/replacing-make-with-a-shell-script-for-running-your-projects-tasks).
For example as a shell script it allows us to pass any arguments to another
program.

This comes in handy to run various Docker commands because sometimes these
commands can be a bit long to type. Feel free to add as many convenience
functions as you want. This file's purpose is to make your experience better!

*If you get tired of typing `./run` you can always create a shell alias with
`alias run=./run` in your `~/.bash_aliases` or equivalent file. Then you'll be
able to run `run` instead of `./run`.*

## 📖 Using the Blog Platform

### Creating and Managing Content

#### Admin Dashboard
After logging in at `/login`, you'll have access to:
- **Dashboard**: Overview of all posts with quick actions
- **Create Post**: Rich markdown editor with TinyMDE
- **Upload Documents**: Import `.md` files with frontmatter support
- **Preview**: See how posts look before publishing

#### Writing Posts
The blog supports rich markdown with frontmatter metadata:

```markdown
---
title: "My Blog Post"
excerpt: "A brief description"
tags: "flask, python, web development"
published: true
---

# Your content here

Code blocks are highlighted:

```python
def hello():
    return "Hello, World!"
``` 
```

#### Using the API
The RESTful API provides programmatic access:

```bash
# Get all published posts
curl http://localhost:8000/api/v1/post/

# Create a new post (requires authentication)
curl -X POST http://localhost:8000/api/v1/post/ \
  -H "Content-Type: application/json" \
  -d '{"title": "New Post", "content": "# Hello World"}'
```

### Customizing Your Blog

If you want to customize the blog name, colors, or structure, the key files are:
- `marrow_blog/` - Main application code
- `public/styles/` - CSS customization
- `marrow_blog/templates/` - HTML templates
- `config/settings.py` - Application configuration

## 🛠 Updating dependencies

You can run `./run uv:outdated` or `./run yarn:outdated` to get a list of
outdated dependencies based on what you currently have installed. Once you've
figured out what you want to update, go make those updates in your
`pyproject.toml` and / or `package.json` file.

Or, let's say you've customized your app and it's time to add a new dependency,
either for Python or Node.

#### In development:

##### Option 1

1. Directly edit `pyproject.toml` or `assets/package.json` to add your package
2. `./run deps:install` or `./run deps:install --no-build`
    - The `--no-build` option will only write out a new lock file without re-building your image

##### Option 2

1. Run `./run uv add mypackage --no-sync` or `run yarn add mypackage --no-lockfile` which will update your `pyproject.toml` or `assets/package.json` with the latest version of that package but not install it
2. The same step as step 2 from option 1

Either option is fine, it's up to you based on what's more convenient at the
time. You can modify the above workflows for updating an existing package or
removing one as well.

You can also access `uv` and `yarn` in Docker with `./run uv` and `./run yarn`
after you've upped the project.

#### In CI:

You'll want to run `docker compose build` since it will use any existing lock
files if they exist. You can also check out the complete CI test pipeline in
the [run](https://github.com/nickjj/docker-flask-example/blob/main/run) file
under the `ci:test` function.

#### In production:

This is usually a non-issue since you'll be pulling down pre-built images from
a Docker registry but if you decide to build your Docker images directly on
your server you could run `docker compose build` as part of your deploy
pipeline which is similar to how it would work in CI.

## 🤝 See a way to improve something?

If you see anything that could be improved please open an issue or start a PR.
Any help is much appreciated!

## 🚢 Deployment

### Fly.io Deployment (Recommended)

This blog is configured for deployment to Fly.io with persistent storage:

```sh
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly.io
flyctl auth login

# Deploy the application
flyctl deploy
```

The app includes:
- **Persistent Storage**: 20GB volume for SQLite database and uploads
- **Auto-scaling**: Machines start/stop automatically based on traffic
- **Health Checks**: Built-in monitoring endpoints
- **CI/CD**: GitHub Actions for automated deployment

### Manual Deployment

For other platforms, the application requires:
- Python 3.13+ environment
- Persistent storage for SQLite database
- Environment variables from `.env.example`
- Static file serving capability

## 🌎 Additional Resources

### Official Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [TinyMDE Documentation](https://github.com/jefago/tiny-markdown-editor)

## 🙏 Credits & Attribution

### Original Template
This blog platform is built on the excellent foundation of **[Nick Janetakis' docker-flask-example](https://github.com/nickjj/docker-flask-example)**. Nick's template provides outstanding Docker configuration, development workflows, and Flask best practices that made this project possible.

- **Nick Janetakis** | [nickjanetakis.com](https://nickjanetakis.com) | [@nickjanetakis](https://twitter.com/nickjanetakis)

### Key Dependencies
- **[TinyMDE](https://github.com/jefago/tiny-markdown-editor)** by jefago - The lightweight markdown editor that powers the blog's content creation
- **[Flask](https://flask.palletsprojects.com/)** - The web framework that makes it all possible
- **[SQLite](https://www.sqlite.org/)** - Reliable, file-based database storage

### Blog Platform
This fork transforms the original template into a complete blogging platform with authentication, content management, and deployment capabilities. While maintaining the excellent development practices and Docker setup from the original, it adds a full-featured CMS suitable for production use.
