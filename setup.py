from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="grogui",
    version="2.0.0",
    author="Mustapha Belaidi",
    author_email="mustapha.belaidi@example.com",
    description="GROMACS Molecular Dynamics Simulation Runner & Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mustaphabelaidi-spec/grogui",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "grogui=grogui.gui.main_window:main",
        ],
    },
)
