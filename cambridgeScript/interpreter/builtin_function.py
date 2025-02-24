import random
from cambridgeScript.interpreter.interpreter import (
    InterpreterError,
    InvalidNode,
    PseudoOpError,
    PseudoBuiltinError,
    PseudoInputError,
    PseudoUndefinedError,
    PseudoAssignmentError,
    PseudoIndexError,
)


def create_builtins(interpreter):
    def substring(params):
        if len(params) != 3:
            raise PseudoBuiltinError(
                "SUBSTRING function requires exactly three parameters.",
                interpreter.origin,
                interpreter.line,
            )

        string_value = interpreter.visit(params[0])
        start_index = interpreter.visit(params[1])
        length = interpreter.visit(params[2])

        if (
            not isinstance(string_value, str)
            or not isinstance(start_index, int)
            or not isinstance(length, int)
        ):
            raise PseudoBuiltinError(
                "Invalid parameter types for SUBSTRING function.",
                interpreter.origin,
                interpreter.line,
            )

        if start_index + length - 1 > len(string_value):
            raise PseudoBuiltinError(
                f"Attempt to access characters beyond the length in SUBSTRING."
                f"(length:{len(string_value)}, last character you trying to access:{start_index + length - 1})",
                interpreter.origin,
                interpreter.line,
            )

        return string_value[start_index - 1 : start_index + length - 1]

    def random_func(params):
        if len(params) != 0:
            raise PseudoBuiltinError(
                "RANDOM function does not take any parameters.",
                interpreter.origin,
                interpreter.line,
            )
        return random.random()

    def mod(params):
        if len(params) != 2:
            raise PseudoBuiltinError(
                "MOD function requires exactly two parameters.",
                interpreter.origin,
                interpreter.line,
            )

        a = interpreter.visit(params[0])
        b = interpreter.visit(params[1])

        if not isinstance(a, int) or not isinstance(b, int):
            raise PseudoBuiltinError(
                "MOD function requires integer parameters.",
                interpreter.origin,
                interpreter.line,
            )

        return a % b

    def div(params):
        if len(params) != 2:
            raise PseudoBuiltinError(
                "DIV function requires exactly two parameters.",
                interpreter.origin,
                interpreter.line,
            )

        a = interpreter.visit(params[0])
        b = interpreter.visit(params[1])

        if not isinstance(a, int) or not isinstance(b, int):
            raise PseudoBuiltinError(
                "DIV function requires integer parameters.",
                interpreter.origin,
                interpreter.line,
            )

        return a // b

    def round_func(params):
        if len(params) != 2:
            raise PseudoBuiltinError(
                "ROUND function requires exactly two parameters.",
                interpreter.origin,
                interpreter.line,
            )

        a = interpreter.visit(params[0])
        b = interpreter.visit(params[1])

        if not (isinstance(a, float) or isinstance(a, int)) or not isinstance(b, int):
            raise PseudoBuiltinError(
                "ROUND function requires a number and an integer.",
                interpreter.origin,
                interpreter.line,
            )

        return round(a, b)

    def length(params):
        if len(params) != 1:
            raise PseudoBuiltinError(
                "LENGTH function requires exactly one parameter.",
                interpreter.origin,
                interpreter.line,
            )

        a = interpreter.visit(params[0])

        if not isinstance(a, str):
            raise PseudoBuiltinError(
                "LENGTH function requires a string parameter.",
                interpreter.origin,
                interpreter.line,
            )

        return len(a)

    def lcase(params):
        if len(params) != 1:
            raise PseudoBuiltinError(
                "LCASE function requires exactly one parameter.",
                interpreter.origin,
                interpreter.line,
            )

        a = interpreter.visit(params[0])

        if not isinstance(a, str):
            raise PseudoBuiltinError(
                "LCASE function requires a string parameter.",
                interpreter.origin,
                interpreter.line,
            )

        return a.lower()

    def ucase(params):
        if len(params) != 1:
            raise PseudoBuiltinError(
                "UCASE function requires exactly one parameter.",
                interpreter.origin,
                interpreter.line,
            )

        a = interpreter.visit(params[0])

        if not isinstance(a, str):
            raise PseudoBuiltinError(
                "UCASE function requires a string parameter.",
                interpreter.origin,
                interpreter.line,
            )

        return a.upper()

    return {
        "SUBSTRING": substring,
        "RANDOM": random_func,
        "MOD": mod,
        "DIV": div,
        "ROUND": round_func,
        "LENGTH": length,
        "LCASE": lcase,
        "UCASE": ucase,
    }
