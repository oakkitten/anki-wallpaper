from functools import wraps, partial

import aqt


def patch_method(obj, method_name, action):
    original_method = getattr(obj, method_name)

    def decorator(function):
        if action == "replace":
            @wraps(original_method)
            def patched_method(*args, **kwargs):
                return function(*args, **kwargs)

        elif action == "prepend":
            @wraps(original_method)
            def patched_method(*args, **kwargs):
                function(*args, **kwargs)
                return original_method(*args, **kwargs)

        elif action == "append":
            @wraps(original_method)
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

prepend_to_method = partial(patch_method, action="prepend")
append_to_method = partial(patch_method, action="append")
replace_method = partial(patch_method, action="replace")


def get_dialog_instance_or_none(name):
    try:
        return aqt.dialogs._dialogs[name][1]
    except KeyError:
        return None
