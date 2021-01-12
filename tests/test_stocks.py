"""
    Tests the stocks module
"""
import json
from pybliotecario.pybliotecario import main
from pybliotecario.backend import TestUtil
from .conftest import generate_fake_config


def test_cmdline_usage(tmpfile):
    """Generates a fake json for stock watching
    and then sends it to the pybliotecario
    """
    # Prepare the json file
    json_example = {"AAPL": {"below": 5, "above": 5}}
    tmp = tmpfile.with_suffix(".json")
    with open(tmp, "w") as f:
        json.dump(json_example, f)
    args = [f"--stock_watcher", str(tmp)]
    # Create the fake backend
    test_util = TestUtil(communication_file=tmpfile)
    fake_config = generate_fake_config(tmpfile)
    main(cmdline_arg=args, tele_api=test_util, config=fake_config)
    messages = tmpfile.read_text().strip().split("\n")
    # We should get just one message saying that AAPL is above the threshold
    assert len(messages) == 1
    assert "price is above" in messages[0]
