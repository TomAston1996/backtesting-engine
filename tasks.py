"""
The tasks.py file defines various tasks for managing the backtesting engine project.

These tasks include cleaning build artifacts, formatting code, running tests, auditing dependencies, and running the main backtesting
engine script. It uses the Invoke library to define and run tasks, making it easy to manage project workflows in Windows.
"""

import os
import shutil

from invoke import Context, task


@task
def clean(c: Context) -> None:
    """
    Clean the project by removing build artifacts and cache directories.

    Run with: `invoke clean`
    """
    for folder in ["dist", "static", "service", "code"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    c.run("uv clean")


@task
def format(c: Context) -> None:
    """
    Format the code using ruff.

    Run with: `invoke format`
    """
    c.run("uv run pyright")
    c.run("uv run ruff check . --fix")


@task
def test(c: Context) -> None:
    """
    Run the test suite with coverage.

    Run with: `invoke test`
    """
    c.run("uv run pytest --cov=src/backtesting_engine --cov-report=term-missing -vv")


@task
def audit(c: Context) -> None:
    """
    Run a security audit on the dependencies.

    Run with: `invoke audit`
    """
    c.run("uv export --format requirements-txt > requirements.txt")
    c.run("uvx pip-audit -r requirements.txt --disable-pip --strict --fix")
    os.remove("requirements.txt")


@task
def run(c: Context) -> None:
    """
    Run the backtesting engine main script.

    Run with: `invoke run`
    """
    c.run("uv run python src/backtesting_engine/main.py")
