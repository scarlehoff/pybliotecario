from setuptools import setup, find_packages
from sys import argv

if len(argv) > 1 and argv[1] in ('develop', 'install'):
    import socket
# When installing with setup.py in develop/install mode
# use hostname as the name of the script
# with the first letter uppercased
    hostname = socket.gethostname()
    pybliotecario_name = hostname.capitalize()
else:
    pybliotecario_name = "pybliotecario"

setup(
        name=pybliotecario_name,
        version="1.0",
        package_dir = {'':'src'},
        packages=find_packages('src'),

        install_requires=[
            'arxiv',
            'pyowm',
        ],

        entry_points = {'console_scripts':
            [f'{pybliotecario_name} = pybliotecario.pybliotecario:main',]
            },
)

print(f'Installed pybliotecario as {pybliotecario_name}')
