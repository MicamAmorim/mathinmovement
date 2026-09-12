"""DSL visual declarativa e versionada do Math in Movement."""

from .coverage import (
    DEMO_USAGE,
    DEMO_VALIDATION_SET,
    QENEM_COMMON,
    QENEM_USAGE,
    QENEM_VALIDATION_SET,
    minimum_cover,
)
from .errors import DSLError, DSLReferenceError, DSLVersionError
from .registry import (
    action_capabilities,
    capability_names,
    get_action,
    get_object,
    object_capabilities,
)

__all__ = [
    "DSLError",
    "DSLReferenceError",
    "DSLVersionError",
    "DEMO_USAGE",
    "DEMO_VALIDATION_SET",
    "QENEM_COMMON",
    "QENEM_USAGE",
    "QENEM_VALIDATION_SET",
    "minimum_cover",
    "get_action",
    "get_object",
    "object_capabilities",
    "action_capabilities",
    "capability_names",
]
