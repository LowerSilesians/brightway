"""Fixtures for bw_visualization"""

import pytest
import bw2data as bd
import bw2io as bi

PROJECT_NAME = 'test'
BACKUP_PATH = ''


def pytest_sessionstart(session):
    global BACKUP_PATH
    bd.projects.set_current(PROJECT_NAME)
    bi.useeio11(collapse_products=True, prune=True)
    BACKUP_PATH = bi.backup_project_directory(PROJECT_NAME)  # backup_project_directory doesn't return file path and cant be used


@pytest.fixture
def restore_database():
    bi.restore_project_directory(BACKUP_PATH)
    bd.projects.set_current(PROJECT_NAME)
