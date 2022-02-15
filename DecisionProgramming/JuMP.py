''' Interface for Jump functionality necessary for optimizing models generated
from diagrams.
'''
from .juliaUtils import JuliaName
from .juliaUtils import julia
from .Diagram import ExpectedValue


class Model(JuliaName):
    """ Wraps a JuMP optimizer model and decision model variables. """

    def __init__(self):
        super().__init__()
        self.optimizer_set = False
        julia.eval(f'{self._name} = Model()')

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

        julia.eval(command)
        julia.eval(f'set_optimizer({self._name}, optimizer)')
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
            julia.eval(f'''@objective(
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
            julia.eval(command)
        else:
            raise ValueError("expected a dp.Diagram.ExpectedValue object"
            + " or a string")

    def optimize(self):
        ''' Run the current optimizer '''

        if not self.optimizer_set:
            self.setup_Gurobi_optimizer()

        julia.eval(f'optimize!({self._name})')

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
        julia.eval(f'''@constraint(
            {self._name},
            {argument_text}
        ); 0''')


class Expression(JuliaName):
    ''' Builds a JuMP expression from a string or set of strings.

    model: dp.Model
        A JuMP Model object

    loop: String (optional)
        Set of loop variables in the JuMP constraint format (see the
        contingent portfolio analysis page in examples)

    constraint: String
        The contraints in the JuMP format (see the contingent portfolio
         analysis page in examples)

    '''

    def __init__(self, model, *args):
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
        julia.eval(command)


class Array(JuliaName):
    ''' An array of JuMP variables. Makes it easier to define contraints
    using the @constraint syntax.

    Parameters
    ----------

    model: dp.Model
        A JuMP Model object

    dims: List of Integers
        A list corresponding to the size of the array in each of its
        dimensions.

    binary: Boolean (optional, default False)
        Wether the variables are boolean.

    '''

    def __init__(self, model, dims, binary=False):
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
        julia.eval(command)



