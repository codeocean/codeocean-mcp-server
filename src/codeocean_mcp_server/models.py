from dataclasses import fields, is_dataclass
from typing import Any, List, Type, get_args, get_origin, get_type_hints

from pydantic import BaseModel, Field, create_model


def dataclass_to_pydantic(
    data_class: Type[Any], cache: dict[Type[Any], Type[BaseModel]] = None
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
    assert is_dataclass(data_class), (
        f"{data_class.__name__} is not a dataclass"
    )

    # 1) Resolve all annotations to real types (no strings)
    module_ns = vars(
        __import__(data_class.__module__, fromlist=["*"])
    )
    type_hints = get_type_hints(
        data_class, globalns=module_ns, localns=module_ns
    )

    definitions: dict[str, tuple[type, Any]] = {}
    for field in fields(data_class):
        # Use the evaluated hint if available, else the raw annotation
        typ = type_hints.get(field.name, field.type)
        default = field.default
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

        # 4) Handle field with description from metadata
        field_info = default
        if field.metadata and "description" in field.metadata:
            # Create a Pydantic Field with description
            field_info = Field(
                default=default, description=field.metadata["description"]
            )

        definitions[field.name] = (field_type, field_info)

    # 5) Dynamically create the Pydantic model
    model = create_model(
        f"{data_class.__name__}Model",
        __base__=BaseModel,
        __doc__=data_class.__doc__,
        **definitions
    )

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
