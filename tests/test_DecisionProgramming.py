import DecisionProgramming as dp
import os
import pytest
import numpy as np


def test_setupProject():
    '''
    Check that the setupProject function creates an
    environment.
    '''
    if os.path.exists("Manifest.toml"):
        os.remove("Manifest.toml")

    if os.path.exists("Project.toml"):
        os.remove("Project.toml")

    dp.setupProject()

    assert(os.path.exists("Manifest.toml"))


def test_activate():
    '''
    Check that DecisionProgramming is available after
    dp.activate()
    '''
    if not os.path.exists("Manifest.toml"):
        dp.setupProject()

    dp.activate()

    # If everything is correct, at least InfluenceDiagram
    # should be defined
    assert(dp.julia.eval("isdefined(Main, :InfluenceDiagram)"))


def test_random_number_generator():
    '''
    Check that the random_number_generator() returns a
    JuliaName and that the name is defined.
    '''

    generator = dp.juliaUtils.random_number_generator()
    name = generator._name

    assert(dp.julia.eval(f"isdefined(Main, :{name})"))


def test_JuliaMain():
    '''
    Check setting and fetching values with JuliaMain.
    dp.julia is an instance of JuliaMain
    '''

    # fetching thisisinotdefined should raise an
    # AttributeError
    with pytest.raises(AttributeError):
        x = dp.julia.thisisinotdefined

    # Now set it
    dp.julia.thisisinotdefined = 5

    # and it should be fetchable
    assert(dp.julia.thisisinotdefined == 5)

    # use eval to set something and try to fetch it
    dp.julia.eval("anotherthing = 4")
    assert(dp.julia.anotherthing == 4)


def test_handle_index_syntax():
    '''
    Check handle_index_syntax with a few examples
    '''

    handle = dp.juliaUtils.handle_index_syntax

    assert(handle(1)==2)
    assert(handle('a')=='"a"')
    assert(handle(slice(None))==':')
    assert(handle(("a",1,5,slice(None)))=='"a",2,6,:')
    assert(handle((slice(None),'a',slice(None),5))==':,"a",:,6')


@pytest.fixture
def julianame1():
    name = dp.JuliaName()
    dp.julia.eval(f'''
        {name._name} = 1
    ''')
    return name


@pytest.fixture
def julianame2():
    name = dp.JuliaName()
    dp.julia.eval(f'''
        {name._name} = 2
    ''')
    return name


@pytest.fixture
def diagram_simple():
    diagram = dp.InfluenceDiagram()
    D = dp.DecisionNode("D", [], ["1", "2"])
    diagram.add_node(D)
    O = dp.ChanceNode("O", [], ["lemon", "peach"])
    diagram.add_node(O)
    V = dp.ValueNode("V", ["D","O"])
    diagram.add_node(V)
    diagram.generate_arcs()

    X_C = diagram.construct_probability_matrix("O")
    X_C[0] = 1
    diagram.set_probabilities("O", X_C)

    Y_V1 = diagram.construct_utility_matrix("V")
    Y_V1[0,:] = [1,0]
    Y_V1[1,:] = [0,1]
    diagram.set_utility("V", Y_V1)

    diagram.generate()
    return diagram


class TestJuliaName():
    def test_init(self, julianame1, julianame2):
        '''
        Test that a name is initialized
        '''
        assert(type(julianame1._name) is str)

        # names should be unique
        assert(julianame1._name != julianame2._name)

    def test_repr(self, julianame1):
        '''
        Test that the __repr__ function returns a string
        '''
        assert(type(str(julianame1)) is str)

    def test_getattr(self, julianame1):
        '''
        Check accessing by attribute
        '''
        dp.julia.eval(f'''
            {julianame1._name} = InfluenceDiagram()
        ''')

        # This should return a JuliaName
        nodes = julianame1.Nodes
        assert(type(nodes) is dp.JuliaName)

        # Try getting an attribute that does not exist
        with pytest.raises(AttributeError):
            x = julianame1.doesnotexist

    def test_getitem(self, julianame1):
        '''
        Check item syntax
        '''
        # create and array in Julia and assign it to the name
        dp.julia.l = [1, 2, 3, 4]
        dp.julia.eval(f'''
            {julianame1._name} = l
        ''')

        # This should return JuliaName containing only the number
        n = julianame1[1]
        assert(type(n) is dp.JuliaName)
        # There is no direct way to fetch the number
        # directly. Let's check it anyway
        dp.julia.n = n
        assert(dp.julia.n == 2)

        # Try getting outside the array
        with pytest.raises(IndexError):
            x = julianame1[8]

        # Try getting outside the array
        with pytest.raises(IndexError):
            x = julianame1[8,4.0]

    def test_getslice(self, julianame1):
        '''
        Check slicing
        '''
        # create and array in Julia and assign it to the name
        dp.julia.l = [1, 2, 3, 4]
        dp.julia.eval(f'''
            {julianame1._name} = l
        ''')

        # This should return JuliaName containing only the number
        n = julianame1[:]
        assert(type(n) is dp.JuliaName)
        # There is no direct way to fetch the number
        # directly. Let's check it anyway
        dp.julia.n = n
        assert(dp.julia.n[0] == 1)

        # Try getting outside the array
        with pytest.raises(IndexError):
            x = julianame1[2:56]

    def test_setitem(self, julianame1):
        '''
        Check getting at index
        '''
        # create and array in Julia and assign it to the name
        dp.julia.l = [1, 2, 3, 4]
        dp.julia.eval(f'''
            {julianame1._name} = l
        ''')

        # set an entry
        julianame1[1] = 10
        dp.julia.n = julianame1
        assert(dp.julia.n[1] == 10)

        # Try setting outside the array
        with pytest.raises(IndexError):
            julianame1[15] = 5

    def test_setslice(self, julianame1):
        '''
        Check getting at index
        '''
        # create and array in Julia and assign it to the name
        dp.julia.l = [1, 2, 3, 4]
        dp.julia.eval(f'''
            {julianame1._name} = l
        ''')

        # set an entry
        julianame1[:] = [5, 6, 7, 8]
        dp.julia.n = julianame1
        assert(dp.julia.n[0] == 5)
        assert(dp.julia.n[1] == 6)
        assert(dp.julia.n[2] == 7)
        assert(dp.julia.n[3] == 8)


class TestInfluenceDiagram():

    def test_init(self):
        '''
        Test initializing a diagram
        '''
        diagram = dp.InfluenceDiagram()
        assert(type(diagram) is dp.InfluenceDiagram)

    def test_build_random(self):
        '''
        Test the building random diagram and setting
        random values.
        '''
        diagram = dp.InfluenceDiagram()
        diagram.build_random(2, 2, 2, 4, 4, [2, 3, 4])

        c = diagram.C[0]
        diagram.random_probabilities(c)

        v = diagram.V[0]
        diagram.random_utilities(v)

    def test_add_node_and_generate_arcs(self):
        '''
        Test adding a node and generate arcs. These
        are best tested together, since this allows
        accessing and checking the result easily.
        '''
        diagram = dp.InfluenceDiagram()
        O = dp.ChanceNode("O", [], ["1", "2"])
        diagram.add_node(O)

        D = dp.DecisionNode("D", ["O"], ["1", "2"])
        diagram.add_node(D)

        diagram.generate_arcs()
        # the _names are not the same, even if the
        # objects are
        # assert(diagram.C[0]._name == O._name)
        # assert(diagram.D[0]._name == D._name)

    def test_set_utility(self):
        '''
        Test setting utilities
        '''
        diagram = dp.InfluenceDiagram()
        D = dp.DecisionNode("D", [], ["1", "2"])
        diagram.add_node(D)
        V = dp.ValueNode("V", ["D"])
        diagram.add_node(V)
        V2 = dp.ValueNode("V2", ["D"])
        diagram.add_node(V2)

        diagram.generate_arcs()

        # try with a UtilityMatrix
        Y_V1 = diagram.construct_utility_matrix("V")
        Y_V1[0] = 1
        Y_V1[1] = 1
        diagram.set_utility("V", Y_V1)

        # Try with a numpy matrix
        Y_V2 = diagram.construct_utility_matrix("V2")
        Y_V2 = np.array([1.0, 1.0])
        diagram.set_utility("V2", Y_V2)

    def test_set_probabilities(self):
        '''
        Test setting probabilities
        '''
        diagram = dp.InfluenceDiagram()
        O = dp.ChanceNode("O", [], ["1", "2"])
        diagram.add_node(O)
        O2 = dp.ChanceNode("O2", [], ["1", "2"])
        diagram.add_node(O2)

        diagram.generate_arcs()

        # try with a ProbabilityMatrix
        X_C = diagram.construct_probability_matrix("O")
        X_C[0] = 1
        diagram.set_probabilities("O", X_C)

        # Try with a numpy matrix
        X_C = np.array([1,0])
        diagram.set_probabilities("O2", X_C)

    def test_num_states(self):
        '''
        Test getting the number of states
        '''
        diagram = dp.InfluenceDiagram()
        O = dp.ChanceNode("O", [], ["1", "2"])
        diagram.add_node(O)
        diagram.generate_arcs()

        n = diagram.num_states("O")
        assert(n == 2)

    def index_of(self):
        '''
        Test getting the number of states
        '''
        diagram = dp.InfluenceDiagram()
        O = dp.ChanceNode("O", [], ["1", "2"])
        diagram.add_node(O)
        diagram.generate_arcs()

        n = diagram.index_of("O")
        assert(n == 0)

    def test_decision_variables(self, diagram_simple):
        '''
        Test getting decision variables
        '''
        model = dp.Model()
        z = diagram_simple.decision_variables(model)
        assert(type(z) == dp.Diagram.DecisionVariables)

    @pytest.mark.with_gurobi
    def test_model_build(self, diagram_simple):
        '''
        Test getting path compatibility variable
        '''
        model = dp.Model()

        x_s = diagram_simple.path_compatibility_variables(model)
        assert(type(x_s) == dp.Diagram.PathCompatibilityVariables)

        EV = diagram_simple.expected_value(model, x_s)
        assert(type(EV) == dp.Diagram.ExpectedValue)

        model.objective(EV, "Max")
        model.setup_Gurobi_optimizer(
           ("IntFeasTol", 1e-9),
           ("LazyConstraints", 1)
        )
        model.optimize()

    @pytest.mark.with_gurobi
    def test_decision_strategy(self, diagram_simple):
        model = dp.Model()
        z = diagram_simple.decision_variables(model)
        x_s = diagram_simple.path_compatibility_variables(model, z)
        EV = diagram_simple.expected_value(model, x_s)
        model.objective(EV, "Max")

        model.setup_Gurobi_optimizer(
           ("IntFeasTol", 1e-9),
           ("LazyConstraints", 1)
        )
        model.optimize()

        Z = z.decision_strategy()
        assert(type(Z) == dp.Diagram.DecisionStrategy)

        S_probabilities = diagram_simple.state_probabilities(Z)
        assert(type(S_probabilities) == dp.Diagram.StateProbabilities)

        U_distribution = diagram_simple.utility_distribution(Z)
        assert(type(U_distribution) == dp.Diagram.UtilityDistribution)

