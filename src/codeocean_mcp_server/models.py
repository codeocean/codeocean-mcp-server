from dataclasses import fields, is_dataclass
from typing import Any, List, Type, get_args, get_origin, get_type_hints

from pydantic import BaseModel, create_model


def dataclass_to_pydantic(
    data_class: Type[Any],
    cache: dict[Type[Any], Type[BaseModel]] = None
) -> Type[BaseModel]:
    """Convert a dataclass to Pydantic model.

    Recursively convert a frozen @dataclass (and nested dataclasses)
    into validating Pydantic BaseModel subclasses — resolving all
    forward/string annotations via get_type_hints().
    """
    if cache is None:
        cache = {}
    if data_class in cache:
        return cache[data_class]
    assert is_dataclass(data_class), f"{data_class.__name__} is not a dataclass"

    # 1) Resolve all annotations to real types (no strings)
    module_ns = vars(__import__(data_class.__module__, fromlist=["*"]))
    type_hints = get_type_hints(data_class, globalns=module_ns, localns=module_ns)

    definitions: dict[str, tuple[type, Any]] = {}
    for filed in fields(data_class):
        # Use the evaluated hint if available, else the raw annotation
        typ = type_hints.get(filed.name, filed.type)
        default = filed.default
        field_type = typ
        origin = get_origin(typ)
        args = get_args(typ)

        # 2) Nested dataclass → build or fetch nested model
        if is_dataclass(typ):
            nested_model = dataclass_to_pydantic(typ, cache)
            field_type = nested_model

        # 3) List[...] of dataclasses → List[NestedModel]
        elif origin in (list, List) and args and is_dataclass(args[0]):
            nested_model = dataclass_to_pydantic(args[0], cache)
            field_type = List[nested_model]


        definitions[filed.name] = (field_type, default)

    # 5) Dynamically create the Pydantic model
    model = create_model( f"{data_class.__name__}Model", __base__=BaseModel, **definitions)

    # 6) Rebuild to resolve any remaining forward refs
    model.model_rebuild()

    cache[data_class] = model
    return model
