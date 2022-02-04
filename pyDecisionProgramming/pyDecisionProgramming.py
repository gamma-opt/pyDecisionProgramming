from __future__ import annotations
import time
from julia import Julia
from julia.core import JuliaError

# Create an instance of julia without incremental precompilation.
# This does not seem to affect performance much
base_julia = Julia(compiled_modules=False)

# These must be imported after creating the julia name space
from julia import Pkg
from julia import Main
from julia import DecisionProgramming as jdp
import uuid


# Random number generator on Julia side
_random_number_generator = None


def random_number_generator(seed=None):
    ''' Return a random number generator on the Julia side. MersenneTwister is the
    only option here.

    Parameters
    ----------
    seed : integer
        A long integer used as a seed when creating the generator

    Returns
    -------
    pdp.JuliaName
        The random number generator wrapped in a JuliaName

    '''
    global _random_number_generator

    if _random_number_generator is None:
        if seed is None:
            seed = int(time.time())
        _random_number_generator = JuliaName()
        Main.eval('using Random')
        Main.eval(f'{_random_number_generator._name} = MersenneTwister({seed})')
    return _random_number_generator


class JuliaMain():
    ''' Maps to julia.main from the julia library, unless the setting
    an object implemented here (inherits JuliaName). JuliaNames are
    assigned directly.

    '''
    def __setattr__(self, name, value):
        if type(value) == JuliaName or JuliaName in type(value).__bases__:
            Main.eval(f'{name} = {value._name}')
        else:
            Main.__setattr__(name, value)

    def __getattr__(self, name):
        if Main.eval(f"isdefined(Main, :{name})"):
            return Main.__getattr__(name)
        else:
            raise AttributeError(f'{name} not defined in Julia name space')

    def eval(self, command):
        ''' Evaluate Julia code

        Parameters
        -------
        command: string
            A string containing Julia code

        '''
        return Main.eval(command)


# Expose the Julia runner as pdp.Main
julia = JuliaMain()


def load_libs():
    ''' Load Julia dependencies

    '''

    Main.eval('using DecisionProgramming')
    Main.eval('using Gurobi')
    Main.eval('using JuMP')

    # Define a PathUtility type on Julia side
    command = f'''struct PathUtility <: AbstractPathUtility
            data::Array{{AffExpr}}
        end
        Base.getindex(U::PathUtility, i::State) = getindex(U.data, i)
        Base.getindex(U::PathUtility, I::Vararg{{State,N}}) where N = getindex(U.data, I...)
        (U::PathUtility)(s::Path) = value.(U[s...])
    '''
    Main.eval(command)


def activate():
    """ Activate a Julia environment in the working
    directory and load requirements

    """

    Pkg.activate(".")
    load_libs()


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

    load_libs()


def handle_index_syntax(key):
    """ Turn a key tuple into Julia slicing and indexing syntax

    Parameters
    ----------
    key: String, integer, slice or a tuple of these

    Returns
    -------
    string
        The index string in Julia format

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
                raise IndexError('Index not must be string, integer or ":"')
        index_string = ','.join(indexes)

    elif key == slice(None):
        index_string = ':'
    elif isinstance(key, str):
        index_string = f'"{key}"'
    elif isinstance(key, int):
        index_string = key+1
    else:
        raise IndexError('Index must be string, integer or ":"')

    return index_string


class JuliaName():
    ''' Base class for all following Julia objects. Stores the object
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
        raise AttributeError

    def __getitem__(self, key):
        r = JuliaName()
        index_string = handle_index_syntax(key)
        try:
            Main.eval(f'{r._name} = {self._name}[{index_string}]')
        except JuliaError as j:
            raise IndexError(j)
        return r

    def __setitem__(self, key, value):
        index_string = handle_index_syntax(key)
        try:
            command = f'{self._name}[{index_string}] = {value}'
            Main.eval(command)
        except JuliaError as j:
            raise IndexError(j)


class InfluenceDiagram(JuliaName):
    ''' Holds information about the influence diagram, including nodes
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
        Main.eval(f'''
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
        node: pdp.ChanceNode
            Random probabilities will be assigned to this node.

        n_inactive: Int
            Number of inactive states

        '''
        rng = random_number_generator(seed)
        print(rng)
        Main.eval(f'''
            random_probabilities!(
                {rng._name}, {self._name},
                {node._name}; n_inactive={n_inactive}
            )
        ''')

    def random_utilities(self, node, low=-1.0, high=1.0, seed=None):
        ''' Generate random utilities for a value node.

        Parameters
        ----------
        node: pdp.ValueNode
            Random utilities are generated for this node

        low: float
            Lower bound for random utilities

        high: float
            Upper bound for random utilities

        seed: int
            Seed for the random number generator

        '''
        rng = random_number_generator(seed)
        Main.eval(f'''
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
        Main.eval(command)

    def generate_arcs(self):
        ''' Generate arc structures using nodes added to influence diagram, by ordering nodes, giving them indices and generating correct values for the vectors Names, I_j, states, S, C, D, V in the influence digram. Abstraction is created and the names of the nodes and states are only used in the user interface from here on.

        '''
        Main.eval(f'generate_arcs!({self._name})')

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
        """ Generate the diagram once nodes, probabilities and utilities have been
        added.

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
        Main.default_probability = default_probability
        Main.default_utility = default_utility
        Main.positive_path_utility = positive_path_utility
        Main.negative_path_utility = negative_path_utility
        Main.eval(f'''generate_diagram!(
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
        Main.eval(f'''tmp = num_states(
            {self._name}, "{node}"
        )''')
        return Main.tmp

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
        return Main.eval(f'''index_of({self._name}, "{name}")''')-1

    def set_path_utilities(self, expressions):
        ''' Use given expression as the path utilities of the diagram.

        Parameters
        ----------
        expressions: ExpressionPathUtilities
            A set of JuMP expression.

        '''
        Main.eval(f'''
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
        pdp.ProbabilityMatrix
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
        pdp.UtilityMatrix
            A utility matrix with values set to negative infinity.

        '''
        return UtilityMatrix(self, node)

    def decision_variables(self, model):
        ''' Construct the decision variables for a given model and this diagram.

        Parameters
        ----------
        model: pdp.Model
            A model constructed for this diagram.

        Returns
        -------
        pdp.DecisionVariables
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
        model: pdp.Model
            A model constructed for this diagram.
        decision variables: pdp.DecisionVariables (optional)
            DecisionVariables constructed for this model.
        names: Bool (optional)
        name: String (optional)
        forbidden_paths: List of pdp.ForbiddenPath variables (optional)
        fixed: List of pdp.FixedPath variables (optional)
        probability_cut: Bool (optional)
        probability_scale_factor: Number (optional)

        Returns
        -------
        pdp.PathCompatibilityVariables
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
        model: pdp.Model
            A model constructed for this diagram.
        path_compatibility_variables: pdp.PathCompatibilityVariables (optional)
            PathCompatibilityVariables generated for this model, usually using
            diagram.path_compatibility_variables.

        Returns
        -------
        pdp.ExpectedValue
            A pdp.ExpectedValue object describing the expected value for the
            optimal decision strategy.

        '''
        x_s = path_compatibility_variables
        if x_s is None:
            x_s = self.path_compatibility_variables(model)
        return ExpectedValue(model, self, path_compatibility_variables)

    def state_probabilities(self, decision_strategy):
        ''' Extract the state probabilities as a pdp.StateProbabilities object.

        Parameters
        ----------
        decision_strategy: pdp.DecisionStrategy
            A decision strategy. A decision strategy can be constructed using
            the pdp.DecisionVariables.decision_strategy method.

        Returns
        -------
        pdp.StateProbabilities
            A pdp.StateProbabilities object containing information about the
            probabilites of each state given the decision strategy.

        '''
        return StateProbabilities(self, decision_strategy)

    def utility_distribution(self, decision_strategy):
        ''' Extract the utility distribution as a pdp.UtilityDistribution object.

        Parameters
        ----------
        decision_strategy: pdp.DecisionStrategy
            A decision strategy. A decision strategy can be constructed using
            the pdp.DecisionVariables.decision_strategy method.

        Returns
        -------
        pdp.UtilityDistribution
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
        pdp.ForbiddenPath
            A pdp.ForbiddenPath object.

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
        pdp.FixedPath
            A pdp.FixedPath object.

        '''
        return FixedPath(self, node_values)

    def lazy_probability_cut(
        model, path_compatibility_variables
    ):
        ''' Add a probability cut to the model as a lazy constraint.

        Parameters
        ----------
        path_compatibility_variables: pdp.PathCompatibilityVariables
            A set of path compatibility variables constructed for this diagram.

        '''
        Main.eval(f'''
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
        Main.eval(f'''
            conditional_value_at_risk(
               model, self,
               path_compatibility_variables,
               alpha,
               probability_scale_factor
            )
        ''')


class Model(JuliaName):
    """ Wraps a JuMP optimizer model and decision model variables.

    Methods
    -------
    setup_Gurobi_optimizer(*constraints):
        Create a Gurobi optimizer with a given set of contraints.

    optimize():
        Run the optimizer.

    """
    def __init__(self):
        super().__init__()
        self.optimizer_set = False
        Main.eval(f'{self._name} = Model()')

    def setup_Gurobi_optimizer(self, *constraints):
        ''' Set Gurobi as the optimizer for this model.

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
        self.optimizer_set = True

    def objective(self, objective, operator="Max"):
        """ Set the objective for the optimizer

        Parameters
        ----------
        op: "Min" or "Max"
            Whether to minimize or maximize the objective

        expected_value: ExpectedValue
            An ExpectedValue object. Describes the objective function.

        """
        if type(objective) == ExpectedValue:
            Main.eval(f'''@objective(
                {self._name}, {operator},
                {objective._name})
            ''')
        elif type(objective) == str:
            # Note: ending the command with ;0 to prevent
            # Julia from returning the object. Otherwise
            # the Python julia library will try to convert
            # this to a Python object and cause an exception.
            command = f'''@objective(
                {self._name},
                {operator},
                {objective}
            ); 0'''
            Main.eval(command)

    def optimize(self):
        ''' Run the current optimizer '''

        if not self.optimizer_set:
            self.setup_Gurobi_optimizer()

        Main.eval(f'optimize!({self._name})')

    def constraint(self, *args):
        ''' Set a model constraints

        loop: String (optional)
            Set of loop variables in the JuMP constraint format (see the
            contingent portfolio analysis page in examples)

        constraint: String
            The contraints in the JuMP format (see the contingent portfolio
             analysis page in examples)

        '''
        argument_text = ",".join(args)
        # Note: ending the command with ;0 to prevent
        # Julia from returning the object. Otherwise
        # the Python julia library will try to convert
        # this to a Python object and cause an exception.
        Main.eval(f'''@constraint(
            {self._name},
            {argument_text}
        ); 0''')


class JuMPExpression(JuliaName):
    def __init__(self, model, *args):
        ''' Construct a JuMP expression.

        model: Model
            A pyDecisionProgramming Model object

        loop: String (optional)
            Set of loop variables in the JuMP constraint format (see the
            contingent portfolio analysis page in examples)

        constraint: String
            The contraints in the JuMP format (see the contingent portfolio
             analysis page in examples)

        '''
        super().__init__()
        argument_text = ",".join(args)
        # Note: ending the command with ;0 to prevent
        # Julia from returning the object. Otherwise
        # the Python julia library will try to convert
        # this to a Python object and cause an exception.
        command = f'''{self._name} = @expression(
            {model._name},
            {argument_text}
        ); 0'''
        Main.eval(command)


class JuMPArray(JuliaName):
    ''' An array of JuMP variables. Makes it easier to define contraints
    using the @constraint syntax.

    '''
    def __init__(self, model, dims, binary=False):
        ''' Construct an array of JuMP expressions.

        model: Model
            A pyDecisionProgramming Model object

        dims: List of Integers
            A list corresponding to the size of the array in each of its
            dimensions.

        binary: Boolean (optional, default False)
            Wether the variables are boolean.

        '''
        super().__init__()
        binary_arg = ""
        if binary:
            binary_arg = "binary=true, "
        command = f'''
            tmp = Array{{VariableRef}}(undef, {dims}...)
            for i in eachindex(tmp)
                tmp[i] = @variable({model._name}, {binary_arg})
            end
            {self._name} = tmp
        '''
        Main.eval(command)


class ExpressionPathUtilities(JuliaName):
    ''' An expression that can be used to set path utilities.

    '''
    def __init__(self, model, diagram, expression, path_name="s"):
        ''' Path utilities as a JuMP expression.

        model: Model
            A pyDecisionProgramming Model object

        diagram: pdp.InfluenceDiagram
            The influence diagram the model was constructed with.

        expression: string
            A JuMP expression that describes the path utilities (see the
            contingent portfolio analysis page in examples).

        '''
        super().__init__()
        command = f''' {self._name} =
            [{expression} for {path_name} in paths({diagram._name}.S)]
        '''
        Main.eval(command)


class DecisionVariables(JuliaName):
    """ Create decision variables and constraints.
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

    def decision_strategy(self):
        ''' Extract the optimal decision strategy.

        Returns
        -------
        pdp.DecisionStrategy
            The optimal decision strategy wrapped in a Python object.

        '''
        return DecisionStrategy(self)


class DecisionStrategy(JuliaName):
    """ Extract values for decision variables from solved decision model.

    """
    def __init__(self, decision_variables):
        """
        Parameters
        ----------
        Decision variables for a solved model

        """
        super().__init__()
        commmand = f'{self._name} = DecisionStrategy({decision_variables._name})'
        Main.eval(commmand)


class PathCompatibilityVariables(JuliaName):
    """ Create path compatibility variables and constraints

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
                 forbidden_paths=None,
                 fixed=None,
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
        Main.names = names
        Main.name = name
        forbidden_str = ""
        if forbidden_paths is not None:
            forbidden_paths = [x._name for x in forbidden_paths]
            forbidden_str = "forbidden_paths = [" + ",".join(forbidden_paths) + "],"

        fixed_str = ""
        if fixed is not None:
            fixed_str = f"fixed = {fixed._name},"

        Main.probability_cut = probability_cut
        Main.probability_scale_factor = probability_scale_factor
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
        Main.eval(command)


class ExpectedValue(JuliaName):
    """ An expected value object JuMP can minimize on maximize

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


class StateProbabilities(JuliaName):
    """ Extract state propabilities from a solved model

    Methods
    -------
    print_decision_strategy()
        Pretty print the decision strategy

    print()
        Pretty print state probabilities for a list of nodes

    """
    def __init__(self, diagram, decision_strategy):
        """
        Parameters
        ----------
        diagram: Diagram
            An influence diagram

        decision_strategy: pdp.DecisionStrategy
            A decision strategy created for the diagram.

        """
        super().__init__()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = StateProbabilities({diagram._name}, {decision_strategy._name})'
        Main.eval(commmand)

    def print_decision_strategy(self):
        ''' Print the decision strategy.

        '''
        Main.eval(f'''print_decision_strategy(
            {self.diagram._name},
            {self.decision_strategy._name},
            {self._name})''')

    def print(self, nodes):
        ''' Print the state probabilities.

        '''
        # Format the nodes list using " instead of '
        node_string = str(nodes).replace("\'", "\"")
        Main.eval(f'''print_state_probabilities(
            {self.diagram._name},
            {self._name},
            {node_string})''')


class UtilityDistribution(JuliaName):
    """ Extract utility distribution from a solved model

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
            A decision strategy extracted from a solved model.

        """
        super().__init__()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = UtilityDistribution({diagram._name}, {decision_strategy._name})'
        Main.eval(commmand)

    def print_distribution(self):
        ''' Print the utility distribution. '''
        Main.eval(f'''print_utility_distribution({self._name})''')

    def print_statistics(self):
        '''Print statistics about the utility distribution.'''
        Main.eval(f'''print_statistics({self._name})''')

    def print_risk_measures(self, alpha, format="%f"):
        '''Print risk measures.'''
        Main.eval(f'''
            print_risk_measures(
                {self._name}, {alpha}; fmt={format}
            )
        ''')

    def value_at_risk(self, alpha):
        ''' Print the value at risk. '''
        Main.eval(f'''
            value_at_risk({self._name}, {alpha})
        ''')

    def conditional_value_at_risk(self, alpha):
        ''' Print the conditional value at rist '''
        Main.eval(f'''
            conditional_value_at_risk(
                {self._name}, {alpha}
            )
        ''')


class ChanceNode(JuliaName):
    """ Create a change node that can be added into a Diagram

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
    """ Create a decision node that can be added into a Diagram

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
    """ Create a value node that can be added into a Diagram

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

        self.leaves = nodes

        Main.tmp = jdp.ValueNode(id, nodes)
        Main.eval(f'{self._name} = tmp')


class ProbabilityMatrix(JuliaName):
    """ Construct an empty probability matrix for a chance node. """
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

    def size(self):
        ''' Return the size of the nodes information set. '''
        return Main.eval(f'''size({self._name})''')


class UtilityMatrix(JuliaName):
    """ Construct an empty probability matrix for a chance node. """
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


class ForbiddenPath(JuliaName):
    """ Describes forbidden paths through an influence diagram. """
    def __init__(self, diagram, nodes, states):
        '''
        Parameters
        ----------
        diagram: An InfluenceDiagram
            The influence diagram.

        nodes: List of strings
            List of node names connected by the forbidden paths

        values: List of tuples of strings
            List of states of the connected nodes that are forbidden

        '''
        super().__init__()
        node_string = str(nodes).replace("\'", "\"")
        states_string = str(states).replace("\'", "\"")
        Main.eval(f'''{self._name} = ForbiddenPath(
            {diagram._name},
            {node_string},
            {states_string}
        )''')


class FixedPath(JuliaName):
    """ Describes fixed paths in an influence diagram. """
    def __init__(self, diagram, paths):
        '''
        Parameters
        ----------
        diagram: An InfluenceDiagram
            The influence diagram.

        node_values: dict
            Dictionary with node names as keys and the fixed value as the
            corresponding values.

        '''
        super().__init__()
        path_string = "Dict("
        for key, val in paths.items():
            if type(val) == str:
                path_string += f'''"{key}" => "{val}",'''
            else:
                path_string += f'''"{key}" => {val},'''
        path_string += ")"
        Main.eval(f'''{self._name} = FixedPath(
            {diagram._name},
            {path_string}
        )''')


class Paths(JuliaName):
    """ Iterate over paths in lexicographical order. """
    def __init__(self, states, fixed=None):
        '''
        Parameters
        ----------
        states: List of strings
            List of paths to connect

        fixed: pdp.FixedPath
            Describes states that are held fixed.

        '''
        super().__init__()
        if type(states) == list and type(states[0]) == int:
            Main.eval(f'tmp = States(State.({states}))')
        elif type(states) == JuliaName:
            Main.eval(f'tmp = {states._name}')

        if fixed is None:
            Main.eval('tmp = paths(tmp)')
        else:
            Main.eval(f'tmp = paths(tmp; fixed={fixed})')
        self._name = Main.tmp

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

    '''
    def __init__(
        self, diagram, decision_strategy,
        fixed=None
    ):
        '''
        Parameters
        ----------
        diagram: pdp.Diagram
            An influence diagram.

        decision_strategy: pdp.DecisionStrategy
            A decision strategy for the diagram.

        fixed: pdp.FixedPath
            Describes states that are held fixed.

        '''
        super().__init__()

        if fixed is None:
            Main.eval('''
                tmp = CompatiblePaths(
                    {diagram._name},
                    {decision_strategy._name}
                )
            ''')
        else:
            Main.eval(f'''
                tmp = CompatiblePaths(
                    {diagram._name},
                    {decision_strategy._name}; fixed={fixed}
                )
            ''')
        self._name = Main.tmp

    def __iter__(self):
        self._iterator = iter(self._name)
        return self

    def __next__(self):
        path = next(self._iterator)
        if path:
            path = [i-1 for i in path]
        return path
