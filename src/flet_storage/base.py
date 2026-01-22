import json

import flet as ft


async def save(name: str, app_name: str, obj: object) -> None:
    """
    Saves a Python object to SharedPreferences after serializing it to JSON.

    Args:
        name (str): The specific key name for the data.
        app_name (str): The namespace or prefix for your application to avoid key collisions.
        obj (object): The Python object (dict, list, etc.) to be stored.

    Example:
        >>> await save("settings", "my_app", {"theme": "dark"})
    """
    name_obj = f"{app_name}.{name}"
    obj_json = json.dumps(obj)

    await ft.SharedPreferences().set(name_obj, obj_json)


async def load(name: str, app_name: str) -> object:
    """
    Loads a JSON string from SharedPreferences and deserializes it back into a Python object.

    Args:
        name (str): The specific key name of the data to retrieve.
        app_name (str): The namespace or prefix used during saving.

    Returns:
        object: The deserialized Python object.

    Note:
        Raises json.JSONDecodeError if the stored data is not valid JSON.
    """
    obj_json = await ft.SharedPreferences().get(f"{app_name}.{name}")
    obj = json.loads(obj_json)

    return obj


async def clear() -> None:
    """
    Removes all stored keys and values from the application's SharedPreferences.

    This operation is destructive and cannot be undone.
    """
    await ft.SharedPreferences().clear()


async def list_keys() -> None:
    """
    Prints a list of all existing keys in SharedPreferences to the console.

    Useful for debugging and inspecting the current state of the local storage.
    """
    keys = await ft.SharedPreferences().get_keys("")
    print(keys)
