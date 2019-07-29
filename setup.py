from setuptools import setup, find_packages

setup(
        name="pybliotecario",
        version="1.0",
        package_dir = {'':'src'},
        packages=find_packages('src'),

        entry_points = {'console_scripts':
            ['pybliotecario = pybliotecario.pybliotecario:main',]
            },
)
