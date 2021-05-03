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
    Pkg.add("JuMP")

    Main.eval('using DecisionProgramming')
    Main.eval('using Gurobi')
    Main.eval('using JuMP')


def states(state_list):
    """ Set states in the graph

    state_list -- formatted as [(n, id)], where n is the
    number of states and id an iteger identifying the node
    """

    params = [(c, [n]) for c, n in state_list]

    graph_states = jdp.States(params)
    return graph_states


def createFromLists(ids, state_counts):
    """ Set states in the graph

    ids -- a list of numbers identifying each node
    state_counts -- list of the number of states on each node
    """

    params = [(c, [n]) for c, n in zip(state_counts, ids)]
    graph_states = states(params)
    return graph_states


def createVector(type: str, name: str = None):
    ''' Create a new Julia vector of a given type

    type: str -- The Julia type the vector contains
    name: str -- Name of the vector in the Julia main namespace
    '''

    if name is None:
        # Generate a unique 9 character name
        name = 'n'+uuid.uuid4().hex[:8]
        print(name)

    print(f'{name} = Vector{{{type}}}()')
    Main.eval(f'{name} = Vector{{{type}}}()')
    return getattr(Main, name)


def pushToVector(vec, element):
    ''' Push and element to a given vector

    vec -- the vector
    element -- the new element
    '''

    Main.v = vec
    Main.e = element
    Main.eval('push!(Main.v, Main.e)')
    return Main.v


def chanceNode(id, nodes):
    ''' Create a chance node at given location in the graph

    id -- The id of the node
    nodes -- A vector of connected nodes
    '''

    return jdp.ChanceNode(id, nodes)


def probabilities(id, probabilities):
    ''' Create a chance node at given location in the graph

    id -- The id of the node
    nodes -- A vector of connected nodes
    '''

    return jdp.Probabilities(id, probabilities)
