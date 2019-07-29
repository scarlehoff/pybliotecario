from setuptools import setup, find_packages
import socket


# By default we will use 'hostname' as the name for the script
# with the first letter uppercased
hostname = socket.gethostname()
pybliotecario_name = hostname.capitalize()

setup(
        name=pybliotecario_name,
        version="1.0",
        package_dir = {'':'src'},
        packages=find_packages('src'),

        entry_points = {'console_scripts':
            [f'{pybliotecario_name} = pybliotecario.pybliotecario:main',]
            },
)

print(f'Installed pybliotecario as {pybliotecario_name}')
