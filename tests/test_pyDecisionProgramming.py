import pyDecisionProgramming as pdp
import os
import pytest


def test_setupProject():
    '''
    Check that the setupProject function creates an
    environment.
    '''
    if not os.path.exists("Manifest.toml"):
        os.remove("Manifest.toml")

    pdp.setupProject()

    assert(os.path.exists("Manifest.toml"))


def test_random_number_generator():
    '''
    Check that the random_number_generator() returns a
    JuliaName and that the name is defined.
    '''

    generator = pdp.random_number_generator()
    name = generator._name

    assert(pdp.julia.eval(f"isdefined(Main, :{name})"))


def test_JuliaMain():
    '''
    Check setting and fetching values with JuliaMain.
    pdp.julia is an instance of JuliaMain
    '''

    # fetching thisisinotdefined should raise an
    # AttributeError
    with pytest.raises(AttributeError):
        x = pdp.julia.thisisinotdefined

    # Now set it
    pdp.julia.thisisinotdefined = 5

    # and it should be fetchable
    assert(pdp.julia.thisisinotdefined == 5)


