# Flet Storage

> 🌐 **Translations:** [🇺🇦 Українська](README.uk.md)

A lightweight, asynchronous, namespaced storage utility...

A lightweight, asynchronous, namespaced storage utility for [Flet](https://flet.dev) applications.

`FletStorage` is a powerful wrapper around Flet's built-in `SharedPreferences`. It simplifies client-side data persistence by adding automatic JSON serialization, allowing you to store and retrieve complex Python objects without manual conversion, while keeping your data organized and isolated.

## Features

- Automatic JSON serialization: store and retrieve `dict`, `list`, `int`, `bool`, and `str` directly.
- Namespaced storage: automatically prefixes keys with `app_name` to prevent data collisions between different applications on the same device.
- Asynchronous and parallel: fully asynchronous API with parallel deletion in the `clear()` method for maximum performance.
- Robust error handling: clear `KeyError` and `ValueError` exceptions for predictable data management.

## Installation
```bash
pip install flet-storage
```

## Quick Start
```python
import flet as ft
from flet_storage import FletStorage


async def main(page: ft.Page):
    # Initialize storage with a unique namespace
    storage = FletStorage("my_app")

    # Save data
    await storage.set("user", {"name": "Ivan", "age": 25})
    await storage.set("settings", {"theme": "dark", "language": "en"})

    # Retrieve data
    user = await storage.get("user")
    print(user)  # {'name': 'Ivan', 'age': 25}

    # Get with default value
    config = await storage.get_or_default("config", {"version": "1.0"})
    print(config)  # {'version': '1.0'}

    # Check if key exists
    exists = await storage.contains_key("user")
    print(exists)  # True

    # Get all keys
    keys = await storage.get_keys()
    print(keys)  # ['user', 'settings']

    # Remove a key
    await storage.remove("settings")

    # Clear entire storage
    await storage.clear()

ft.run(main)
```

## API Reference

### `__init__(app_name: str)`

Initializes the storage with a unique namespace.

**Parameters:**
- `app_name` (str): The unique namespace for the application.

**Example:**
```python
storage = FletStorage("todo_app")
```

---

### `async set(key: str, obj: object) -> bool`

Serializes an object to JSON and stores it under a namespaced key.

**Parameters:**
- `key` (str): The unique key identifier (without namespace).
- `obj` (object): Any JSON-serializable object (dict, list, str, int, etc.).

**Returns:**
- `bool`: `True` if the operation was successful.

**Example:**
```python
await storage.set("preferences", {"notifications": True})
```

---

### `async get(key: str) -> Any`

Retrieves and deserializes an object by its key.

**Parameters:**
- `key` (str): The key identifier to look up.

**Returns:**
- `Any`: The deserialized Python object.

**Raises:**
- `KeyError`: If the key does not exist in the storage.
- `ValueError`: If the stored data is not valid JSON.

**Example:**
```python
try:
    data = await storage.get("preferences")
except KeyError:
    print("Key not found")
```

---

### `async get_or_default(key: str, default: Any = None) -> Any`

Gets the value for the given key or returns a default value if not found.

**Parameters:**
- `key` (str): The key identifier to look up.
- `default` (Any): The value to return if the key does not exist. Defaults to `None`.

**Returns:**
- `Any`: The deserialized object if found, otherwise the default value.

**Raises:**
- `ValueError`: If the stored data is not valid JSON.

**Example:**
```python
config = await storage.get_or_default("config", {"version": "1.0"})
```

---

### `async contains_key(key: str) -> bool`

Checks if a specific key exists within the application namespace.

**Parameters:**
- `key` (str): The key identifier to check.

**Returns:**
- `bool`: `True` if the key exists, `False` otherwise.

**Example:**
```python
if await storage.contains_key("user_token"):
    token = await storage.get("user_token")
```

---

### `async remove(key: str) -> bool`

Removes a specific key and its value from the storage.

**Parameters:**
- `key` (str): The key identifier to remove.

**Returns:**
- `bool`: `True` if the operation was successful.

**Example:**
```python
await storage.remove("temp_data")
```

---

### `async get_keys() -> list[str]`

Retrieves all keys belonging to the current application namespace.

**Returns:**
- `list[str]`: A list of keys with the `app_name.` prefix removed.

**Example:**
```python
all_keys = await storage.get_keys()
print(f"Stored {len(all_keys)} keys")
```

---

### `async clear() -> None`

Deletes all keys and values associated with the current application namespace. Other namespaces in `SharedPreferences` remain untouched.

**Example:**
```python
await storage.clear()  # Removes all app data
```

---

## Usage Examples

### Saving User Settings
```python
async def save_user_settings(storage: FletStorage, settings: dict):
    await storage.set("settings", settings)
    print("Settings saved")

async def load_user_settings(storage: FletStorage) -> dict:
    return await storage.get_or_default("settings", {
        "theme": "light",
        "language": "en",
        "notifications": True
    })
```

### Managing a Todo List
```python
async def add_todo(storage: FletStorage, task: str):
    todos = await storage.get_or_default("todos", [])
    todos.append({"task": task, "completed": False})
    await storage.set("todos", todos)

async def get_all_todos(storage: FletStorage) -> list:
    return await storage.get_or_default("todos", [])

async def clear_completed_todos(storage: FletStorage):
    todos = await storage.get_or_default("todos", [])
    active_todos = [t for t in todos if not t["completed"]]
    await storage.set("todos", active_todos)
```

### Data Caching
```python
import time

async def cache_data(storage: FletStorage, key: str, data: Any, ttl: int = 3600):
    cache_entry = {
        "data": data,
        "expires_at": time.time() + ttl
    }
    await storage.set(f"cache_{key}", cache_entry)

async def get_cached_data(storage: FletStorage, key: str) -> Any | None:
    try:
        cache_entry = await storage.get(f"cache_{key}")
        if time.time() < cache_entry["expires_at"]:
            return cache_entry["data"]
        else:
            await storage.remove(f"cache_{key}")
            return None
    except KeyError:
        return None
```

## Error Handling
```python
async def safe_get_data(storage: FletStorage, key: str):
    try:
        data = await storage.get(key)
        return data
    except KeyError:
        print(f"Key '{key}' not found")
        return None
    except ValueError as e:
        print(f"JSON error: {e}")
        return None
```

## Best Practices

1. **Use descriptive namespace names:** Choose a unique `app_name` to avoid conflicts with other applications.

2. **Handle exceptions:** Always handle `KeyError` and `ValueError` when working with `get()`.

3. **Use `get_or_default()`:** For optional data, this is more convenient than exception handling.

4. **Structure your data:** Store related data together in dictionaries for better organization.

5. **Clean up stale data:** Regularly remove unnecessary keys to keep storage clean.

## Requirements

- Python 3.12+
- Flet >= 0.80.1

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests on [GitHub](https://github.com/BogdanovychA/flet-storage).

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub](https://github.com/BogdanovychA/flet-storage/issues)

---

**Made with ❤️ for the Flet community**