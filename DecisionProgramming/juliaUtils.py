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
    dp.JuliaName
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
        ----------
        command: string
            A string containing Julia code

        '''
        return Main.eval(command)


# Expose the Julia runner as dp.julia
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


