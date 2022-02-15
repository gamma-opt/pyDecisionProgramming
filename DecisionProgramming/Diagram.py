''' Interface for Jump functionality necessary for optimizing models generated
from diagrams.
'''
from .juliaUtils import JuliaName
from .juliaUtils import random_number_generator
from .juliaUtils import julia


class InfluenceDiagram(JuliaName):
    ''' Holds information about the influence diagram, including nodes
    and possible states.

    See the latest documentation for the Julia type at
    (https://gamma-opt.github.io/DecisionProgramming.jl/dev/api/).

    '''

    def __init__(self):
        super().__init__()
        julia.eval(f'{self._name} = InfluenceDiagram()')

    def build_random(self, n_C, n_D, n_V, m_C, m_D, states, seed=None):
        ''' Generate random decision diagram with n_C chance nodes, n_D
        decision nodes, and n_V value nodes. Parameter m_C and m_D are the
        upper bounds for the size of the information set.

        Parameters
        ----------
        n_C: Int
            Number of chance nodes.
        n_D: Int
            Number of decision nodes.
        n_V: Int
            Number of value nodes.
        m_C: Int
            Upper bound for size of information set for chance nodes.
        m_D: Int
            Upper bound for size of information set for decision nodes.
        states: List if integers
            The number of states for each chance and decision node is
            randomly chosen from this set of numbers.

        '''
        rng = random_number_generator(seed)
        julia.eval(f'''
            random_diagram!(
                {rng._name}, {self._name},
                {n_C}, {n_D}, {n_V}, {m_C}, {m_D},
                {str(states)}
            )
        ''')

    def random_probabilities(self, node, n_inactive=0, seed=None):
        ''' Generate random probabilities for a chance node.

        Parameters
        ----------
        node: dp.ChanceNode
            Random probabilities will be assigned to this node.

        n_inactive: Int
            Number of inactive states

        '''
        rng = random_number_generator(seed)
        print(rng)
        julia.eval(f'''
            random_probabilities!(
                {rng._name}, {self._name},
                {node._name}; n_inactive={n_inactive}
            )
        ''')

    def random_utilities(self, node, low=-1.0, high=1.0, seed=None):
        ''' Generate random utilities for a value node.

        Parameters
        ----------
        node: dp.ValueNode
            Random utilities are generated for this node

        low: float
            Lower bound for random utilities

        high: float
            Upper bound for random utilities

        seed: int
            Seed for the random number generator

        '''
        rng = random_number_generator(seed)
        julia.eval(f'''
            random_utilities!(
                {rng._name}, {self._name},
                {node._name}; low={low}, high={high}
            )
        ''')

    def add_node(self, node):
        """ Add a node to the diagram

        Parameters
        ----------
        node : ChanceNode, DecisionNode, or ValueNode

        """
        command = f'add_node!({self._name}, {node._name})'
        julia.eval(command)

    def generate_arcs(self):
        ''' Generate arc structures using nodes added to influence diagram, by ordering nodes, giving them indices and generating correct values for the vectors Names, I_j, states, S, C, D, V in the influence digram. Abstraction is created and the names of the nodes and states are only used in the user interface from here on.

        '''
        julia.eval(f'generate_arcs!({self._name})')

    def set_probabilities(self, node, matrix):
        """ Set the probabilities of a ChanceNode

        Parameters
        ----------
        node : str
            The name of a ChanceNode. The probability matrix of this node is
            returned.

        matrix : ProbabilityMatrix or Numpy array
            The probability matrix that replaces the current one. May be a
            ProbabilityMarix of a Numpy array.

        """
        if isinstance(matrix, ProbabilityMatrix):
            julia.eval(f'''add_probabilities!(
                {self._name},
                "{node}",
                {matrix._name})
            ''')
        else:
            julia.tmp = matrix
            julia.eval('tmp = convert(Array{Float64}, tmp)')
            julia.eval(f'add_probabilities!({self._name}, "{node}", tmp)')

    def set_utility(self, value, matrix):
        """ Set the utilities of a ValueNode

        Parameters
        ----------
        node : str
            The name of a ValueNode. The probability matrix of this node is
            returned.

        matrix : Numpy array
            The probability matrix that replaces the current one.

        """
        if isinstance(matrix, UtilityMatrix):
            julia.eval(f'''add_utilities!(
                {self._name},
                "{value}",
                {matrix._name})
            ''')
        else:
            julia.tmp = matrix
            julia.eval('tmp = convert(Array{Float64}, tmp)')
            julia.eval(f'add_utilities!({self._name}, "{value}", tmp)')

    def generate(self,
                 default_probability=True,
                 default_utility=True,
                 positive_path_utility=False,
                 negative_path_utility=False
                 ):
        """ Generate the diagram once nodes, probabilities and utilities
        have been added.

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
        julia.default_probability = default_probability
        julia.default_utility = default_utility
        julia.positive_path_utility = positive_path_utility
        julia.negative_path_utility = negative_path_utility
        julia.eval(f'''generate_diagram!(
            {self._name};
            default_probability=default_probability,
            default_utility=default_utility,
            positive_path_utility=positive_path_utility,
            negative_path_utility=negative_path_utility
        )''')

    def num_states(self, node):
        ''' Find the number of states a given node has.

        Parameters
        ----------
        node: String
            The name of a node

        Returns
        -------
        Integer
            The number of states the given node has

        '''
        julia.eval(f'''tmp = num_states(
            {self._name}, "{node}"
        )''')
        return julia.tmp

    def index_of(self, name):
        ''' Find index of a given node.

        Parameters
        ----------
        node: String
            The name of a node

        Returns
        -------
        Integer
            The index of the node in the diagram

        '''
        return julia.eval(f'''index_of({self._name}, "{name}")''')-1

    def set_path_utilities(self, expressions):
        ''' Use given expression as the path utilities of the diagram.

        Parameters
        ----------
        expressions: ExpressionPathUtilities
            A set of JuMP expression.

        '''
        julia.eval(f'''
            {self._name}.U = PathUtility({expressions._name})
        ''')

    def construct_probability_matrix(self, node):
        ''' Return a probability matrix with appriate dimensions for a given node
        and zero values.

        Parameters
        ----------
        node: String
            The name of a ChanceNode.

        Returns
        -------
        dp.ProbabilityMatrix
            A probabity matrix with zero values.

        '''
        return ProbabilityMatrix(self, node)

    def construct_utility_matrix(self, node):
        ''' Return a utility matrix with appriate dimensions for a given node
        and values set to negative infinity.

        Parameters
        ----------
        node: String
            The name of a UtilityMatrix.

        Returns
        -------
        dp.UtilityMatrix
            A utility matrix with values set to negative infinity.

        '''
        return UtilityMatrix(self, node)

    def decision_variables(self, model):
        ''' Construct the decision variables for a given model and this diagram.

        Parameters
        ----------
        model: dp.Model
            A model constructed for this diagram.

        Returns
        -------
        dp.DecisionVariables
            The set of decision variables for the model.

        '''
        return DecisionVariables(model, self)

    def path_compatibility_variables(
        self, model,
        decision_variables=None,
        names=False,
        name="x",
        forbidden_paths=None,
        fixed=None,
        probability_cut=True,
        probability_scale_factor=1.0
    ):
        ''' Construct the path compatibility variables for a given model and this
        diagram.

        Parameters
        ----------
        model: dp.Model
            A model constructed for this diagram.
        decision variables: dp.DecisionVariables (optional)
            DecisionVariables constructed for this model.
        names: Bool (optional)
        name: String (optional)
        forbidden_paths: List of dp.ForbiddenPath variables (optional)
        fixed: List of dp.FixedPath variables (optional)
        probability_cut: Bool (optional)
        probability_scale_factor: Number (optional)

        Returns
        -------
        dp.PathCompatibilityVariables
            The set of path compatibility variables for the model.

        '''
        if decision_variables is None:
            decision_variables = self.decision_variables(model)
        return PathCompatibilityVariables(
            model, self,
            decision_variables,
            names=names,
            name=name,
            forbidden_paths=forbidden_paths,
            fixed=fixed,
            probability_cut=probability_cut,
            probability_scale_factor=probability_scale_factor
        )

    def expected_value(
        self, model,
        path_compatibility_variables=None
    ):
        ''' Return the expected value given the optimal decision strategy after
        optimizing the model.

        Parameters
        ----------
        model: dp.Model
            A model constructed for this diagram.
        path_compatibility_variables: dp.PathCompatibilityVariables (optional)
            PathCompatibilityVariables generated for this model, usually using
            diagram.path_compatibility_variables.

        Returns
        -------
        dp.ExpectedValue
            A dp.ExpectedValue object describing the expected value for the
            optimal decision strategy.

        '''
        x_s = path_compatibility_variables
        if x_s is None:
            x_s = self.path_compatibility_variables(model)
        return ExpectedValue(model, self, path_compatibility_variables)

    def state_probabilities(self, decision_strategy):
        ''' Extract the state probabilities as a dp.StateProbabilities object.

        Parameters
        ----------
        decision_strategy: dp.DecisionStrategy
            A decision strategy. A decision strategy can be constructed using
            the dp.DecisionVariables.decision_strategy method.

        Returns
        -------
        dp.StateProbabilities
            A dp.StateProbabilities object containing information about the
            probabilites of each state given the decision strategy.

        '''
        return StateProbabilities(self, decision_strategy)

    def utility_distribution(self, decision_strategy):
        ''' Extract the utility distribution as a dp.UtilityDistribution object.

        Parameters
        ----------
        decision_strategy: dp.DecisionStrategy
            A decision strategy. A decision strategy can be constructed using
            the dp.DecisionVariables.decision_strategy method.

        Returns
        -------
        dp.UtilityDistribution
            Describes the distribution of utilities given the decision strategy.

        '''
        return UtilityDistribution(self, decision_strategy)

    def forbidden_path(self, nodes, values):
        ''' Create a ForbiddenPath object used to describe invalid paths through the
        diagram.

        Parameters
        ----------
        nodes: List of strings
            List of node names connected by the forbidden paths

        values: List of tuples of strings
            List of states of the connected nodes that are forbidden

        Returns
        -------
        dp.ForbiddenPath
            A dp.ForbiddenPath object.

        '''
        return ForbiddenPath(self, nodes, values)

    def fixed_path(self, node_values):
        ''' Create a fixed path object, used to force ChangeNodes to have given
        values.

        Parameters
        ----------
        node_values: dict
            Dictionary with node names as keys and the fixed value as the
            corresponding values.

        Returns
        -------
        dp.FixedPath
            A dp.FixedPath object.

        '''
        return FixedPath(self, node_values)

    def lazy_probability_cut(
        model, path_compatibility_variables
    ):
        ''' Add a probability cut to the model as a lazy constraint.

        Parameters
        ----------
        path_compatibility_variables: dp.PathCompatibilityVariables
            A set of path compatibility variables constructed for this diagram.

        '''
        julia.eval(f'''
            lazy_probability_cut(model, self, path_compatibility_variables)
        ''')

    def conditional_value_at_risk(
        model, path_compatibility_variables,
        alpha, probability_scale_factor
    ):
        ''' Create a conditional value-at-risk (CVaR) objective.

        Parameters
        ----------
        model: Model
            JuMP model into which variables are added.
        x_s: PathCompatibilityVariables
            Path compatibility variables.
        alpha: Float64
            Probability level at which conditional value-at-risk is optimised.
        probability_scale_factor:Float64
            Adjusts conditional value at risk model to be compatible with the expected value expression if the probabilities were scaled there.

        '''
        julia.eval(f'''
            conditional_value_at_risk(
               model, self,
               path_compatibility_variables,
               alpha,
               probability_scale_factor
            )
        ''')


class ExpressionPathUtilities(JuliaName):
    ''' An expression that can be used to set path utilities.

    Parameters
    ----------

    model: dp.Model
        A JuMP Model object

    diagram: dp.InfluenceDiagram
        The influence diagram the model was constructed with.

    expression: string
        A JuMP expression that describes the path utilities (see the
        contingent portfolio analysis page in examples).

    '''

    def __init__(self, model, diagram, expression, path_name="s"):
        super().__init__()
        command = f''' {self._name} =
            [{expression} for {path_name} in paths({diagram._name}.S)]
        '''
        julia.eval(command)


class DecisionVariables(JuliaName):
    """ Create decision variables and constraints.

    Parameters
    ----------
    model: dp.Model
        A JuMP Model object

    diagram: dp.InfluenceDiagram
        A DecisionProgramming Diagram object

    names: bool
        Use names or have anonymous Jump variables

    name: str
        Prefix for predefined decision variable naming convention
    """

    def __init__(self, model, diagram, names=False, name="z"):
        super().__init__()
        self.diagram = diagram
        self.model = model
        julia.tmp1 = names
        julia.tmp2 = name
        commmand = f'''{self._name} = DecisionVariables(
            {model._name},
            {diagram._name};
            names=tmp1,
            name=tmp2
        )'''
        julia.eval(commmand)

    def decision_strategy(self):
        ''' Extract the optimal decision strategy.

        Returns
        -------
        dp.DecisionStrategy
            The optimal decision strategy wrapped in a Python object.

        '''
        return DecisionStrategy(self)


class DecisionStrategy(JuliaName):
    """ Extract values for decision variables from solved decision model.

    Parameters
    ----------
    decision_variables
        Decision variables from a solved model

    """

    def __init__(self, decision_variables):
        super().__init__()
        commmand = f'{self._name} = DecisionStrategy({decision_variables._name})'
        julia.eval(commmand)


class PathCompatibilityVariables(JuliaName):
    """ Create path compatibility variables and constraints

    Attributes
    ----------
    diagram: InfluenceDiagram
        An influence diagram.

    decision_variables: DecisionVariables
        A set of decision variables for the diagram

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
    def __init__(self,
                 model,
                 diagram,
                 decision_variables,
                 names=False,
                 name="x",
                 forbidden_paths=None,
                 fixed=None,
                 probability_cut=True,
                 probability_scale_factor=1.0
                 ):
        super().__init__()
        self.model = model
        self.diagram = diagram
        self.decision_variables = decision_variables
        julia.names = names
        julia.name = name
        forbidden_str = ""
        if forbidden_paths is not None:
            forbidden_paths = [x._name for x in forbidden_paths]
            forbidden_str = "forbidden_paths = [" + ",".join(forbidden_paths) + "],"

        fixed_str = ""
        if fixed is not None:
            fixed_str = f"fixed = {fixed._name},"

        julia.probability_cut = probability_cut
        julia.probability_scale_factor = probability_scale_factor
        command = f'''{self._name} = PathCompatibilityVariables(
            {model._name},
            {diagram._name},
            {decision_variables._name};
            names = names,
            name = name,
            {forbidden_str}
            {fixed_str}
            probability_cut = probability_cut,
            probability_scale_factor = probability_scale_factor
        )'''
        julia.eval(command)


class ExpectedValue(JuliaName):
    """ An expected value object JuMP can minimize on maximize

    Parameters
    ----------
    model: Model

    diagram: Diagram

    pathcompatibility: PathCompatibilityVariables

    """

    def __init__(self, model, diagram, pathcompatibility):
        super().__init__()
        commmand = f'''{self._name} = expected_value(
            {model._name},
            {diagram._name},
            {pathcompatibility._name}
        )'''
        julia.eval(commmand)


class StateProbabilities(JuliaName):
    """ Extract state propabilities from a solved model

    Parameters
    ----------
    diagram: Diagram
        An influence diagram

    decision_strategy: dp.DecisionStrategy
        A decision strategy created for the diagram.

    """
    def __init__(self, diagram, decision_strategy):
        super().__init__()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = StateProbabilities({diagram._name}, {decision_strategy._name})'
        julia.eval(commmand)

    def print_decision_strategy(self):
        ''' Print the decision strategy. '''
        julia.eval(f'''print_decision_strategy(
            {self.diagram._name},
            {self.decision_strategy._name},
            {self._name})''')

    def print(self, nodes):
        ''' Print the state probabilities. '''
        # Format the nodes list using " instead of '
        node_string = str(nodes).replace("\'", "\"")
        julia.eval(f'''print_state_probabilities(
            {self.diagram._name},
            {self._name},
            {node_string})''')


class UtilityDistribution(JuliaName):
    """ Extract utility distribution from a solved model

    Parameters
    ----------
    diagram: Diagram
        The diagram of a solved model

    decision_strategy: DecisionStrategy
        A decision strategy extracted from a solved model.

    """
    def __init__(self, diagram, decision_strategy):
        super().__init__()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = UtilityDistribution({diagram._name}, {decision_strategy._name})'
        julia.eval(commmand)

    def print_distribution(self):
        ''' Print the utility distribution. '''
        julia.eval(f'''print_utility_distribution({self._name})''')

    def print_statistics(self):
        '''Print statistics about the utility distribution.'''
        julia.eval(f'''print_statistics({self._name})''')

    def print_risk_measures(self, alpha, format="%f"):
        '''Print risk measures.'''
        julia.eval(f'''
            print_risk_measures(
                {self._name}, {alpha}; fmt={format}
            )
        ''')

    def value_at_risk(self, alpha):
        ''' Print the value at risk. '''
        julia.eval(f'''
            value_at_risk({self._name}, {alpha})
        ''')

    def conditional_value_at_risk(self, alpha):
        ''' Print the conditional value at rist '''
        julia.eval(f'''
            conditional_value_at_risk(
                {self._name}, {alpha}
            )
        ''')


class ProbabilityMatrix(JuliaName):
    """ Construct an empty probability matrix for a chance node.

    Parameters
    ----------
    diagram: Diagram
       The influence diagram that contains the node

    node : str
        The name of a ChanceNode. The probability matrix of this node is
        returned.

    """

    def __init__(self, diagram, node):
        super().__init__()
        self.diagram = diagram
        julia.eval(f'''{self._name} = ProbabilityMatrix(
           {diagram._name},
           "{node}"
        )''')

    def size(self):
        ''' Return the size of the nodes information set. '''
        return julia.eval(f'''size({self._name})''')


class UtilityMatrix(JuliaName):
    """ Construct an empty probability matrix for a chance node.

    Parameters
    ----------
    diagram: Diagram
       The influence diagram that contains the node

    node : str
        The name of a ChanceNode. The probability matrix of this node is
        returned.
    """
    def __init__(self, diagram, node):
        super().__init__()
        self.diagram = diagram
        julia.eval(f'''{self._name} = UtilityMatrix(
           {diagram._name},
           "{node}"
        )''')


class ForbiddenPath(JuliaName):
    """ Describes forbidden paths through an influence diagram.

    Parameters
    ----------
    diagram: An InfluenceDiagram
        The influence diagram.

    nodes: List of strings
        List of node names connected by the forbidden paths

    values: List of tuples of strings
        List of states of the connected nodes that are forbidden

    """

    def __init__(self, diagram, nodes, states):
        super().__init__()
        node_string = str(nodes).replace("\'", "\"")
        states_string = str(states).replace("\'", "\"")
        julia.eval(f'''{self._name} = ForbiddenPath(
            {diagram._name},
            {node_string},
            {states_string}
        )''')


class FixedPath(JuliaName):
    """ Describes fixed paths in an influence diagram.

    Parameters
    ----------
    diagram: An InfluenceDiagram
        The influence diagram.

    node_values: dict
        Dictionary with node names as keys and the fixed value as the
        corresponding values.

    """

    def __init__(self, diagram, paths):
        super().__init__()
        path_string = "Dict("
        for key, val in paths.items():
            if type(val) == str:
                path_string += f'''"{key}" => "{val}",'''
            else:
                path_string += f'''"{key}" => {val},'''
        path_string += ")"
        julia.eval(f'''{self._name} = FixedPath(
            {diagram._name},
            {path_string}
        )''')


class Paths(JuliaName):
    """ Iterate over paths in lexicographical order.

    Parameters
    ----------
    states: List of strings
        List of paths to connect

    fixed: dp.FixedPath
        Describes states that are held fixed.

    """
    def __init__(self, states, fixed=None):
        super().__init__()
        if type(states) == list and type(states[0]) == int:
            julia.eval(f'tmp = States(State.({states}))')
        elif type(states) == JuliaName:
            julia.eval(f'tmp = {states._name}')

        if fixed is None:
            julia.eval('tmp = paths(tmp)')
        else:
            julia.eval(f'tmp = paths(tmp; fixed={fixed})')
        self._name = julia.tmp

    def __iter__(self):
        self._iterator = iter(self._name)
        return self

    def __next__(self):
        path = next(self._iterator)
        if path:
            path = [i-1 for i in path]
        return path


class CompatiblePaths(JuliaName):
    ''' Interface for iterating over paths that are compatible and active given
    influence diagram and decision strategy.

    Parameters
    ----------
    diagram: dp.Diagram
        An influence diagram.

    decision_strategy: dp.DecisionStrategy
        A decision strategy for the diagram.

    fixed: dp.FixedPath
        Describes states that are held fixed.

    '''
    def __init__(
        self, diagram, decision_strategy,
        fixed=None
    ):
        super().__init__()

        if fixed is None:
            julia.eval('''
                tmp = CompatiblePaths(
                    {diagram._name},
                    {decision_strategy._name}
                )
            ''')
        else:
            julia.eval(f'''
                tmp = CompatiblePaths(
                    {diagram._name},
                    {decision_strategy._name}; fixed={fixed}
                )
            ''')
        self._name = julia.tmp

    def __iter__(self):
        self._iterator = iter(self._name)
        return self

    def __next__(self):
        path = next(self._iterator)
        if path:
            path = [i-1 for i in path]
        return path


