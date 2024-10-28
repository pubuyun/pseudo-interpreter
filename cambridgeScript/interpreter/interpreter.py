from cambridgeScript.interpreter.variables import VariableState
from cambridgeScript.parser.lexer import LiteralToken, Value
from cambridgeScript.syntax_tree.expression import Expression, Assignable
from cambridgeScript.syntax_tree.types import Type, PrimitiveType, ArrayType

from cambridgeScript.syntax_tree import (
    Expression,
    Identifier,
    Literal,
    ArrayIndex,
    FunctionCall,
    UnaryOp,
    BinaryOp,
    Statement,
    AssignmentStmt,
    ProcedureCallStmt,
    FileCloseStmt,
    FileWriteStmt,
    FileReadStmt,
    FileOpenStmt,
    ReturnStmt,
    OutputStmt,
    InputStmt,
    ConstantDecl,
    VariableDecl,
    WhileStmt,
    RepeatUntilStmt,
    ForStmt,
    CaseStmt,
    IfStmt,
    FunctionDecl,
    ProcedureDecl,
    Program,
)
from cambridgeScript.syntax_tree.visitors import ExpressionVisitor, StatementVisitor
import random

class InterpreterError(Exception):
    pass


        

class InvalidNode(InterpreterError):
    node: Statement | Expression

    def __init__(self, node: Statement | Expression):
        self.node = node


class Interpreter(ExpressionVisitor, StatementVisitor):
    variable_state: VariableState

    def __init__(self, vairable_state: VariableState):
        self.variable_state = vairable_state

    def visit(self, thing: Expression | Statement):
        if isinstance(thing, Expression):
            return ExpressionVisitor.visit(self, thing)
        else:
            return StatementVisitor.visit(self, thing)

    def visit_statements(self, statements: list[Statement]):
        for stmt in statements:
            self.visit(stmt)

    def visit_binary_op(self, expr: BinaryOp) -> Value:
        left = self.visit(expr.left)
        right = self.visit(expr.right)
        return expr.operator(left, right)

    def visit_unary_op(self, expr: UnaryOp) -> Value:
        operand = self.visit(expr.operand)
        return expr.operator(operand)

    def visit_function_call(self, func_call):
        # Retrieve the function name
        function_name = func_call.function.token.value

        if function_name == "SUBSTRING":
            # Expecting three parameters: string, start index, length
            if len(func_call.params) != 3:
                raise ValueError("SUBSTRING function requires exactly three parameters.")
            
            # Evaluate the parameters
            string_value = self.visit(func_call.params[0])
            start_index = self.visit(func_call.params[1])
            length = self.visit(func_call.params[2])
            
            # Check if parameters are of expected types
            if not isinstance(string_value, str) or not isinstance(start_index, int) or not isinstance(length, int):
                raise TypeError("Invalid parameter types for SUBSTRING function.")
            
            # Perform the substring operation
            result = string_value[start_index:start_index + length]
            return result

        elif function_name == "RANDOM":
            # Expecting zero parameters
            if len(func_call.params) != 0:
                raise ValueError("RANDOM function does not take any parameters.")
            
            # Generate a random real number between 0 and 1
            return random.random()
        
        elif function_name == "MOD":
            # Expecting two parameters: a and b
            if len(func_call.params) != 2:
                raise ValueError("MOD function requires exactly two parameters.")
            
            a = self.visit(func_call.params[0])
            b = self.visit(func_call.params[1])
            
            # Perform modulo operation
            if not isinstance(a, int) or not isinstance(b, int):
                raise TypeError("MOD function requires integer parameters.")
            
            return a % b

        elif function_name == "DIV":
            # Expecting two parameters: a and b
            if len(func_call.params) != 2:
                raise ValueError("DIV function requires exactly two parameters.")
            
            a = self.visit(func_call.params[0])
            b = self.visit(func_call.params[1])
            
            # Perform floor division
            if not isinstance(a, int) or not isinstance(b, int):
                raise TypeError("DIV function requires integer parameters.")
            
            return a // b

        elif function_name == "ROUND":
            # Expecting two parameters: a (number), b (decimal points)
            if len(func_call.params) != 2:
                raise ValueError("ROUND function requires exactly two parameters.")
            
            a = self.visit(func_call.params[0])
            b = self.visit(func_call.params[1])
            
            # Perform rounding
            if not (isinstance(a, float) or isinstance(a, int)) or not isinstance(b, int):
                raise TypeError("ROUND function requires a number and an integer.")
            
            return round(a, b)
        
        elif function_name == "LENGTH":
            # Expecting one parameter: a (string)
            if len(func_call.params) != 1:
                raise ValueError("LENGTH function requires exactly one parameter.")
            
            a = self.visit(func_call.params[0])
            
            # Check type and get the length
            if not isinstance(a, str):
                raise TypeError("LENGTH function requires a string parameter.")
            
            return len(a)

        elif function_name == "LCASE":
            # Expecting one parameter: a (string)
            if len(func_call.params) != 1:
                raise ValueError("LCASE function requires exactly one parameter.")
            
            a = self.visit(func_call.params[0])
            
            # Convert to lowercase
            if not isinstance(a, str):
                raise TypeError("LCASE function requires a string parameter.")
            
            return a.lower()
        
        elif function_name == "UCASE":
            # Expecting one parameter: a (string)
            if len(func_call.params) != 1:
                raise ValueError("UCASE function requires exactly one parameter.")
            
            a = self.visit(func_call.params[0])
            
            # Convert to uppercase
            if not isinstance(a, str):
                raise TypeError("UCASE function requires a string parameter.")
            
            return a.upper()
        
        else:
            # Raise an error for unimplemented functions
            raise NotImplementedError(f"Function '{function_name}' is not implemented.")

            
    def visit_array_index(self, expr: ArrayIndex) -> Value:
        raise NotImplemented

    def visit_literal(self, expr: Literal) -> Value:
        if not isinstance(expr.token, LiteralToken):
            raise InvalidNode
        return expr.token.value

    def visit_identifier(self, expr: Identifier) -> Value:
        name = expr.token.value
        if name not in self.variable_state.variables:
            raise InterpreterError(f"Name {name} isn't defined")
        value = self.variable_state.variables[name][0]
        if value is None:
            raise InterpreterError(f"Name {name} has no value")
        return value

    def visit_proc_decl(self, stmt: ProcedureDecl) -> None:
        pass

    def visit_func_decl(self, stmt: FunctionDecl) -> None:
        pass

    def visit_if(self, stmt: IfStmt) -> None:
        condition = self.visit(stmt.condition)
        if condition:
            self.visit_statements(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.visit_statements(stmt.else_branch)

    def visit_case(self, stmt: CaseStmt) -> None:
        expr = self.visit(stmt.expr)
        for i in stmt.cases:
            if i[0].value == expr:
                self.visit_statements(i[1])
                return 0
        self.visit_statements(stmt.otherwise) 

    def visit_for_loop(self, stmt: ForStmt) -> None:
        if isinstance(stmt, ArrayIndex):
            raise NotImplemented
        name = stmt.variable.token.value
        current_value = self.visit(stmt.start)
        end_value = self.visit(stmt.end)
        if stmt.step is not None:
            step_value = self.visit(stmt.step)
        else:
            step_value = 1
        while current_value <= end_value:
            self.variable_state.variables[name] = current_value
            self.visit_statements(stmt.body)
            current_value += step_value

    def visit_repeat_until(self, stmt: RepeatUntilStmt) -> None:
        self.visit_statements(stmt.body)
        expr = self.visit(stmt.condition)
        while not expr:
            self.visit_statements(stmt.body)
            expr = self.visit(stmt.condition)

    def visit_while(self, stmt: WhileStmt) -> None:
        expr = self.visit(stmt.condition)
        while expr:
            self.visit_statements(stmt.body)
            expr = self.visit(stmt.condition)

    def visit_variable_decl(self, stmt: VariableDecl) -> None:
        print(stmt.name.value)
        self.variable_state.variables[stmt.name.value] = (None, stmt.vartype)
    def visit_constant_decl(self, stmt: ConstantDecl) -> None:
        self.variable_state.constants[stmt.name.value] = stmt.value
    def visit_input(self, stmt: InputStmt) -> None:
        if isinstance(stmt.variable, ArrayIndex):
            raise NotImplemented
        name = stmt.variable.token.value
        if name not in self.variable_state.variables:
            raise InterpreterError(f"{name} was not declared")
        if name in self.variable_state.constants:
            raise Interpreter(f"{name} is a constant, which can't be input")
        vartype = self.variable_state.variables[name][1]
        print(Type)
        if isinstance(vartype, PrimitiveType):
            if vartype == PrimitiveType.INTEGER:
                self.variable_state.variables[name][0] = int(input())
            elif vartype == PrimitiveType.BOOLEAN:
                self.variable_state.variables[name][0] = True if input().upper() == "TRUE" else False
            elif vartype == PrimitiveType.CHAR:
                self.variable_state.variables[name][0] = input()[0]
            elif vartype == PrimitiveType.STRING:
                self.variable_state.variables[name][0] = input()
            elif vartype == PrimitiveType.REAL:
                self.variable_state.variables[name][0] = float(input())
        else:
            raise NotImplementedError
    def visit_output(self, stmt: OutputStmt) -> None:
        values = []
        for expr in stmt.values:
            values.append(self.visit(expr))
        print("".join(map(str, values)))

    def visit_return(self, stmt: ReturnStmt) -> None:
        pass

    def visit_f_open(self, stmt: FileOpenStmt) -> None:
        pass

    def visit_f_read(self, stmt: FileReadStmt) -> None:
        pass

    def visit_f_write(self, stmt: FileWriteStmt) -> None:
        pass

    def visit_f_close(self, stmt: FileCloseStmt) -> None:
        pass

    def visit_proc_call(self, stmt: ProcedureCallStmt) -> None:
        pass

    def visit_assign(self, stmt: AssignmentStmt) -> None:
        if isinstance(stmt.target, ArrayIndex):
            raise NotImplemented
        name = stmt.target.token.value
        if name not in self.variable_state.variables:
            raise InterpreterError(f"{name} was not declared")
        self.variable_state.variables[name] = ( self.visit(stmt.value), self.variable_state.variables[name][1])

    def visit_program(self, stmt: Program) -> None:
        self.visit_statements(stmt.statements)
