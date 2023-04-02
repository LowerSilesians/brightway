"""Fixtures for bw_visualization"""

import pytest
import bw2data as bd
import bw2io as bi

PROJECT_NAME = 'test'


def pytest_sessionstart(session):
    bd.projects.set_current(PROJECT_NAME)
    bi.useeio11(collapse_products=True, prune=True)
    bi.backup_project_directory(PROJECT_NAME)


@pytest.fixture
async def restore_database():
    bi.restore_project_directory(f"{PROJECT_NAME}.tar.gz")
    bd.projects.set_current(PROJECT_NAME)
