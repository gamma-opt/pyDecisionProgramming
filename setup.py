from setuptools import setup
from os import path

package_path = path.abspath(path.dirname(__file__))
print(package_path)
# Load requirements from requirements.txt
requirements = path.join(package_path, "requirements.txt")
with open(requirements, "r") as requirements_file:
    requirements = [line.strip() for line in requirements_file if line.strip()]

# Load the README file as the long description
readme = path.join(package_path, "README.md")
with open(readme, "r") as readme_file:
    long_description = readme_file.read()

setup(
   name='DecisionProgramming',
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
   packages=['DecisionProgramming'],
   scripts=['scripts/pdp_setup_julia.jl'],
   install_requires=requirements
)
