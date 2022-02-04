""" Wrappers for node types """
from julia import DecisionProgramming as jdp
from .juliaUtils import julia
from .juliaUtils import JuliaName


class ChanceNode(JuliaName):
    """ Create a change node that can be added into a Diagram

    Parameters
    ----------
    id: str
        The id of the node

    nodes: list(str)
        List of nodes connected to this node

    connected_nodes:
        List of node connected_nodes

    """

    def __init__(self, id, nodes, connected_nodes):
        super().__init__()

        julia.tmp = jdp.ChanceNode(id, nodes, connected_nodes)
        julia.eval(f'{self._name} = tmp')


class DecisionNode(JuliaName):
    """ Create a decision node that can be added into a Diagram

    Parameters
    ----------
    id: str
        The id of the node

    nodes: list(str)
        List of nodes connected to this node

    connected_nodes:
        List of node connected_nodes

    """

    def __init__(self, id, nodes, connected_nodes):
        super().__init__()
        julia.tmp = jdp.DecisionNode(id, nodes, connected_nodes)
        julia.eval(f'{self._name} = tmp')


class ValueNode(JuliaName):
    """ Create a value node that can be added into a Diagram

    Parameters
    ----------
    id: str
        The id of the node

    nodes: list(str)
        List of nodes connected to this node

    connected_nodes:
        List of node connected_nodes

    """

    def __init__(self, id, nodes):
        super().__init__()

        self.leaves = nodes

        julia.tmp = jdp.ValueNode(id, nodes)
        julia.eval(f'{self._name} = tmp')

