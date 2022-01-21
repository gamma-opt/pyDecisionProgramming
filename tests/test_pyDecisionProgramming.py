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


def test_activate():
    '''
    Check that DecisionProgramming is available after
    pdp.activate()
    '''
    if not os.path.exists("Manifest.toml"):
        pdp.setupProject()

    pdp.activate()

    # If everything is correct, at least InfluenceDiagram
    # should be defined
    assert(pdp.julia.eval("isdefined(Main, :InfluenceDiagram)"))


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

    # use eval to set something and try to fetch it
    pdp.julia.eval("anotherthing = 4")
    assert(pdp.julia.anotherthing == 4)


def test_handle_index_syntax():
    '''
    Check handle_index_syntax with a few examples
    '''

    handle = pdp.handle_index_syntax

    assert(handle(1)==2)
    assert(handle('a')=='"a"')
    assert(handle(slice(None))==':')
    assert(handle(("a",1,5,slice(None)))=='"a",2,6,:')
    assert(handle((slice(None),'a',slice(None),5))==':,"a",:,6')


class TestJuliaName():
    def __init__(self):
        self.name1 = pdp.JuliaName()
        self.name2 = pdp.JuliaName()

    def test_init(self):
        '''
        Test that a name is initialized
        '''
        assert(type(self.name1._name) is str)

        # names should be unique
        assert(self.name1._name != self.name2._name)

    def test_get_attr(self):
        '''
        Check accessing by attribute
        '''
        pdp.Main.eval(f'''
            {self.name1._name} = InfluenceDiagram()
        ''')

        # This should return a JuliaName
        u = self.name1.U
        assert(type(u) is pdp.JuliaName)

        # Try getting an attribute that does not exist
        with pytest.raises(AttributeError):
            x = self.name1.doesnotexist


