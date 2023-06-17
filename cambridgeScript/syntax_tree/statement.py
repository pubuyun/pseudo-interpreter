__all__ = [
    "StatementVisitor",
    "Statement",
    "ProcedureDecl",
    "FunctionDecl",
    "IfStmt",
    "CaseStmt",
    "ForStmt",
    "RepeatUntilStmt",
    "WhileStmt",
    "VariableDecl",
    "ConstantDecl",
    "InputStmt",
    "OutputStmt",
    "ReturnStmt",
    "FileOpenStmt",
    "FileReadStmt",
    "FileWriteStmt",
    "FileCloseStmt",
    "ProcedureCallStmt",
    "AssignmentStmt",
    # "ExprStmt",
    "Program",
]

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from cambridgeScript.parser.lexer import Token
from cambridgeScript.syntax_tree.expression import Expression, Assignable
from cambridgeScript.syntax_tree.types import Type


class StatementVisitor(ABC):
    def visit(self, stmt: "Statement") -> Any:
        return stmt.accept(self)

    @abstractmethod
    def visit_proc_decl(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_func_decl(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_if(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_case(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_for_loop(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_repeat_until(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_while(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_variable_decl(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_constant_decl(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_input(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_output(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_return(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_f_open(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_f_read(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_f_write(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_f_close(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_proc_call(self, stmt) -> Any:
        pass

    @abstractmethod
    def visit_assign(self, stmt) -> Any:
        pass

    # @abstractmethod
    # def visit_expr_stmt(self, stmt) -> Any:
    #     pass

    @abstractmethod
    def visit_program(self, stmt) -> Any:
        pass


class Statement(ABC):
    @abstractmethod
    def accept(self, visitor: StatementVisitor) -> Any:
        pass


@dataclass
class ProcedureDecl(Statement):
    name: Token
    params: list[tuple[Token, "Type"]] | None
    body: list[Statement]

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_proc_decl(self)


@dataclass
class FunctionDecl(Statement):
    name: Token
    params: list[tuple[Token, "Type"]] | None
    return_type: "Type"
    body: list[Statement]

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_func_decl(self)


@dataclass
class IfStmt(Statement):
    condition: Expression
    then_branch: list[Statement]
    else_branch: list[Statement] | None

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_if(self)


@dataclass
class CaseStmt(Statement):
    expr: Expression
    cases: list[tuple[Token, Statement]]
    otherwise: Statement | None

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_case(self)


@dataclass
class ForStmt(Statement):
    variable: Assignable
    start: Expression
    end: Expression
    step: Expression | None
    body: list[Statement]

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_for_loop(self)


@dataclass
class RepeatUntilStmt(Statement):
    body: list[Statement]
    condition: Expression

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_repeat_until(self)


@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: list[Statement]

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_while(self)


@dataclass
class VariableDecl(Statement):
    name: Token
    type: "Type"

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_variable_decl(self)


@dataclass
class ConstantDecl(Statement):
    name: Token
    value: Token

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_constant_decl(self)


@dataclass
class InputStmt(Statement):
    variable: Assignable

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_input(self)


@dataclass
class OutputStmt(Statement):
    values: list[Expression]

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_output(self)


@dataclass
class ReturnStmt(Statement):
    value: Expression

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_return(self)


@dataclass
class FileOpenStmt(Statement):
    file: Token
    mode: Token

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_f_open(self)


@dataclass
class FileReadStmt(Statement):
    file: Token
    target: Assignable

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_f_read(self)


@dataclass
class FileWriteStmt(Statement):
    file: Token
    value: Expression

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_f_write(self)


@dataclass
class FileCloseStmt(Statement):
    file: Token

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_f_close(self)


@dataclass
class ProcedureCallStmt(Statement):
    name: Token
    args: list[Expression] | None

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_proc_call(self)


@dataclass
class AssignmentStmt(Statement):
    target: Expression
    value: Expression

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_assign(self)


# @dataclass
# class ExprStmt(Statement):
#     expr: Expression
#
#     def accept(self, visitor: StatementVisitor) -> Any:
#         return visitor.visit_expr_stmt(self)


@dataclass
class Program(Statement):
    statements: list[Statement]

    def accept(self, visitor: StatementVisitor) -> Any:
        return visitor.visit_program(self)
