"""
Shared utilities with no pybliotecario imports
"""

import importlib
import logging

log = logging.getLogger(__name__)


def import_component(module_name, class_name, arg_name=None):
    """Import the component class_name from module_name."""
    module_path = "pybliotecario.components." + module_name
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ModuleNotFoundError as e:
        log.error(f"In order to use --{arg_name} you need to install the module '{e.name}'")
        raise e
