from dataclasses import MISSING, fields, is_dataclass
from dataclasses import Field as DataclassField
from typing import Any, List, Type, get_args, get_origin, get_type_hints

from pydantic import BaseModel, Field, create_model


def _get_field_info(field: DataclassField) -> Any:
    """Get Pydantic field info from dataclass field.

    Args:
        field: Dataclass field to convert

    Returns:
        Pydantic field info (Field, Ellipsis, or default value)

    """
    default = field.default
    has_description = field.metadata and "description" in field.metadata

    if has_description:
        description = field.metadata["description"]
        if default is MISSING:
            # Required field with description
            return Field(description=description)
        else:
            # Optional field with default and description
            return Field(default=default, description=description)
    elif default is MISSING:
        # Required field without description
        return ...
    else:
        # Optional field with default but no description
        return default


def dataclass_to_pydantic(data_class: Type[Any], cache: dict[Type[Any], Type[BaseModel]] = None) -> Type[BaseModel]:
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
    for field in fields(data_class):
        # Use the evaluated hint if available, else the raw annotation
        typ = type_hints.get(field.name, field.type)
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

        # 4) Get Pydantic field info
        field_info = _get_field_info(field)

        definitions[field.name] = (field_type, field_info)

    # 5) Dynamically create the Pydantic model
    model = create_model(f"{data_class.__name__}Model", __base__=BaseModel, __doc__=data_class.__doc__, **definitions)

    # 6) Override the schema generation to include description from docstring
    if data_class.__doc__:
        original_json_schema = model.model_json_schema

        def custom_json_schema(*args, **kwargs):
            schema = original_json_schema(*args, **kwargs)
            schema["description"] = data_class.__doc__.strip()
            return schema

        model.model_json_schema = custom_json_schema

    model.model_rebuild()

    def to_dict_method(self):
        return self.model_dump()

    # 7) Add a method to convert the model instance to a dictionary
    model.to_dict = to_dict_method

    cache[data_class] = model
    return model
