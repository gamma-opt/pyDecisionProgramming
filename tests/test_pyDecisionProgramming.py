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


@pytest.fixture
def julianame1():
    return pdp.JuliaName()


@pytest.fixture
def julianame2():
    return pdp.JuliaName()


class TestJuliaName():
    def test_init(self, julianame1, julianame2):
        '''
        Test that a name is initialized
        '''
        assert(type(julianame1._name) is str)

        # names should be unique
        assert(julianame1._name != julianame2._name)

    def test_getattr(self, julianame1):
        '''
        Check accessing by attribute
        '''
        pdp.Main.eval(f'''
            {julianame1._name} = InfluenceDiagram()
        ''')

        # This should return a JuliaName
        nodes = julianame1.Nodes
        assert(type(nodes) is pdp.JuliaName)

        # Try getting an attribute that does not exist
        with pytest.raises(AttributeError):
            x = julianame1.doesnotexist

    def test_getitem(self, julianame1):
        '''
        Check item syntax
        '''
        # create and array in Julia and assign it to the name
        pdp.julia.l = [1, 2, 3, 4]
        pdp.Main.eval(f'''
            {julianame1._name} = l
        ''')

        # This should return JuliaName containing only the number
        n = julianame1[1]
        assert(type(n) is pdp.JuliaName)
        # There is no direct way to fetch the number
        # directly. Let's check it anyway
        pdp.julia.n = n
        assert(pdp.julia.n == 2)

        # Try getting outside the array
        with pytest.raises(IndexError):
            x = julianame1[8]

    def test_getslice(self, julianame1):
        '''
        Check slicing
        '''
        # create and array in Julia and assign it to the name
        pdp.julia.l = [1, 2, 3, 4]
        pdp.Main.eval(f'''
            {julianame1._name} = l
        ''')

        # This should return JuliaName containing only the number
        n = julianame1[:]
        assert(type(n) is pdp.JuliaName)
        # There is no direct way to fetch the number
        # directly. Let's check it anyway
        pdp.julia.n = n
        assert(pdp.julia.n[0] == 1)

        # Try getting outside the array
        with pytest.raises(IndexError):
            x = julianame1[2:56]

    def test_setitem(self, julianame1):
        '''
        Check getting at index
        '''
        # create and array in Julia and assign it to the name
        pdp.julia.l = [1, 2, 3, 4]
        pdp.Main.eval(f'''
            {julianame1._name} = l
        ''')

        # set an entry
        julianame1[1] = 10
        pdp.julia.n = julianame1
        assert(pdp.julia.n[1] == 10)

        # Try setting outside the array
        with pytest.raises(IndexError):
            julianame1[15] = 5

