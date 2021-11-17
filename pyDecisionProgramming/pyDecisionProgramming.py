from julia import Pkg
from julia import Main
from julia import DecisionProgramming as jdp
import uuid


class JuliaMain():
    '''
    Maps to julia.main from the julia library, unless the setting
    an object implemented here (inherits JuliaName). JuliaNames are
    assigned directly.
    '''

    def __setattr__(self, name, value):
        if type(value) == JuliaName or JuliaName in type(value).__bases__:
            print(name)
            Main.eval(f'{name} = {value._name}')
        else:
            Main.__setattr__(name, value)

    def __getattr__(self, name):
        if Main.eval(f"isdefined(Main, :{name})"):
            return Main.__getattr__(name)
        else:
            return None

    def eval(self, command):
        return Main.eval(command)


julia = JuliaMain()


def activate():
    """ Activate a Julia environment in the working
        directory and load requirements
    """

    Pkg.activate(".")
    Main.eval('using DecisionProgramming')
    Main.eval('using Gurobi')
    Main.eval('using JuMP')


def setupProject():
    """ Activate a Julia environment in the working
        directory and install DecisionProgramming,
        Gurobi and JuMP
    """

    Pkg.activate(".")
    github_url = "https://github.com/gamma-opt/DecisionProgramming.jl.git"
    Pkg.add(url=github_url)
    Pkg.add("Gurobi")
    Pkg.build("Gurobi")
    Pkg.add("JuMP")

    Main.eval('using DecisionProgramming')
    Main.eval('using Gurobi')
    Main.eval('using JuMP')


def handle_index_syntax(key):
    """
    Turn a key tuple into Julia slicing and indexing syntax

    Parameters
    ----------
    key: String, integer, slice or a tuple of these
    """
    if isinstance(key, tuple):
        indexes = []
        for index in key:
            if index == slice(None):
                indexes += ':'
            elif isinstance(index, str):
                indexes += [f'"{index}"']
            elif isinstance(index, int):
                indexes += [str(index+1)]
            else:
                raise IndexError('Index not must be string, integer or string')
        index_string = ','.join(indexes)

    elif key == slice(None):
        index_string = ':'
    elif isinstance(key, str):
        index_string = f'"{key}"'
    elif isinstance(key, int):
        index_string = key+1
    else:
        raise IndexError('Index not must be string, integer or string')

    return index_string


class JuliaName():
    '''
    Base class for all following Julia objects. Stores the object
    name in the Julia main name space and defines string
    representation from Julia.
    '''
    def __init__(self):
        self._name = 'pyDP'+uuid.uuid4().hex[:10]

    def __str__(self):
        return Main.eval(f'repr({self._name})')

    def __repr__(self):
        return Main.eval(f'repr({self._name})')

    def __getattr__(self, name):
        if Main.eval(f"isdefined(Main, :{self._name})") and Main.eval(f"hasproperty({self._name}, :{name})"):
            r = JuliaName()
            Main.eval(f'{r._name} = {self._name}.{name}')
            return r
        return None

    def __getitem__(self, key):
        r = JuliaName()
        index_string = handle_index_syntax(key)
        Main.eval(f'{r._name} = {self._name}[{index_string}]')
        return r

    def __getslice__(self, key):
        r = JuliaName()
        index_string = handle_index_syntax(key)
        Main.eval(f'{r._name} = {self._name}[{index_string}]')
        return r

    def __setitem__(self, key, value):
        index_string = handle_index_syntax(key)
        Main.eval(f'{self._name}[{index_string}] = {value}')

    def __setslice__(self, key, value):
        index_string = handle_index_syntax(key)
        Main.eval(f'{self._name}[{index_string}] = {value}')


class InfluenceDiagram(JuliaName):
    '''
    Holds information about the influence diagram, including nodes
    and possible states.

    See the latest documentation for the Julia type at
    (https://gamma-opt.github.io/DecisionProgramming.jl/dev/api/).

    Methods
    -------
    add_node(node)
        Add a node to the influence diagram. The node can a ChanceNode,
        DecisionNode, or a ValueNode.

    generate_arcs()
        Generate arc structures using nodes added to influence diagram, by
        ordering nodes, giving them indices and generating correct values for
        the vectors Names, I_j, states, S, C, D, V in the influence diagram.
        Abstraction is created and the names of the nodes and states are only
        used in the user interface from here on.

    set_probabilities(change_node_name, matrix)
        Set the probability matrix at a given node. The matrix is a Numpy
        array. You can use the probability_matrix-method to find the matrix
        size.

    set_utility(value_node_name, matrix)
        Set the utility matrix at a given node. The matrix is a Numpy
        array. You can use the utility_matrix-method to find the matrix
        size.

    generate(
               default_probability=True,
               default_utility=True,
               positive_path_utility=False,
               negative_path_utility=False
            )
        Generate complete influence diagram with probabilities and utilities as well.
    '''

    def __init__(self):
        super().__init__()
        Main.eval(f'{self._name} = InfluenceDiagram()')

    def add_node(self, node):
        """
        Parameters
        ----------
        node : ChanceNode, DecisionNode, or ValueNode
        """
        command = f'add_node!({self._name}, {node._name})'
        Main.eval(command)

    def generate_arcs(self):
        Main.eval(f'generate_arcs!({self._name})')

    def set_probabilities(self, node, matrix):
        """set_probabilities
        Parameters
        ----------
        node : str
            The name of a ValueNode. The probability matrix of this node is
            returned.

        matrix : ProbabilityMatrix or Numpy array
            The probability matrix that replaces the current one. May be a
            ProbabilityMarix of a Numpy array.
        """
        if isinstance(matrix, ProbabilityMatrix):
            Main.eval(f'''add_probabilities!(
                {self._name},
                "{node}",
                {matrix._name})
            ''')
        else:
            Main.tmp = matrix
            Main.eval('tmp = convert(Array{Float64}, tmp)')
            Main.eval(f'add_probabilities!({self._name}, "{node}", tmp)')

    def set_utility(self, value, matrix):
        """
        Parameters
        ----------
        node : str
            The name of a ValueNode. The probability matrix of this node is
            returned.

        matrix : Numpy array
            The probability matrix that replaces the current one.
        """
        if isinstance(matrix, UtilityMatrix):
            Main.eval(f'''add_utilities!(
                {self._name},
                "{value}",
                {matrix._name})
            ''')
        else:
            Main.tmp = matrix
            Main.eval('tmp = convert(Array{Float64}, tmp)')
            Main.eval(f'add_utilities!({self._name}, "{value}", tmp)')

    def generate(self,
                 default_probability=True,
                 default_utility=True,
                 positive_path_utility=False,
                 negative_path_utility=False
                 ):
        """
        Parameters
        ----------
            default_probability: bool = True
                Choice to use default path probabilities

            default_utility: bool = True
                Choice to use default path utilities

            positive_path_utility : bool = False
                Choice to use a positive path utility translation

            negative_path_utility : bool = False
                Choice to use a negative path utility translation
        """
        Main.tmp1 = default_probability
        Main.tmp2 = default_utility
        Main.tmp3 = positive_path_utility
        Main.tmp4 = negative_path_utility
        Main.eval(f'''generate_diagram!(
            {self._name};
            default_probability=tmp1,
            default_utility=tmp2,
            positive_path_utility=tmp3,
            negative_path_utility=tmp4
        )''')

    def num_states(self, node):
        Main.eval(f'''tmp = num_states(
            {self._name}, "{node}"
        )''')
        return Main.tmp


class Model(JuliaName):
    """
    Wraps a JuMP optimizer model and decision model variables.

    Methods
    -------
    setup_Gurobi_optimizer(*constraints):
        Create a Gurobi optimizer with a given set of contraints.

    optimize():
        Run the optimizer.
    """
    def __init__(self):
        super().__init__()
        Main.eval(f'{self._name} = Model()')

    def setup_Gurobi_optimizer(self, *constraints):
        '''
        Parameters
        ----------
        constraints -- Tuple
            Formatted as (constraint_name, constraint_value)
        '''

        command = '''optimizer = optimizer_with_attributes(
                     () -> Gurobi.Optimizer(Gurobi.Env())'''

        for constraint in constraints:
            command += f''',
                         "{constraint[0]}" => {constraint[1]}'''

        command += ')'

        Main.eval(command)
        Main.eval(f'set_optimizer({self._name}, optimizer)')

    def objective(self, op, expected_value):
        """
        Set the objective for the optimizer

        Parameters
        ----------
        op: "Min" or "Max"
            Whether to minimize or maximize the objective

        expected_value: ExpectedValue
            An ExpectedValue object. Describes the objective function.
        """
        Main.eval(f'@objective({self._name}, Max, {expected_value._name})')

    def optimize(self):
        ''' Run the current optimizer '''

        Main.eval(f'optimize!({self._name})')

    def constraint(self, *args):
        print(args)
        argument_text = ",".join(args)
        print(argument_text)
        Main.eval(f'''@constraint(
            {self._name},
            {argument_text}
        )''')


class JuMP_Variable(JuliaName):
    def __init__(self, model, size, binary=False):
        size_string = str(size).replace("\'", "\"")
        binary_arg = ""
        if binary:
            binary_arg = "; binary=true, "
        # Note: ending the command with ;0 to prevent
        # Julia from returning the object. Otherwise
        # the Python julia library will try to convert
        # this to a Python object and cause an exception.
        command = f'''tmp = @variable(
            {model._name},
            {size_string}
            {binary_arg}
        ); 0'''
        Main.eval(command)


class DecisionVariables(JuliaName):
    """
    Create decision variables and constraints.
    """

    def __init__(self, model, diagram, names=False, name="z"):
        """
        Parameters
        ----------
        model: Model
            A pyDecisionProgramming Model object

        diagram: Diagram
            A pyDecisionProgramming Diagram object

        names: bool
            Use names or have anonymous Jump variables

        name: str
            Prefix for predefined decision variable naming convention
        """
        super().__init__()
        self.diagram = diagram
        self.model = model
        Main.tmp1 = names
        Main.tmp2 = name
        commmand = f'''{self._name} = DecisionVariables(
            {model._name},
            {diagram._name};
            names=tmp1,
            name=tmp2
        )'''
        Main.eval(commmand)


class PathCompatibilityVariables(JuliaName):
    """
    Create path compatibility variables and constraints

    Attributes
    ----------
    diagram: InfluenceDiagram
        An influence diagram.

    decision_variables: DecisionVariables
        A set of decision variables for the diagram

    Methods
    -------
    expected_value()
        Create an expected value objective.
    """
    def __init__(self,
                 model,
                 diagram,
                 decision_variables,
                 names=False,
                 name="x",
                 # TODO: forbidden_paths=ForbiddenPath([]),
                 # TODO: fixed=FixedPath(),
                 probability_cut=True,
                 probability_scale_factor=1.0
                 ):
        """
        Parameters
        ----------
        model: Model
            JuMP model into which variables are added.

        diagram: InfluenceDiagram
            Influence diagram structure.

        decision_variables: DecisionVariables
            A set of decision variables for the diagram.

        names: bool
            Use names or have JuMP variables be anonymous.

        name: str
            Prefix for predefined decision variable naming convention.

        forbidden_paths: list of ForbiddenPath objects:
            The forbidden subpath structures. Path compatibility variables
            will not be generated for paths that include forbidden subpaths.

        fixed: FixedPath
            Path compatibility variable will not be generated for paths which
            do not include these fixed subpaths.

        probability_cut: bool
            Includes probability cut constraint in the optimisation model.

        probability_scale_factor: float
            Adjusts conditional value at risk model to be compatible with the
            expected value expression if the probabilities were scaled there.
        """
        super().__init__()
        self.model = model
        self.diagram = diagram
        self.decision_variables = decision_variables
        Main.tmp1 = names
        Main.tmp2 = name
        # TODO: Main.tmp3 = forbidden_paths
        # TODO: Main.tmp4 = fixed
        Main.tmp5 = probability_cut
        Main.tmp6 = probability_scale_factor
        commmand = f'''{self._name} = PathCompatibilityVariables(
            {model._name},
            {diagram._name},
            {decision_variables._name};
            names = tmp1, name = tmp2,
            probability_cut = tmp5,
            probability_scale_factor = tmp6
        )'''
        Main.eval(commmand)


class ExpectedValue(JuliaName):
    """
    An expected value object JuMP can minimize on maximize
    """
    def __init__(self, model, diagram, pathcompatibility):
        """
        Parameters
        ----------
        model: Model

        diagram: Diagram

        pathcompatibility: PathCompatibilityVariables

        """
        super().__init__()
        commmand = f'''{self._name} = expected_value(
            {model._name},
            {diagram._name},
            {pathcompatibility._name}
        )'''
        Main.eval(commmand)


class DecisionStrategy(JuliaName):
    """
    Extract values for decision variables from solved decision model.
    """
    def __init__(self, decision_variables):
        """
        Parameters
        ----------
        A decision variables for a solved model
        """
        super().__init__()
        commmand = f'{self._name} = DecisionStrategy({decision_variables._name})'
        Main.eval(commmand)


class StateProbabilities(JuliaName):
    """
    Extract state propabilities from a solved model

    Methods
    -------
    print_decision_strategy()
        Pretty print the decision strategy

    print()
        Pretty print state probabilities for a list of nodes
    """
    def __init__(self, diagram, decision_strategy):
        super().__init__()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = StateProbabilities({diagram._name}, {decision_strategy._name})'
        Main.eval(commmand)

    def print_decision_strategy(self):
        Main.eval(f'''print_decision_strategy(
            {self.diagram._name},
            {self.decision_strategy._name},
            {self._name})''')

    def print(self, nodes):
        # Format the nodes list using " instead of '
        node_string = str(nodes).replace("\'", "\"")
        Main.eval(f'''print_state_probabilities(
            {self.diagram._name},
            {self._name},
            {node_string})''')


class UtilityDistribution(JuliaName):
    """
    Extract utility distribution from a solved model

    Methods
    -------
    print_distribution()
        Pretty print the utility distribution

    print_statistics()
        Pretty print statistics
    """
    def __init__(self, diagram, decision_strategy):
        """
        Parameters
        ----------
        diagram: Diagram
            The diagram of a solved model

        decision_strategy: DecisionStrategy
            A decition strategy extracted from a solved model.
        """
        super().__init__()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = UtilityDistribution({diagram._name}, {decision_strategy._name})'
        Main.eval(commmand)

    def print_distribution(self):
        Main.eval(f'''print_utility_distribution({self._name})''')

    def print_statistics(self):
        Main.eval(f'''print_statistics({self._name})''')


class ChanceNode(JuliaName):
    """
    Create a change node that can be added into a Diagram
    """
    def __init__(self, id, nodes, connected_nodes):
        '''
        Parameters
        ----------
        id: str
            The id of the node

        nodes: list(str)
            List of nodes connected to this node

        connected_nodes:
            List of node connected_nodes
        '''

        super().__init__()

        Main.tmp = jdp.ChanceNode(id, nodes, connected_nodes)
        Main.eval(f'{self._name} = tmp')


class DecisionNode(JuliaName):
    """
    Create a decision node that can be added into a Diagram
    """
    def __init__(self, id, nodes, connected_nodes):
        '''
        Parameters
        ----------
        id: str
            The id of the node

        nodes: list(str)
            List of nodes connected to this node

        connected_nodes:
            List of node connected_nodes
        '''

        super().__init__()
        Main.tmp = jdp.DecisionNode(id, nodes, connected_nodes)
        Main.eval(f'{self._name} = tmp')


class ValueNode(JuliaName):
    """
    Create a value node that can be added into a Diagram
    """
    def __init__(self, id, nodes):
        '''
        Parameters
        ----------
        id: str
            The id of the node

        nodes: list(str)
            List of nodes connected to this node

        connected_nodes:
            List of node connected_nodes
        '''

        super().__init__()

        Main.tmp = jdp.ValueNode(id, nodes)
        Main.eval(f'{self._name} = tmp')


class ProbabilityMatrix(JuliaName):
    """
    Construct an empty probability matrix for a chance node.
    """
    def __init__(self, diagram, node):
        """
        Parameters
        ----------
        diagram: Diagram
           The influence diagram that contains the node

        node : str
            The name of a ChanceNode. The probability matrix of this node is
            returned.
        """
        super().__init__()
        self.diagram = diagram
        Main.eval(f'''{self._name} = ProbabilityMatrix(
           {diagram._name},
           "{node}"
        )''')


class UtilityMatrix(JuliaName):
    """
    Construct an empty probability matrix for a chance node.
    """
    def __init__(self, diagram, node):
        """
        Parameters
        ----------
        diagram: Diagram
           The influence diagram that contains the node

        node : str
            The name of a ChanceNode. The probability matrix of this node is
            returned.
        """
        super().__init__()
        self.diagram = diagram
        Main.eval(f'''{self._name} = UtilityMatrix(
           {diagram._name},
           "{node}"
        )''')


class Paths():
    def __init__(self, states, fixed=None):
        Main.eval(f'tmp = States(State.({states}))')
        if fixed == None:
            Main.eval('tmp = paths(tmp)')
        else:
            Main.eval(f'tmp = paths(tmp; fixed={fixed})')
        self.paths = Main.tmp

    def __iter__(self):
        self._iterator = iter(Main.tmp)
        return self

    def __next__(self):
        path = next(self._iterator)
        if path:
            path = [i-1 for i in path]
        return path

