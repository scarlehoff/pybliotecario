"""
    Configuration file for pytest
"""
import pytest

from pybliotecario.customconf import CustomConfigParser
from pybliotecario.backend.backend_test import TESTID


def generate_fake_config(main_folder):
    """Generate a fake configuration"""
    config = CustomConfigParser()
    config["DEFAULT"] = {
        "main_folder": main_folder,
        "token": "AAAaaa123",
        "chat_id": TESTID,
    }
    return config


@pytest.fixture
def tmpfile(tmp_path):
    """ Create a temporary file in the temporary directory """
    return tmp_path / "test.txt"
