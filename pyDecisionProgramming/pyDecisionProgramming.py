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
    ''' A wrapper for the DecisionProgramming.jl probabilities
    class.

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
        return getattr(Main, self.name)


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
                f'push!(Main.{self.name}, Main.{element.name})'
            )
            return

        Main.pDR_e = element
        Main.eval(
            f'push!(Main.{self.name}, Main.pDR_e)'
        )


def states(state_list):
    """ Set states in the graph

    state_list -- formatted as [(n, id)], where n is the
    number of states and id an iteger identifying the node
    """

    params = [(c, [n]) for c, n in state_list]

    graph_states = jdp.States(params)
    return graph_states


def statesFromLists(ids, state_counts):
    """ Set states in the graph

    ids -- a list of numbers identifying each node
    state_counts -- list of the number of states on each node
    """

    params = [(c, [n]) for c, n in zip(state_counts, ids)]
    graph_states = states(params)
    return graph_states


def consequences(id, probabilities):
    ''' Set values for each outcome on a value node

    id -- The id of the node
    probabilities -- A Probabilies-object describing the
    '''

    return jdp.Probabilities(id, probabilities)


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
