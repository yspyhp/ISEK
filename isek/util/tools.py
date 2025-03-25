import inspect
import re
import json
import hashlib


def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }


def load_json_from_chat_response(chat_result):
    pattern = r'```json(.*?)```'
    match = re.search(pattern, chat_result, re.DOTALL)
    if match:
        json_data = match.group(1).strip()
        return json.loads(json_data)
    else:
        raise RuntimeError(f"Source str[{chat_result}] no json content extracted.")


def split_list(input_list, chunk_size):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def md5(source):
    return hashlib.md5(source.encode()).hexdigest()


def dict_md5(dict_content, exclude_fields=None):
    dict_to_md5 = dict(dict_content)
    exclude_dict = {}
    if exclude_fields and len(exclude_fields) > 0:
        for exclude_field in exclude_fields:
            if exclude_field in dict_to_md5:
                exclude_dict[exclude_field] = dict_to_md5[exclude_field]
                del dict_to_md5[exclude_field]
    sorted_json_str = json.dumps(dict_to_md5, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(sorted_json_str.encode()).hexdigest()
