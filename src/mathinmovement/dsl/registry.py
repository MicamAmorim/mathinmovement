from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .errors import DSLError


@dataclass(frozen=True, slots=True)
class Capability:
    canonical: str
    kind: str
    handler: Callable
    since: str = "1.0"
    aliases: tuple[str, ...] = ()
    description: str = ""


_OBJECTS: dict[str, Capability] = {}
_ACTIONS: dict[str, Capability] = {}
_ALIASES: dict[tuple[str, str], str] = {}


def _register(table, *, kind, canonical, handler, since, aliases, description):
    if canonical in table:
        raise RuntimeError(f"Capacidade DSL duplicada: {canonical}")
    cap = Capability(canonical, kind, handler, since, aliases, description)
    table[canonical] = cap
    for alias in aliases:
        key = (kind, alias)
        if key in _ALIASES:
            raise RuntimeError(f"Alias DSL duplicado: {kind}:{alias}")
        _ALIASES[key] = canonical
    return handler


def object_type(canonical, *, since="1.0", aliases=(), description=""):
    def decorator(func):
        return _register(
            _OBJECTS,
            kind="object",
            canonical=canonical,
            handler=func,
            since=since,
            aliases=tuple(aliases),
            description=description,
        )
    return decorator


def action_type(canonical, *, since="1.0", aliases=(), description=""):
    def decorator(func):
        return _register(
            _ACTIONS,
            kind="action",
            canonical=canonical,
            handler=func,
            since=since,
            aliases=tuple(aliases),
            description=description,
        )
    return decorator


def _resolve(table, kind, name):
    if name in table:
        return table[name]
    canonical = _ALIASES.get((kind, name))
    if canonical is not None:
        return table[canonical]
    matches = [cap for key, cap in table.items() if key.rsplit(".", 1)[-1] == name]
    if len(matches) == 1:
        return matches[0]
    raise DSLError(f"Capacidade DSL desconhecida ({kind}): {name!r}")


def get_object(name):
    return _resolve(_OBJECTS, "object", str(name))


def get_action(name):
    return _resolve(_ACTIONS, "action", str(name))


def object_capabilities():
    return tuple(_OBJECTS[key] for key in sorted(_OBJECTS))


def action_capabilities():
    return tuple(_ACTIONS[key] for key in sorted(_ACTIONS))


def capability_names():
    return set(_OBJECTS) | set(_ACTIONS)
