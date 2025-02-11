import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrotation",
    version="0.0.2",
    author="Christof Dubs",
    author_email="christof.dubs@gmx.ch",
    description="A numpy-based rotation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChristofDubs/pyrotation",
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    license='MIT',
)
