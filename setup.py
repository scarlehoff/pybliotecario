import pathlib
from setuptools import setup, find_packages
import sys

pybliotecario_name = "pybliotecario"
if "--with_name" in sys.argv:
    import socket

    # Use the hostname as the name of the pybliotecario
    # executable
    hostname = socket.gethostname().capitalize()
    pybliotecario_name = hostname

    # Remove it from the list of argument, nobody should know
    sys.argv.remove("--with_name")

# Readup the readme
README = (pathlib.Path(__file__).parent / "readme.md").read_text()
setup(
    name=pybliotecario_name,
    version="2.0.0",
    author="Scarlehoff",
    author_email="juacrumar@lairen.eu",
    url="https://github.com/scarlehoff/pybliotecario",
    description="Personal telegram bot to interact between your Telegram account and your computer",
    long_description=README,
    long_description_content_type="text/markdown",
    license="GNU GPLv3",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        "numpy",
        "requests",
        "regex",
        "arxiv",
        "pyowm",
        "psutil",
        "wikipedia",
    ],
    extras_require={"facebook": ["flask", "requests_toolbelt"]},
    entry_points={
        "console_scripts": [
            "{0} = pybliotecario.pybliotecario:main".format(pybliotecario_name),
        ]
    },
)

print(
    """
##############
Installed pybliotecario as {0}

IMPORTANT: Don't forget to run
      ~$ {0} --init
for proper configuration of the pybliotecario""".format(
        pybliotecario_name
    )
)
