from setuptools import setup
from os.path import join, dirname

requirementstxt = join(dirname(__file__), "requirements.txt")
requirements = [line.strip() for line in open(requirementstxt, "r") if line.strip()]

setup(
   name='pyDecisionProgramming',
   version='0',
   description='Python interface for DecisionProgramming.jl',
   author='Jarno Rantaharju',
   author_email='jarno.rantaharju@aalto.fi',
   packages=['pyDecisionProgramming'],
   scripts=['scripts/pdp_setup_julia.jl'],
   install_requires=requirements
)
