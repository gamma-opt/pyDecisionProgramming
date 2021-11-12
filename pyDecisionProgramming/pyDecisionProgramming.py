from julia import Pkg
from julia import Main
from julia import DecisionProgramming as jdp
import numpy as np
import uuid


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


def unique_name():
    ''' A utility for generating unique names for the Julia main name space '''

    return 'pyDP'+uuid.uuid4().hex[:10]


class InfluenceDiagram():
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

    probability_matrix(change_node_name)
        Construct an empty probability matrix for the given chance node.
        This is helpful in setting probabilities, since it provides a matrix
        of the righ size and default zero values to all entries.

    set_probabilities(change_node_name, matrix)
        Set the probability matrix at a given node. The matrix is a Numpy
        array. You can use the probability_matrix-method to find the matrix
        size.

    utility_matrix(value_node_name)
        Construct an empty utility matrix for the given value node.
        This is helpful in setting utilities, since it provides a matrix
        of the right size.

    set_utility(value_node_name, matrix)
        Set the utility matrix at a given node. The matrix is a Numpy
        array. You can use the utility_matrix-method to find the matrix
        size.

    generate(
               default_probability=true,
               default_utility=true,
               positive_path_utility=false,
               negative_path_utility=false
            )
        Generate complete influence diagram with probabilities and utilities as well.
    '''

    def __init__(self):
        self._name = unique_name()
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

    def probability_matrix(self, node):
        """
        Parameters
        ----------
        node : str
            The name of a ChanceNode. The probability matrix of this node is
            returned.

        Returns
        -------
            An empty probability matrix as a Numpy array
        """
        Main.eval(f'tmp = {self._name}')
        matrix = Main.ProbabilityMatrix(Main.tmp, node)
        return np.array(matrix)

    def set_probabilities(self, node, matrix):
        """set_probabilities
        Parameters
        ----------
        node : str
            The name of a ValueNode. The probability matrix of this node is
            returned.

        matrix : Numpy array
            The probability matrix that replaces the current one.
        """
        Main.tmp = matrix
        Main.eval('tmp = convert(Array{Float64}, tmp)')
        Main.eval(f'add_probabilities!({self._name}, "{node}", tmp)')

    def utility_matrix(self, value):
        """
        Parameters
        ----------
        node : str
            The name of a ValueNode. The probability matrix of this node is
            returned.

        Returns
        -------
            An empty utility matrix as a Numpy array
        """
        Main.eval(f'tmp = {self._name}')
        matrix = Main.UtilityMatrix(Main.tmp, value)
        return np.array(matrix)

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


class Model():
    def __init__(self):
        self._name = unique_name()
        Main.eval(f'{self._name} = Model()')

    def expected_value(self, diagram, decision_variables):
        commmand = f'tmp = expected_value({self._name}, {diagram._name}, {decision_variables._name})'
        Main.eval(commmand)
        return Main.tmp

    def setup_Gurobi_optimizer(self, *constraints):
        ''' Create a JuMP optimizer

        constraints -- Tuple formatted as (constraint_name, constraint)
        '''

        julia_command = '''optimizer = optimizer_with_attributes(
                     () -> Gurobi.Optimizer(Gurobi.Env())'''

        for constraint in constraints:
            julia_command += f''',
                         "{constraint[0]}" => {constraint[1]}'''

        julia_command += ')'

        Main.eval(julia_command)
        Main.eval('print(optimizer)')

        Main.eval(f'set_optimizer({self._name}, optimizer)')

    def optimize(self):
        ''' Run the current optimizer '''

        Main.eval(f'optimize!({self._name})')


class DecisionVariables():
    def __init__(self, model, diagram):
        self._name = unique_name()
        commmand = f'{self._name} = DecisionVariables({model._name}, {diagram._name})'
        Main.eval(commmand)


class PathCompatibilityVariables():
    def __init__(self, model, diagram, decision_variables):
        self._name = unique_name()
        commmand = f'{self._name} = PathCompatibilityVariables({model._name}, {diagram._name}, {decision_variables._name})'
        Main.eval(commmand)


class DecisionStrategy():
    def __init__(self, decision_variables):
        self._name = unique_name()
        commmand = f'{self._name} = DecisionStrategy({decision_variables._name})'
        Main.eval(commmand)


class StateProbabilities():
    def __init__(self, diagram, decision_strategy):
        self._name = unique_name()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = StateProbabilities({diagram._name}, {decision_strategy._name})'
        Main.eval(commmand)

    def print(self):
        Main.eval(f'''print_decision_strategy(
            {self.diagram._name},
            {self.decision_strategy._name},
            {self._name})''')


class UtilityDistribution():
    def __init__(self, diagram, decision_strategy):
        self._name = unique_name()
        self.diagram = diagram
        self.decision_strategy = decision_strategy
        commmand = f'{self._name} = UtilityDistribution({diagram._name}, {decision_strategy._name})'
        Main.eval(commmand)

    def print_distribution(self):
        Main.eval(f'''print_utility_distribution({self._name})''')

    def print_statistics(self):
        Main.eval(f'''print_statistics({self._name})''')


class ChanceNode():
    def __init__(self, id, nodes, names):
        ''' Create a chance node

        id: str
            The id of the node
        nodes: list(str)
            List of nodes connected to this node
        names:
            List of node names

        return -- Change node
        '''

        self._name = unique_name()

        Main.tmp = jdp.ChanceNode(id, nodes, names)
        Main.eval(f'{self._name} = tmp')


class DecisionNode():
    def __init__(self, id, nodes, names):
        ''' Create a decision node

        id -- The id of the node
        nodes -- List of nodes connected to this node
        names -- List of node names

        return -- Change node
        '''

        self._name = unique_name()

        if isinstance(nodes, Vector):
            assert(isinstance(names, Vector))

            Main.eval(f'{self._name} = DecisionNode({id}, Main.{nodes._name}, Main.{names._name})')

        else:
            # Try with a python object, Julia will type-check
            Main.tmp = jdp.DecisionNode(id, nodes, names)
            Main.eval(f'{self._name} = tmp')


class ValueNode():
    def __init__(self, id, nodes):
        ''' Create a value node

        id -- The id of the node
        nodes -- List of nodes connected to this node
        names -- List of node names

        return -- Change node
        '''

        self._name = unique_name()

        if isinstance(nodes, Vector):
            Main.eval(f'{self._name} = ValueNode({id}, {nodes._name})')

        else:
            # Try with a python object, Julia will type-check
            Main.tmp = jdp.ValueNode(id, nodes)
            Main.eval(f'{self._name} = tmp')


class ProbabilityMatrix():
    def __init__(self, diagram, node):
        ''' Create a probability matrix

        return -- Change node
        '''

        self._name = unique_name()

        command = f'{self._name} = ProbabilityMatrix({diagram._name}, "{node}")'
        Main.eval(command)

    def set(self, outcome, probability):
        Main.eval(f'{self._name}["{outcome}"] = {probability}')






def DecisionStrategy_old(decisionVariables):
    ''' Create a JuMP optimizer

    decisionVariables -- A DecisionVariables object
    '''

    return Main.eval(f'DecisionStrategy({decisionVariables._name})')


class Probabilities:
    ''' A wrapper for the DecisionProgramming.jl Probabilities
    type.

    Without the wrapper it get's interpreted as a python array,
    which in turn becomes a Julia vector.

    self.id -- The node id the probabilies correspond to
    self._name -- The name of the Probabilities-variable in
        Julia main name space.
    '''

    def __init__(self, id, probabilities):
        ''' Set propabilities for outcomes on a chance node and
        build the corresponding probabilities object.

        id -- The id of the node
        probabilities -- List of probabilities for each outcome
        '''

        self.id = id
        self._name = unique_name()
        print('prob name', self._name)
        Main.pDR_id = id
        Main.pDR_p = probabilities
        Main.eval(f'{self._name} = Probabilities(pDR_id, pDR_p)')

    def __str__(self):
        return getattr(Main, self._name).__str__()


class Consequences:
    ''' A wrapper for the DecisionProgramming.jl Consequences
    type.

    Without the wrapper it get's interpreted as a python array,
    which in turn becomes a Julia vector.

    self.id -- The node id the consequences correspond to
    self._name -- The name of the Consequences-variable in
        Julia main name space.
    '''

    def __init__(self, id, consequences):
        ''' Set consequences to outcomes on a value node and
        build the corresponding Consequences object.

        id -- The id of the node
        consequences -- List of consequences for each outcome
        '''

        self.id = id
        self._name = unique_name()
        print('consq name', self._name)
        Main.pDR_id = id
        Main.pDR_c = consequences
        Main.eval(f'{self._name} = Consequences(pDR_id, pDR_c)')

    def __str__(self):
        return getattr(Main, self._name).__str__()


class Vector:
    ''' Corresponds to the Julia Vector class.

    We implement this here since the python Array class does
    not automatically support the DecisionProgramming types
    defined on the Julia side.
    '''

    def __init__(self, type: str):
        ''' Create a new Julia vector of a given type

        type: str -- The Julia type the vector contains
        '''

        self._name = unique_name()
        self.type = type

        Main.eval(f'{self._name} = Vector{{{type}}}()')

    def __str__(self):
        return getattr(Main, self._name).__str__()

    def push(self, element):
        ''' Push and element to a given vector

        element -- the new element
        '''

        if self.type == 'Probabilities':
            assert(isinstance(element, Probabilities))

            Main.eval(
                f'push!({self._name}, {element._name})'
            )

        elif self.type == 'Consequences':
            assert(isinstance(element, Consequences))

            Main.eval(f'push!({self._name}, {element._name})')

        else:
            Main.pDR_e = element
            Main.eval(f'push!({self._name}, pDR_e)')

    def sortByNode(self):
        ''' Sort the vector by node id contained in the elements
        '''

        Main.eval(f'sort!({self._name}, by = x -> x.j)')


class States:
    ''' A wrapper for the DecisionProgramming.jl States
    type.

    Without the wrapper it get's interpreted as a python array,
    which in turn becomes a Julia vector.

    self._name -- The name of the States-variable in
        Julia main name space.
    '''

    def __init__(self, state_list):
        ''' Set node states and build the corresponding States object.

        state_list -- A list of tuples of the form formatted as [(n, id)],
        where n is the number of states and id an integer identifying the node
        '''

        Main.pDR_params = [(c, [n]) for c, n in state_list]
        self._name = unique_name()
        Main.eval(f'{self._name} = States(pDR_params)')

    def __getitem__(self, key):
        return Main.eval(f'{self._name}[{key}]')

    def __str__(self):
        return getattr(Main, self._name).__str__()


def DefaultPathProbability(chanceNodes, probabilites):
    ''' Construct a defaultPathProbability (Julia Struct)

    changeNodes -- Vector of ChangeNodes
    probabilites -- Vector of Probabilities-objects for each ChangeNode
    '''

    return Main.eval(f'''DefaultPathProbability(
        {chanceNodes._name},
        {probabilites._name}
    )''')


def DefaultPathUtility(valueNodes, consequences):
    ''' Construct a defaultPathProbability (Julia Struct)

    valueNodes -- Vector of ValueNodes
    consequences -- Vector of Consequences-objects for each ValueNode
    '''

    return Main.eval(f'''DefaultPathUtility(
        {valueNodes._name},
        {consequences._name}
    )''')


def validate_influence_diagram(
    states,
    chanceNodes,
    decisionNodes,
    valueNodes
):
    """ Validate an influence diagram
    """

    Main.eval(f'''validate_influence_diagram(
                    {states._name},
                    {chanceNodes._name},
                    {decisionNodes._name},
                    {valueNodes._name}
               )''')


class Model_old():
    ''' A wrapper for the DecisionProgramming.jl Model
    type.

    Members include functions that modify the model.

    self._name -- The name of the DecisionProgramming-variable in
        Julia main name space.

    self.probability_cut() -- Adds a probability cut to the model
        as a lazy constraint
    '''

    def __init__(self):
        ''' Initialize a pyDecisionProgramming Model '''
        self._name = unique_name()
        Main.eval(f'''{self._name} = Model()''')

    def probability_cut(self, pi_s, P, probability_scale_factor=1.0):
        '''Adds a probability cut to the model as a lazy constraint

        pi_s -- A PathProbabilityVariables object
        P -- An AbstractPathProbability object
        probability_scale_factor -- An additional scaling factor
        '''

        Main.eval(f'''DecisionVariables(
                              {self._name},
                              {pi_s._name},
                              {P._name}
                         )''')

    def __str__(self):
        return Main.eval(f'''{self._name}''')



class PathProbabilityVariables():
    ''' A wrapper for the DecisionProgramming.jl PathProbabilityVariables
    type.

    Without the wrapper it get's interpreted as a python dictionary,
    and does not preserve the Julia type.

    self._name -- The name of the DecisionProgramming-variable in
        Julia main name space.
    '''

    def __init__(self,
                 model,
                 decisionVariables,
                 states,
                 defaultPathProbability
                 ):
        ''' Construct a PathProbabilityVariables-object (Julia Struct)

        model -- A wrapped Model object
        decisionVariables -- A wrapped DecisionVariables object
        states -- A pyDecisionProgramming States object
        defaultPathProbability -- A wrapped defaultPathProbability object
        '''

        self._name = unique_name()
        Main.dp_decisionVariables = decisionVariables
        Main.dp_defaultPathProbability = defaultPathProbability

        Main.eval(f'''{self._name} = PathProbabilityVariables(
                    {model._name},
                    dp_decisionVariables,
                    {states._name},
                    dp_defaultPathProbability
               )''')


def expected_value(
    model,
    pathProbabilityVariables,
    defaultPathUtility
):
    ''' Construct a expected-value objective (Julia Struct) '''

    Main.dp_defaultPathUtility = defaultPathUtility

    return Main.eval(f'''expected_value(
                          {model._name},
                          {pathProbabilityVariables._name},
                          dp_defaultPathUtility
                     )''')


def set_objective(
    model,
    direction,
    objective
):
    ''' Set an objective for the DecisionProgramming model

    model -- A wrapped Model object
    direction -- string: "Max" to maximize and "Min" to minimize
    objective -- An objective-object created by pyDecisionProgramming
    '''

    Main.dp_objective = objective

    return Main.eval(f'''@objective(
                          {model._name},
                          {direction},
                          dp_objective
                     )''')




def UtilityDistribution_old(
       states,
       defaultPathProbability,
       defaultPathUtility,
       decisionVariables
):
    ''' Build a utility distribution

    states -- A pyDecisionProgramming States object
    defaultPathProbability -- A wrapped defaultPathProbability object
    defaultPathUtility -- A wrapped defaultPathUtility object
    decisionVariables -- A wrapped decisionVariables object
    '''

    Main.dp_defaultPathProbability = defaultPathProbability
    Main.dp_defaultPathUtility = defaultPathUtility
    Main.dp_decisionVariables = decisionVariables
    return Main.eval(f'''UtilityDistribution(
        {states._name},
        dp_defaultPathProbability,
        dp_defaultPathUtility,
        dp_decisionVariables
        )
    ''')


def print_utility_distribution(utilityDistribution):
    ''' Print information about the utility distribution.

    utilityDistribution -- A utilityDistribution object
    '''

    Main.dp_utilityDistribution = utilityDistribution
    return Main.eval('''print_utility_distribution(
        dp_utilityDistribution)
        ''')


def print_statistics(utilityDistribution):
    ''' Print additional statistics about the utility distibution

    utilityDistribution -- A utilityDistribution object
    '''

    Main.dp_utilityDistribution = utilityDistribution
    return Main.eval('''print_statistics(
        dp_utilityDistribution)
        ''')
