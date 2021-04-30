from julia import Pkg
from julia import Main
from julia import DecisionProgramming as jdp


def setup_project():
    """ Activate a Julia environment in the working
        directory and install DecisionProgramming,
        Gurobi and JuMP
    """

    Pkg.activate(".")
    github_url = "https://github.com/gamma-opt/DecisionProgramming.jl.git"
    Pkg.add(url=github_url)
    Pkg.add("Gurobi")
    Pkg.add("JuMP")


def states(state_list):
    """ Set states in the graph

    state_list -- formatted as [(n, id)], where n is the
    number of states and id an iteger identifying the node
    """

    params = [(c, [n]) for c, n in state_list]

    graph_states = jdp.States(params)
    return graph_states


def create_states(ids, state_counts):
    """ Set states in the graph

    ids -- a list of numbers identifying each node
    state_counts -- list of the number of states on each node
    """

    params = [(c, [n]) for c, n in zip(state_counts, ids)]
    graph_states = states(params)
    return graph_states
