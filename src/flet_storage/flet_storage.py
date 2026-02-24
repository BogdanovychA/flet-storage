import asyncio
import json
from typing import Any

import flet as ft


class FletStorage:
    """
    A wrapper for flet.SharedPreferences that provides namespaced storage.

    This class ensures that all keys are prefixed with a specific application name,
    preventing data collisions between different apps. It also handles
    JSON serialization and deserialization automatically.

    Supported data types:
        - dict, list, str, int, float, bool, None
        - set (automatically preserved during serialization/deserialization)

    Example:
        storage = FletStorage("my_app")
        await storage.set("tags", {"python", "flet"})
        tags = await storage.get("tags")  # Returns set, not list!
    """

    def __init__(self, app_name: str) -> None:
        """
        Initializes the storage with a specific namespace.

        Args:
            app_name: The unique namespace for the application.
        """
        self.app_name = app_name
        self.storage = ft.SharedPreferences()

    @staticmethod
    def _set_default(obj):
        """
        JSON serializer helper that handles 'set' objects.

        Converts sets to a special dict format with type metadata to preserve
        the set type during deserialization.

        Args:
            obj: Object to serialize (expecting a set).

        Returns:
            dict: A dictionary with '__type__' marker and set values as list.

        Raises:
            TypeError: If obj is not a set (allows default encoder to handle it).

        Example:
            _set_default({"python", "flet"})
            {'__type__': 'set', 'values': ['python', 'flet']}
        """
        if isinstance(obj, set):
            return {"__type__": "set", "values": list(obj)}
        raise TypeError

    @staticmethod
    def _object_hook(dct):
        """
        JSON deserializer helper that reconstructs sets from stored format.

        Checks each dictionary during deserialization for the '__type__': 'set'
        marker and converts it back to a Python set.

        Args:
            dct: Dictionary from JSON deserialization.

        Returns:
            set or dict: Original set if marker found, otherwise unchanged dict.

        Example:
            _object_hook({'__type__': 'set', 'values': ['python', 'flet']})
            {'python', 'flet'}
        """
        if dct.get("__type__") == "set":
            return set(dct["values"])
        return dct

    async def set(self, key: str, obj: object) -> bool:
        """
        Serializes an object to JSON and stores it under a namespaced key.

        Args:
            key: The unique key identifier (without namespace).
            obj: Any JSON-serializable object (dict, list, str, int, etc.).

        Returns:
            bool: True if the operation was successful.
        """

        name_obj = f"{self.app_name}.{key}"
        obj_json = json.dumps(obj, default=self._set_default)

        return await self.storage.set(name_obj, obj_json)

    async def get(self, key: str) -> Any:
        """
        Retrieves and deserializes an object by its key.

        Args:
            key: The key identifier to look up.

        Returns:
            object: The deserialized Python object.

        Raises:
            KeyError: If the key does not exist in the storage.
            ValueError: If the stored data is not valid JSON.
        """
        obj_json = await self.storage.get(f"{self.app_name}.{key}")

        if obj_json is None:
            raise KeyError(f"Key '{key}' not found in '{self.app_name}' namespace")

        try:
            return json.loads(obj_json, object_hook=self._object_hook)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON for key '{key}': {e}")

    async def get_or_default(self, key: str, default: Any = None) -> Any:
        """
        Gets the value for the given key or returns a default value if not found.

        Args:
            key: The key identifier to look up.
            default: The value to return if the key does not exist. Defaults to None.

        Returns:
            Any: The deserialized object if found, otherwise the default value.

        Raises:
            ValueError: If the stored data is not valid JSON.
        """
        try:
            return await self.get(key)
        except KeyError:
            return default

    async def contains_key(self, key: str) -> bool:
        """
        Checks if a specific key exists within the application namespace.

        Args:
            key: The key identifier to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return await self.storage.contains_key(f"{self.app_name}.{key}")

    async def remove(self, key: str) -> bool:
        """
        Removes a specific key and its value from the storage.

        Args:
            key: The key identifier to remove.

        Returns:
            bool: True if the operation was successful.
        """
        return await self.storage.remove(f"{self.app_name}.{key}")

    async def get_keys(self) -> list[str]:
        """
        Retrieves all keys belonging to the current application namespace.

        Returns:
            list[str]: A list of keys with the 'app_name.' prefix removed.
        """
        data = await self.storage.get_keys(self.app_name)

        if not data:
            return []

        prefix = f"{self.app_name}."

        return [item.removeprefix(prefix) for item in data]

    async def clear(self) -> None:
        """
        Deletes all keys and values associated with the current application namespace.
        Other namespaces in SharedPreferences remain untouched.
        """
        keys = await self.get_keys()
        await asyncio.gather(*[self.remove(key) for key in keys])
