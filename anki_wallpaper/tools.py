from functools import wraps, partial

import aqt


def patch_method(obj, method_name, action):
    original_method = getattr(obj, method_name)

    def decorator(function):
        if not hasattr(obj, method_name):
            raise Exception(f"Object {obj} has no method with the name {method_name}")

        if action == "replace":
            @wraps(function)
            def patched_method(*args, **kwargs):
                return function(*args, **kwargs)

        elif action == "append":
            @wraps(function)
            def patched_method(*args, **kwargs):
                result = original_method(*args, **kwargs)
                function(*args, **kwargs)
                return result

        else:
            raise ValueError(f"Bad action: {action}")

        function.original_method = original_method
        setattr(obj, method_name, patched_method)
        return function

    return decorator

append_to_method = partial(patch_method, action="append")
replace_method = partial(patch_method, action="replace")


def exception_to_string(exception):
    exception_class = exception.__class__.__name__
    return f"{exception_class}: {exception}"


def get_dialog_instance_or_none(name):
    try:
        return aqt.dialogs._dialogs[name][1]
    except KeyError:
        return None
