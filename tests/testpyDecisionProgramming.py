import pyDecisionProgramming as pdp
import os


def test_setupProject():
    '''
    Check that the setupProject function creates an
    environment.
    '''
    if not os.path.exists("Manifest.toml"):
        os.remove("Manifest.toml")

    pdp.setupProject()

    assert(os.path.exists("Manifest.toml"))



