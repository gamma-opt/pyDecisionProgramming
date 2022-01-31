from setuptools import setup

setup(
   name='pyDecisionProgramming',
   version='0',
   description='Python interface for DecisionProgramming.jl',
   author='Jarno Rantaharju',
   author_email='jarno.rantaharju@aalto.fi',
   packages=['pyDecisionProgramming'],
   scripts=['pyDecisionProgramming/pdp_setup_julia.jl'],
   requires=['julia']
)
