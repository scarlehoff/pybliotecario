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
            'psutil',
        ],

        entry_points = {'console_scripts':
            ['{0} = pybliotecario.pybliotecario:main'.format(pybliotecario_name),]
            },
)

print("""

##############
Installed pybliotecario as {0}

IMPORTANT: Don't forget to run
      ~$ {0} --init
for proper configuration of the pybliotecario""".format(pybliotecario_name))
