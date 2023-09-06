"""Fixtures for bw_visualization"""
from pathlib import Path
import requests

from bw2data.tests import bw2test
import bw2data as bd
import bw2io as bi


FIXTURES_DIR = Path(__file__).parent.absolute() / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)
USEEIO_FILENAME = "useeio.tar.gz"
USEEIO_FIXTURE = FIXTURES_DIR / USEEIO_FILENAME
USEEIO_PROJECT_NAME = 'USEEIO-1.1-noproducts'


def pytest_sessionstart(session):
    if not USEEIO_FIXTURE.exists():
        print("Downloading US EEIO")
        url = "https://files.brightway.dev/" + USEEIO_FILENAME
        request = requests.get(url, stream=True, timeout=120)
        if request.status_code != 200:
            raise ValueError(
                f"URL {url} returns status code {request.status_code}."
            )
        download = request.raw
        chunk = 128 * 1024
        with open(USEEIO_FIXTURE, "wb") as f:
            while True:
                segment = download.read(chunk)
                if not segment:
                    break
                f.write(segment)


@bw2test
def restore_database_useeio():
    bi.restore_project_directory(USEEIO_FIXTURE)
    bd.projects.set_current(USEEIO_PROJECT_NAME)
