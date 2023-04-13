"""Fixtures for bw_visualization"""

from bw2data.tests import bw2test
from pathlib import Path
import bw2data as bd
import bw2io as bi
import requests


FIXTURES_DIR = Path(__file__).parent.absolute() / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)
USEEIO_FILENAME = "useeio.tar.gz"
USEEIO_FIXTURE = FIXTURES_DIR / USEEIO_FILENAME
PROJECT_NAME = 'USEEIO-1.1-noproducts'


def pytest_sessionstart(session):
    if not USEEIO_FIXTURE.exists():
        print("Downloading US EEIO")
        URL = "https://files.brightway.dev/" + USEEIO_FILENAME
        request = requests.get(URL, stream=True)
        if request.status_code != 200:
            raise ValueError(
                "URL {} returns status code {}.".format(URL, request.status_code)
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
def restore_database():
    bi.restore_project_directory(USEEIO_FIXTURE)
    bd.projects.set_current(PROJECT_NAME)
