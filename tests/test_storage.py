import json
from unittest.mock import AsyncMock, MagicMock

import flet as ft
import pytest

from flet_storage import FletStorage


@pytest.fixture
def mock_storage():
    """Fixture to mock ft.SharedPreferences."""
    mock = MagicMock(spec=ft.SharedPreferences)
    mock.set = AsyncMock(return_value=True)
    mock.get = AsyncMock()
    mock.contains_key = AsyncMock(return_value=True)
    mock.remove = AsyncMock(return_value=True)
    mock.get_keys = AsyncMock(return_value=[])
    return mock


@pytest.mark.asyncio
async def test_storage_set(mock_storage, monkeypatch):
    # Patch ft.SharedPreferences to return our mock
    monkeypatch.setattr(ft, "SharedPreferences", lambda: mock_storage)

    storage = FletStorage(app_name="test_app")

    # Test setting a simple string
    await storage.set("key1", "value1")
    mock_storage.set.assert_called_with("test_app.key1", '"value1"')

    # Test setting a dictionary
    await storage.set("key2", {"a": 1})
    mock_storage.set.assert_called_with("test_app.key2", '{"a": 1}')

    # Test setting a set (should be handled by _set_default)
    await storage.set("key3", {1, 2})
    # The order of elements in set might vary, so we check for the structure
    call_args = mock_storage.set.call_args
    assert call_args[0][0] == "test_app.key3"
    data = json.loads(call_args[0][1])
    assert data["__type__"] == "set"
    assert set(data["values"]) == {1, 2}


@pytest.mark.asyncio
async def test_storage_get(mock_storage, monkeypatch):
    monkeypatch.setattr(ft, "SharedPreferences", lambda: mock_storage)
    storage = FletStorage(app_name="test_app")

    # Mocking string return
    mock_storage.get.return_value = '"value1"'
    assert await storage.get("key1") == "value1"

    # Mocking dict return
    mock_storage.get.return_value = '{"a": 1}'
    assert await storage.get("key2") == {"a": 1}

    # Mocking set return (using the special format)
    mock_storage.get.return_value = '{"__type__": "set", "values": [1, 2]}'
    result = await storage.get("key3")
    assert isinstance(result, set)
    assert result == {1, 2}

    # Mocking key not found
    mock_storage.get.return_value = None
    with pytest.raises(KeyError):
        await storage.get("nonexistent")


@pytest.mark.asyncio
async def test_get_or_default(mock_storage, monkeypatch):
    monkeypatch.setattr(ft, "SharedPreferences", lambda: mock_storage)
    storage = FletStorage(app_name="test_app")

    # Key exists
    mock_storage.get.return_value = '"exists"'
    assert await storage.get_or_default("key", "default") == "exists"

    # Key doesn't exist
    mock_storage.get.return_value = None
    assert await storage.get_or_default("missing", "default") == "default"


@pytest.mark.asyncio
async def test_contains_key(mock_storage, monkeypatch):
    monkeypatch.setattr(ft, "SharedPreferences", lambda: mock_storage)
    storage = FletStorage(app_name="test_app")

    mock_storage.contains_key.return_value = True
    assert await storage.contains_key("key") is True
    mock_storage.contains_key.assert_called_with("test_app.key")

    mock_storage.contains_key.return_value = False
    assert await storage.contains_key("missing") is False


@pytest.mark.asyncio
async def test_remove(mock_storage, monkeypatch):
    monkeypatch.setattr(ft, "SharedPreferences", lambda: mock_storage)
    storage = FletStorage(app_name="test_app")

    await storage.remove("key")
    mock_storage.remove.assert_called_with("test_app.key")


@pytest.mark.asyncio
async def test_get_keys(mock_storage, monkeypatch):
    monkeypatch.setattr(ft, "SharedPreferences", lambda: mock_storage)
    storage = FletStorage(app_name="test_app")

    mock_storage.get_keys.return_value = ["test_app.k1", "test_app.k2", "other_app.k3"]
    keys = await storage.get_keys()
    assert keys == ["k1", "k2"]
    mock_storage.get_keys.assert_called_with("test_app")


@pytest.mark.asyncio
async def test_clear(mock_storage, monkeypatch):
    monkeypatch.setattr(ft, "SharedPreferences", lambda: mock_storage)
    storage = FletStorage(app_name="test_app")

    # Setup get_keys to return some keys
    mock_storage.get_keys.return_value = ["test_app.k1", "test_app.k2"]

    await storage.clear()

    # Should call remove for each key
    assert mock_storage.remove.call_count == 2
    mock_storage.remove.assert_any_call("test_app.k1")
    mock_storage.remove.assert_any_call("test_app.k2")
