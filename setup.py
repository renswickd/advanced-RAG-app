from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="End-to-End RAG Application",
    version="0.1",
    author="Renswick Delvar",
    packages=find_packages(),
    install_requires = requirements,
)