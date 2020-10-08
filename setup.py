import pathlib
from setuptools import setup, find_packages
from sys import argv

pybliotecario_name = "pybliotecario"
if __name__ == "__main__" and len(argv) > 1 and argv[1] in ("develop", "install"):
    print("You are installing the pybliotecario via the repository")

    import socket

    # When installing with setup.py in develop/install mode
    # use hostname as the name of the script
    # with the first letter uppercased
    hostname = socket.gethostname().capitalize()
    print("By default it will be installed with the name of your computer")
    yn = input(f"Do you want the pybliotecario executable to be called: {hostname} (y/n) ")
    if yn.lower() == "y" or yn.lower() == "yes":
        pybliotecario_name = hostname
    else:
        print(f"You chose to use the name {pybliotecario_name} instead")


# Readup the readme
README = (pathlib.Path(__file__).parent / "readme.md").read_text()
setup(
    name=pybliotecario_name,
    version="1.3",
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
        "regex",
        "arxiv",
        "pyowm",
        "psutil",
        "wikipedia",
    ],
    extra_requires={"facebook": ["flask"]},
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
