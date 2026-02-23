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
    def _set_default(_obj):
        """
        JSON serializer helper that handles 'set' objects.

        Converts sets to lists to ensure JSON compatibility. If the object
        is not a set, raises TypeError to allow the default encoder to
        handle other types or fail.
        """

        if isinstance(_obj, set):
            return list(_obj)
        raise TypeError

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
            return json.loads(obj_json)
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
