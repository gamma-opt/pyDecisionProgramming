from julia import Pkg
from julia import Main
from julia import DecisionProgramming as jdp
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

    def __init__(self):
        self.name = unique_name()
        Main.eval(f'{self.name} = InfluenceDiagram()')

    def add_node(self, node):
        Main.eval(f'add_node!({self.name}, {node.name})')

    def generate_arcs(self):
        Main.eval(f'generate_arcs!({self.name})')

    def add_probabilities(self, node, probability_matrix):
        Main.eval(f'add_probabilities!({self.name}, "{node}", {probability_matrix.name})')


class ChanceNode():
    def __init__(self, id, nodes, names):
        ''' Create a chance node

        id -- The id of the node
        nodes -- List of nodes connected to this node
        names -- List of node names

        return -- Change node
        '''

        self.name = unique_name()

        if isinstance(nodes, Vector):
            assert(isinstance(names, Vector))

            Main.eval(f'{self.name} = ChanceNode({id}, Main.{nodes.name}, Main.{names.name})')

        else:
            # Try with a python object, Julia will type-check
            Main.tmp = jdp.ChanceNode(id, nodes, names)
            Main.eval(f'{self.name} = tmp')


class DecisionNode():
    def __init__(self, id, nodes, names):
        ''' Create a decision node

        id -- The id of the node
        nodes -- List of nodes connected to this node
        names -- List of node names

        return -- Change node
        '''

        self.name = unique_name()

        if isinstance(nodes, Vector):
            assert(isinstance(names, Vector))

            Main.eval(f'{self.name} = DecisionNode({id}, Main.{nodes.name}, Main.{names.name})')

        else:
            # Try with a python object, Julia will type-check
            Main.tmp = jdp.DecisionNode(id, nodes, names)
            Main.eval(f'{self.name} = tmp')


class ValueNode():
    def __init__(self, id, nodes):
        ''' Create a value node

        id -- The id of the node
        nodes -- List of nodes connected to this node
        names -- List of node names

        return -- Change node
        '''

        self.name = unique_name()

        if isinstance(nodes, Vector):
            Main.eval(f'{self.name} = ValueNode({id}, {nodes.name})')

        else:
            # Try with a python object, Julia will type-check
            Main.tmp = jdp.ValueNode(id, nodes)
            Main.eval(f'{self.name} = tmp')


class ProbabilityMatrix():
    def __init__(self, diagram, node):
        ''' Create a propability matrix

        return -- Change node
        '''

        self.name = unique_name()

        command = f'{self.name} = ProbabilityMatrix({diagram.name}, "{node}")'
        Main.eval(command)

    def set(self, outcome, probability):
        Main.eval(f'{self.name}["{outcome}"] = {probability}')



class Probabilities:
    ''' A wrapper for the DecisionProgramming.jl Probabilities
    type.

    Without the wrapper it get's interpreted as a python array,
    which in turn becomes a Julia vector.

    self.id -- The node id the probabilies correspond to
    self.name -- The name of the Probabilities-variable in
        Julia main name space.
    '''

    def __init__(self, id, probabilities):
        ''' Set propabilities for outcomes on a chance node and
        build the corresponding probabilities object.

        id -- The id of the node
        probabilities -- List of probabilities for each outcome
        '''

        self.id = id
        self.name = unique_name()
        print('prob name', self.name)
        Main.pDR_id = id
        Main.pDR_p = probabilities
        Main.eval(f'{self.name} = Probabilities(pDR_id, pDR_p)')

    def __str__(self):
        return getattr(Main, self.name).__str__()


class Consequences:
    ''' A wrapper for the DecisionProgramming.jl Consequences
    type.

    Without the wrapper it get's interpreted as a python array,
    which in turn becomes a Julia vector.

    self.id -- The node id the consequences correspond to
    self.name -- The name of the Consequences-variable in
        Julia main name space.
    '''

    def __init__(self, id, consequences):
        ''' Set consequences to outcomes on a value node and
        build the corresponding Consequences object.

        id -- The id of the node
        consequences -- List of consequences for each outcome
        '''

        self.id = id
        self.name = unique_name()
        print('consq name', self.name)
        Main.pDR_id = id
        Main.pDR_c = consequences
        Main.eval(f'{self.name} = Consequences(pDR_id, pDR_c)')

    def __str__(self):
        return getattr(Main, self.name).__str__()


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

        self.name = unique_name()
        self.type = type

        Main.eval(f'{self.name} = Vector{{{type}}}()')

    def __str__(self):
        return getattr(Main, self.name).__str__()

    def push(self, element):
        ''' Push and element to a given vector

        element -- the new element
        '''

        if self.type == 'Probabilities':
            assert(isinstance(element, Probabilities))

            Main.eval(
                f'push!({self.name}, {element.name})'
            )

        elif self.type == 'Consequences':
            assert(isinstance(element, Consequences))

            Main.eval(f'push!({self.name}, {element.name})')

        else:
            Main.pDR_e = element
            Main.eval(f'push!({self.name}, pDR_e)')

    def sortByNode(self):
        ''' Sort the vector by node id contained in the elements
        '''

        Main.eval(f'sort!({self.name}, by = x -> x.j)')


class States:
    ''' A wrapper for the DecisionProgramming.jl States
    type.

    Without the wrapper it get's interpreted as a python array,
    which in turn becomes a Julia vector.

    self.name -- The name of the States-variable in
        Julia main name space.
    '''

    def __init__(self, state_list):
        ''' Set node states and build the corresponding States object.

        state_list -- A list of tuples of the form formatted as [(n, id)],
        where n is the number of states and id an integer identifying the node
        '''

        Main.pDR_params = [(c, [n]) for c, n in state_list]
        self.name = unique_name()
        Main.eval(f'{self.name} = States(pDR_params)')

    def __getitem__(self, key):
        return Main.eval(f'{self.name}[{key}]')

    def __str__(self):
        return getattr(Main, self.name).__str__()


def DefaultPathProbability(chanceNodes, probabilites):
    ''' Construct a defaultPathProbability (Julia Struct)

    changeNodes -- Vector of ChangeNodes
    probabilites -- Vector of Probabilities-objects for each ChangeNode
    '''

    return Main.eval(f'''DefaultPathProbability(
        {chanceNodes.name},
        {probabilites.name}
    )''')


def DefaultPathUtility(valueNodes, consequences):
    ''' Construct a defaultPathProbability (Julia Struct)

    valueNodes -- Vector of ValueNodes
    consequences -- Vector of Consequences-objects for each ValueNode
    '''

    return Main.eval(f'''DefaultPathUtility(
        {valueNodes.name},
        {consequences.name}
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
                    {states.name},
                    {chanceNodes.name},
                    {decisionNodes.name},
                    {valueNodes.name}
               )''')


class Model():
    ''' A wrapper for the DecisionProgramming.jl Model
    type.

    Members include functions that modify the model.

    self.name -- The name of the DecisionProgramming-variable in
        Julia main name space.

    self.probability_cut() -- Adds a probability cut to the model
        as a lazy constraint
    '''

    def __init__(self):
        ''' Initialize a pyDecisionProgramming Model '''
        self.name = unique_name()
        Main.eval(f'''{self.name} = Model()''')

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

        Main.eval(f'set_optimizer({self.name}, optimizer)')

    def optimize(self):
        ''' Run the current optimizer '''

        Main.eval(f'optimize!({self.name})')

    def probability_cut(self, pi_s, P, probability_scale_factor=1.0):
        '''Adds a probability cut to the model as a lazy constraint

        pi_s -- A PathProbabilityVariables object
        P -- An AbstractPathProbability object
        probability_scale_factor -- An additional scaling factor
        '''

        Main.eval(f'''DecisionVariables(
                              {self.name},
                              {pi_s.name},
                              {P.name}
                         )''')

    def __str__(self):
        return Main.eval(f'''{self.name}''')


def DecisionVariables(model, states, decisionNodes):
    ''' Construct a DecisionVariables-object (Julia Struct) '''

    return Main.eval(f'''DecisionVariables(
                          {model.name},
                          {states.name},
                          {decisionNodes.name}
                     )''')


class PathProbabilityVariables():
    ''' A wrapper for the DecisionProgramming.jl PathProbabilityVariables
    type.

    Without the wrapper it get's interpreted as a python dictionary,
    and does not preserve the Julia type.

    self.name -- The name of the DecisionProgramming-variable in
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

        self.name = unique_name()
        Main.dp_decisionVariables = decisionVariables
        Main.dp_defaultPathProbability = defaultPathProbability

        Main.eval(f'''{self.name} = PathProbabilityVariables(
                    {model.name},
                    dp_decisionVariables,
                    {states.name},
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
                          {model.name},
                          {pathProbabilityVariables.name},
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
                          {model.name},
                          {direction},
                          dp_objective
                     )''')


def DecisionStrategy(decisionVariables):
    ''' Create a JuMP optimizer

    decisionVariables -- A DecisionVariables object
    '''

    Main.dp_decisionVariables = decisionVariables
    return Main.eval('DecisionStrategy(dp_decisionVariables)')


def print_decision_strategy(states, decisionVariables):
    ''' Create a JuMP optimizer

    states -- A pyDecisionProgramming States object
    decisionVariables -- A DecisionVariables object
    '''

    Main.dp_decisionVariables = decisionVariables
    return Main.eval(f'''print_decision_strategy(
        {states.name},
        dp_decisionVariables)
        ''')


def UtilityDistribution(
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
        {states.name},
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
