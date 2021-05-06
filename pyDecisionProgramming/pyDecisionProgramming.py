from julia import Pkg
from julia import Main
from julia import DecisionProgramming as jdp
import uuid


def activate():
    """ Activate a Julia environment in the working
        directory
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
        self.name = 'n'+uuid.uuid4().hex[:8]
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
        self.name = 'n'+uuid.uuid4().hex[:8]
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

        # Generate a unique 9 character name
        self.name = 'n'+uuid.uuid4().hex[:8]
        self.type = type

        Main.eval(f'{self.name} = Vector{{{type}}}()')

    def __str__(self):
        return getattr(Main, self.name).__str__()

    def setName(self, name):
        Main.eval(f'{name} = {self.name}')
        self.name = name

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
        ''' Set consequences to outcomes on a value node and
        build the corresponding Consequences object.

        state_list -- A list of tuples of the form formatted as [(n, id)],
        where n is the number of states and id an integer identifying the node
        '''

        Main.pDR_params = [(c, [n]) for c, n in state_list]
        self.name = 'n'+uuid.uuid4().hex[:8]
        print('States name', self.name)
        Main.eval(f'{self.name} = States(pDR_params)')

    def __getitem__(self, key):
        return Main.eval(f'{self.name}[{key}]')

    def __str__(self):
        return getattr(Main, self.name).__str__()


def ChanceNode(id, nodes):
    ''' Create a chance node at given location in the graph

    id -- The id of the node
    nodes -- List of nodes connected to this node

    return -- Changen
    '''

    if isinstance(nodes, Vector):
        assert(nodes.type == 'Node')

        return Main.eval(f'ChanceNode({id}, Main.{nodes.name})')

    else:
        # Try with a python object, Julia will type-check
        return jdp.ChanceNode(id, nodes)


def ValueNode(id, nodes):
    ''' Create a value node at given location in the graph

    id -- The id of the node
    nodes -- List of nodes connected to this node
    '''

    if isinstance(nodes, Vector):
        assert(nodes.type == 'Node')

        return Main.eval(f'ValueNode({id}, Main.{nodes.name})')

    else:
        # Try with a python object, Julia will type-check
        return jdp.ValueNode(id, nodes)


def DecisionNode(id, nodes):
    ''' Create a decision node at given location in the graph

    id -- The id of the node
    nodes -- List of nodes connected to this node
    '''

    if isinstance(nodes, Vector):
        assert(nodes.type == 'Node')

        return Main.eval(f'DecisionNode({id}, Main.{nodes.name})')

    else:
        # Try with a python object, Julia will type-check
        return jdp.DecisionNode(id, nodes)


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
