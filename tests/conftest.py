"""
    Configuration file for pytest
"""
import pytest

@pytest.fixture
def tmpfile(tmp_path):
    """ Create a temporary file in the temporary directory """
    return tmp_path / "test.txt"
