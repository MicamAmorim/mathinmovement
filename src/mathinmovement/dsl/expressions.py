from __future__ import annotations

import ast
import math
from typing import Any

from .errors import DSLError


_FUNCTIONS = {
    "abs": abs,
    "min": min,
    "max": max,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
}
_CONSTANTS = {"pi": math.pi, "tau": math.tau, "e": math.e}
_ALLOWED_BIN = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
    ast.Mod: lambda a, b: a % b,
}
_ALLOWED_UNARY = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}


def eval_expression(expression: str, variables: dict[str, float]) -> float:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise DSLError(f"Expressão DSL inválida: {expression!r}") from exc

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in variables:
                return float(variables[node.id])
            if node.id in _CONSTANTS:
                return float(_CONSTANTS[node.id])
            raise DSLError(f"Nome não permitido na expressão DSL: {node.id!r}")
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN:
            return _ALLOWED_BIN[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
            return _ALLOWED_UNARY[type(node.op)](visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func = _FUNCTIONS.get(node.func.id)
            if func is None:
                raise DSLError(f"Função não permitida na expressão DSL: {node.func.id!r}")
            if node.keywords:
                raise DSLError("Chamadas DSL não aceitam argumentos nomeados.")
            return float(func(*[visit(arg) for arg in node.args]))
        raise DSLError(
            "Expressão DSL contém construção não permitida: "
            f"{type(node).__name__}"
        )

    return float(visit(tree))


def resolve_value(value: Any, variables: dict[str, float]) -> Any:
    if isinstance(value, str) and value.startswith("="):
        return eval_expression(value[1:].strip(), variables)
    if isinstance(value, list):
        return [resolve_value(item, variables) for item in value]
    if isinstance(value, tuple):
        return tuple(resolve_value(item, variables) for item in value)
    if isinstance(value, dict):
        return {key: resolve_value(item, variables) for key, item in value.items()}
    return value
