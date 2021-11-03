import setuptools

setuptools.setup(
    name = "PyMtk",
    version = "0.0.1",
    description = "MML:n maastotietokannan kohteet",
    scripts = ['PyMtk.py'],
    packages=setuptools.find_packages(),
    install_requires = [
        'PySide2>=5,<6'
    ],
    classifiers = [
        "Programming Language :: Python :: 3"
    ]
)
