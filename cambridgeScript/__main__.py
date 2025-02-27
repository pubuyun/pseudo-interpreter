import click
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cambridgeScript.parser.lexer import parse_tokens
from cambridgeScript.parser.parser import Parser
from cambridgeScript.interpreter.variables import VariableState
from cambridgeScript.interpreter.interpreter import Interpreter


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    if ctx.invoked_subcommand:
        return

    click.echo("REPL is under construction")


@cli.command()
@click.argument("file", type=click.File())
def run(file):
    # Read source code
    code = file.read()

    # Parse code
    tokens = parse_tokens(code)
    parsed = Parser.parse_program(tokens, code)

    # Create interpreter with simple input stream
    interpreter = Interpreter(VariableState(), code, sys.stdin)
    interpreter.visit(parsed)


if __name__ == "__main__":
    cli()
