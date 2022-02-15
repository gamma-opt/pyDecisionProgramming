from setuptools import setup
from os.path import join, dirname

# Load requirements from requirements.txt
requirementstxt = join(dirname(__file__), "requirements.txt")
with open(requirementstxt, "r") as requirements_file:
    requirements = [line.strip() for line in requirements_file if line.strip()]

# Load the README file as the long description
readme = join(dirname(__file__), "README.md")
with open(readme, "r") as readme_file:
    long_description = readme_file.read()

setup(
   name='pyDecisionProgramming',
   version='1.0',
   description='Python interface for DecisionProgramming.jl',
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://github.com/gamma-opt/pyDecisionProgramming",
   project_urls={
        "Bug Tracker": "https://github.com/gamma-opt/pyDecisionProgramming/issues",
        "Documentation": "https://gamma-opt.github.io/pyDecisionProgramming",
    },
   author='Jarno Rantaharju',
   author_email='jarno.rantaharju@aalto.fi',
   license="MIT",
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
   packages=['pyDecisionProgramming'],
   scripts=['scripts/pdp_setup_julia.jl'],
   install_requires=requirements
)
