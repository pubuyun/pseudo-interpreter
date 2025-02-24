from cambridgeScript.interpreter.variables import VariableState
from cambridgeScript.parser.lexer import LiteralToken, Value, Token
from cambridgeScript.syntax_tree.expression import Expression, Assignable
from cambridgeScript.syntax_tree.types import Type, PrimitiveType, ArrayType
from itertools import product
from functools import reduce
import ast

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
    def __init__(self, prompt, origin, line):
        self.prompt = prompt
        self.origin = origin
        self.line = line

    def message(self) -> str:
        return "Unknown error"

    def parse_traceback(self) -> str:
        if not hasattr(self, "origin") or not hasattr(self, "line"):
            return ""
        if self.line >= 2 and self.line <= len(self.origin) - 1:
            return (
                f"{self.line-1} {self.origin[self.line-2]}\n{self.line} {self.origin[self.line-1]}\n"
                + "  "
                + "^" * len(self.origin[self.line - 1])
                + f"\n{self.line+1} {self.origin[self.line]}"
            )
        else:
            return f"{self.line} {self.origin[self.line-1]}\n  " + "^" * len(
                self.origin[self.line - 1]
            )

    def __str__(self) -> str:
        msg = self.message()
        trace = self.parse_traceback()
        return f"{msg}{': ' + chr(10) if trace else ''}{trace}"


class InvalidNode(InterpreterError):
    node: Statement | Expression
    token: Token
    origin: list[str]

    def __init__(self, node: Statement | Expression, token: Token, origin):
        self.node = node
        self.token = token
        self.origin = origin
        self.line = token.line

    def message(self) -> str:
        return f"Invalid node at {self.token.location}: {self.node}"


class PseudoOpError(InterpreterError, TypeError):
    operror: TypeError
    line: int

    def __init__(self, left, right, operror):
        self.left = left
        self.right = right
        self.operror = operror

    def message(self) -> str:
        return f"Unsupported operation for {self.left} and {self.right}: {self.operror}"


class PseudoBuiltinError(InterpreterError, ValueError):

    def message(self) -> str:
        return self.prompt


class PseudoInputError(InterpreterError, ValueError):

    def message(self) -> str:
        return f"Input Error: {self.prompt}"


class PseudoUndefinedError(InterpreterError, RuntimeError):

    def message(self) -> str:
        return f"Undefined Identifier: {self.prompt}"


class PseudoAssignmentError(InterpreterError, RuntimeError):

    def message(self) -> str:
        return f"Assignment Error: {self.prompt}"


class PseudoIndexError(InterpreterError, ValueError):

    def message(self) -> str:
        return self.prompt


class Interpreter(ExpressionVisitor, StatementVisitor):
    variable_state: VariableState

    def __init__(self, variable_state: VariableState, origin: str):
        from cambridgeScript.interpreter.builtin_function import create_builtins

        self.variable_state = variable_state
        self.variable_stack = []
        self.origin = origin.splitlines()
        self.builtins = create_builtins(self)

    def visit(self, thing: Expression | Statement):
        if isinstance(thing, Expression):
            return ExpressionVisitor.visit(self, thing)
        else:
            return StatementVisitor.visit(self, thing)

    def visit_statements(self, statements: list[Statement]):
        for stmt in statements:
            if isinstance(stmt, ReturnStmt):
                return self.visit_return(stmt)
            ret = self.visit(stmt)
            if ret is not None:
                return ret

    def visit_binary_op(self, expr: BinaryOp) -> Value:
        # Recursively visit left and right operands
        left = self.visit(expr.left)
        right = self.visit(expr.right)
        # Extract value from LiteralToken if necessary
        if isinstance(left, LiteralToken):
            left = left.value
        if isinstance(right, LiteralToken):
            right = right.value
        try:
            return expr.operator(left, right)
        except TypeError as e:
            raise PseudoOpError(expr.left, expr.right, e)

    def visit_unary_op(self, expr: UnaryOp) -> Value:
        operand = self.visit(expr.operand)
        return expr.operator(operand)

    def visit_function_call(self, func_call):
        function_name = func_call.function.token.value
        line = func_call.function.token.line
        if function_name in self.builtins:
            return self.builtins[function_name](func_call.params)
        elif function_name in self.variable_state.functions:
            func = self.variable_state.functions[function_name]

            current_scope = self.variable_state.variables.copy()
            # Create new scope for function parameters
            new_scope = self.variable_state.variables.copy()
            if func.params is not None:
                # Bind function parameters to new variable state
                for param, original_param in zip(func_call.params, func.params):
                    param_value = self.visit(param)
                    new_scope[original_param[0].value] = (
                        param_value,
                        original_param[1],
                    )

            # Enter new scope
            self.variable_state.variables = new_scope
            ret = self.visit_statements(func.body)
            for var in current_scope.keys():
                current_scope[var] = new_scope[var]
            # Restore previous scope
            self.variable_state.variables = current_scope
            if ret == None:
                raise RuntimeError(
                    f"There is a possibility that function {function_name} does not return any value."
                )
            return ret
        else:
            raise PseudoUndefinedError(
                f"name {function_name} is not defined", self.origin, line
            )

    def visit_array_index(self, expr: ArrayIndex) -> Value:
        name = expr.array.token.value
        if not isinstance(self.variable_state.variables[name][1], ArrayType):
            raise PseudoAssignmentError(
                f"{name} is not an array.", self.origin, expr.array.token.line
            )
        indices = [self.visit(indexexp) - 1 for indexexp in expr.index]
        try:
            target = reduce(
                lambda x, i: x[i],
                indices,
                self.variable_state.variables[name][0].copy(),
            )
        except IndexError:
            raise PseudoIndexError(
                f"List index out of range, trying to access {name}{''.join(f'[{indice}]' for indice in indices)}",
                self.origin,
                expr.array.token.line,
            )
        return target

    def visit_literal(self, expr: Literal) -> Value:
        if not isinstance(expr.token, LiteralToken):
            raise InvalidNode(expr.token, self.origin)
        return expr.token.value

    def visit_identifier(self, expr: Identifier) -> Value:
        name = expr.token.value
        if name in self.variable_state.variables:
            value = self.variable_state.variables[name][0]
        elif name in self.variable_state.constants:
            value = self.variable_state.constants[name]
        else:
            raise InterpreterError(f"Name {name} isn't defined")

        if value is None:
            raise InterpreterError(f"Name {name} has no value")
        return value

    def visit_proc_decl(self, stmt: ProcedureDecl) -> None:
        self.variable_state.procedures[stmt.name.value] = stmt

    def visit_func_decl(self, stmt: FunctionDecl) -> None:
        self.variable_state.functions[stmt.name.value] = stmt

    def visit_if(self, stmt: IfStmt) -> None:
        condition = self.visit(stmt.condition)
        if condition:
            return self.visit_statements(stmt.then_branch)
        elif stmt.else_branch is not None:
            return self.visit_statements(stmt.else_branch)

    def visit_case(self, stmt: CaseStmt):
        expr = self.visit(stmt.expr)
        for i in stmt.cases:
            if i[0].value == expr:
                return self.visit_statements(i[1])
        if stmt.otherwise is not None:
            return self.visit_statements(stmt.otherwise)

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
        while (
            current_value <= end_value if step_value > 0 else current_value >= end_value
        ):
            self.variable_state.variables[name] = (current_value, PrimitiveType.INTEGER)
            ret = self.visit_statements(stmt.body)
            if ret is not None:
                return ret
            current_value += step_value

    def visit_repeat_until(self, stmt: RepeatUntilStmt) -> None:
        ret = self.visit_statements(stmt.body)
        if ret is not None:
            return ret
        expr = self.visit(stmt.condition)
        while not expr:
            ret = self.visit_statements(stmt.body)
            if ret is not None:
                return ret
            expr = self.visit(stmt.condition)

    def visit_while(self, stmt: WhileStmt) -> None:
        if stmt.condition.token.value is True:
            raise RuntimeError("While loop never stops")
        expr = self.visit(stmt.condition)
        while expr:
            ret = self.visit_statements(stmt.body)
            if ret is not None:
                return ret
            expr = self.visit(stmt.condition)

    def create_nd_array(self, ranges, default=None):
        if not ranges:
            return default  # When there are no more ranges, return default value
        start, end = ranges[0]
        # Recursively create next level of list
        return [
            self.create_nd_array(ranges[1:], default) for _ in range(start, end + 1)
        ]

    def visit_variable_decl(self, stmt: VariableDecl) -> None:
        for name in stmt.names:
            if isinstance(stmt.vartype, ArrayType):
                ranges = [
                    (self.visit(a), self.visit(b)) for a, b in stmt.vartype.ranges
                ]
                self.variable_state.variables[name.value] = (
                    self.create_nd_array(ranges),
                    stmt.vartype,
                )
            else:
                self.variable_state.variables[name.value] = (None, stmt.vartype)

    def visit_constant_decl(self, stmt: ConstantDecl) -> None:
        self.variable_state.constants[stmt.name.value] = stmt.value.value

    def visit_input(self, stmt: InputStmt) -> None:
        if isinstance(stmt.variable, ArrayIndex):
            name = stmt.variable.array.token.value
            vartype = self.variable_state.variables[name][1].type
        else:
            name = stmt.variable.token.value
            vartype = self.variable_state.variables[name][1]

        if name not in self.variable_state.variables:
            raise InterpreterError(f"{name} was not declared")
        if name in self.variable_state.constants:
            raise PseudoInputError(
                f"{name} is a constant, which can't be inputted",
                self.origin,
                stmt.variable.token.line,
            )

        inp = input().strip()
        print(inp)
        if vartype == PrimitiveType.INTEGER:
            try:
                inp = float(inp)
            except:
                raise PseudoInputError(
                    f"Non number value entered for integer variable {name}",
                    self.origin,
                    stmt.variable.token.line,
                )
            if inp % 1:
                raise PseudoInputError(
                    f"Entered real number for integer variable {name}",
                    self.origin,
                    stmt.variable.token.line,
                )
            val = int(inp)
        elif vartype == PrimitiveType.BOOLEAN:
            if not inp.upper() in ["TRUE", "FALSE"]:
                raise PseudoInputError(
                    f"invalid input {inp} for boolean variable {name}",
                    self.origin,
                    stmt.variable.token.line,
                )
            val = True if inp.upper() == "TRUE" else False
        elif vartype == PrimitiveType.CHAR:
            val = inp[0]
        elif vartype == PrimitiveType.STRING:
            val = inp
        elif vartype == PrimitiveType.REAL:
            try:
                inp = float(inp)
            except:
                raise PseudoInputError(
                    f"Non number value entered for integer variable {name}",
                    self.origin,
                    stmt.variable.token.line,
                )
            val = inp
        if isinstance(stmt.variable, ArrayIndex):
            indices = [self.visit(indexexp) - 1 for indexexp in stmt.variable.index]
            arrcpy = self.variable_state.variables[name][0].copy()
            target = reduce(lambda x, i: x[i], indices[:-1], arrcpy)
            target[indices[-1]] = val
            self.variable_state.variables[name] = (
                arrcpy,
                self.variable_state.variables[name][1],
            )
        else:
            self.variable_state.variables[name] = (
                val,
                self.variable_state.variables[name][1],
            )

    def visit_output(self, stmt: OutputStmt) -> None:
        values = [self.visit(expr) for expr in stmt.values]
        print("".join(map(str, values)))

    def visit_return(self, stmt: ReturnStmt) -> Value:
        # Evaluate the return expression and return it to the caller
        return self.visit(stmt.value)

    def visit_f_open(self, stmt: FileOpenStmt) -> None:
        pass

    def visit_f_read(self, stmt: FileReadStmt) -> None:
        pass

    def visit_f_write(self, stmt: FileWriteStmt) -> None:
        pass

    def visit_f_close(self, stmt: FileCloseStmt) -> None:
        pass

    def visit_proc_call(self, stmt: ProcedureCallStmt) -> None:
        procedure_name = stmt.name.value
        line = stmt.name.line
        # Check if the procedure is defined
        if procedure_name not in self.variable_state.procedures:
            raise PseudoUndefinedError(
                f"Procedure {procedure_name} is not defined", self.origin, line
            )

        # Retrieve the procedure statement
        proc = self.variable_state.procedures[procedure_name]

        # Prepare a new scope for procedure parameters
        current_scope = self.variable_state.variables.copy()
        new_scope = current_scope.copy()
        if proc.params is not None:
            # Bind parameters passed to the procedure to the new scope
            for param, proc_param in zip(stmt.args, proc.params):
                param_value = self.visit(param)
                new_scope[proc_param[0].value] = (param_value, proc_param[1])

        # Enter the new scope for the procedure
        self.variable_state.variables = new_scope

        # Execute the procedure's statements
        for statement in proc.body:
            self.visit(statement)

        for var in current_scope.keys():
            current_scope[var] = new_scope[var]
        # Restore the previous scope
        self.variable_state.variables = current_scope

    def visit_assign(self, stmt: AssignmentStmt) -> None:
        if isinstance(stmt.target, ArrayIndex):
            name = stmt.target.array.token.value
            """ class ArrayIndex(Expression):
                    array: Expression
                    index: list[Expression] """
            val = self.visit(stmt.value)
            if not self.check_type(val, self.variable_state.variables[name][1].type):
                raise PseudoAssignmentError(
                    f"Trying to assign invalid type to array {name}, expected {self.variable_state.variables[name][1].type.name}",
                    self.origin,
                    stmt.target.array.token.line,
                )
            indices = [self.visit(indexexp) - 1 for indexexp in stmt.target.index]
            arrcpy = self.variable_state.variables[name][0].copy()
            target = reduce(lambda x, i: x[i], indices[:-1], arrcpy)
            target[indices[-1]] = val
            self.variable_state.variables[name] = (
                arrcpy,
                self.variable_state.variables[name][1],
            )
        else:
            name = stmt.target.token.value
            if name not in self.variable_state.variables:
                raise InterpreterError(f"{name} was not declared")
            if name in self.variable_state.constants:
                raise PseudoAssignmentError(
                    f"{name} is a constant, which can't be assigned a value.",
                    self.origin,
                    stmt.target.token.line,
                )
            val = self.visit(stmt.value)
            if self.check_type(val, self.variable_state.variables[name][1]):
                self.variable_state.variables[name] = (
                    val,
                    self.variable_state.variables[name][1],
                )
            else:
                raise PseudoAssignmentError(
                    f"Type Error for assigning {name}, expected {self.variable_state.variables[name][1].name}",
                    self.origin,
                    stmt.target.token.line,
                )

    def visit_program(self, stmt: Program) -> None:
        self.visit_statements(stmt.statements)

    def check_type(self, val, typ):
        if typ == PrimitiveType.INTEGER:
            if type(val) != int and type(val) != float:
                return False
            try:
                val = float(val)
            except:
                return False
            if val % 1:
                return False
            return True
        if typ == PrimitiveType.REAL:
            try:
                val = float(val)
            except:
                return False
            return True
        if typ == PrimitiveType.STRING:
            if isinstance(val, str):
                return True
            else:
                return False
        if typ == PrimitiveType.CHAR:
            if isinstance(val, str) and len(val) == 1:
                return True
            else:
                return False
        if typ == PrimitiveType.BOOLEAN:
            if isinstance(val, bool) or val in [0, 1]:
                return True
            else:
                return False
