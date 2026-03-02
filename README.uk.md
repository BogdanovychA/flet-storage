# Flet Storage

> 🌐 **Переклади:** [🇬🇧 English](https://github.com/BogdanovychA/flet-storage/blob/main/README.md)

Легка, асинхронна бібліотека для роботи зі сховищем із підтримкою простору імен для застосунків [Flet](https://flet.dev).

`FletStorage` — це потужна обгортка навколо вбудованого `SharedPreferences` у Flet. Вона спрощує збереження даних на стороні клієнта, додаючи автоматичну серіалізацію JSON, що дозволяє зберігати та отримувати складні об'єкти Python без ручного перетворення, тримаючи при цьому ваші дані організованими та ізольованими.

У цьому репозиторії також є skill для агентів. Дивіться файл [skill](https://github.com/BogdanovychA/flet-storage/blob/main/.agents/skills/flet-storage/SKILL.md).

## Особливості

- **Автоматична серіалізація JSON:** Зберігайте та отримуйте `dict`, `list`, `int`, `bool`, `str` та `set` безпосередньо без ручного перетворення.
- **Простір імен:** Автоматично додає префікс `app_name` до ключів для запобігання конфліктів даних між різними застосунками на одному пристрої.
- **Асинхронність і паралелізм:** Повністю асинхронний API з паралельним видаленням у методі `clear()` для максимальної продуктивності.
- **Надійна обробка помилок:** Чіткі винятки `KeyError` та `ValueError` для передбачуваного управління даними.
- **Підтримка set:** Множини Python автоматично зберігаються під час серіалізації та десеріалізації.

## Встановлення
```bash
pip install flet-storage
```

## Швидкий старт
```python
import flet as ft
from flet_storage import FletStorage


async def main(page: ft.Page):
    # Ініціалізація сховища з унікальним простором імен
    storage = FletStorage("my_app")

    # Збереження даних
    await storage.set("user", {"name": "Іван", "age": 25})
    await storage.set("settings", {"theme": "dark", "language": "uk"})

    # Отримання даних
    user = await storage.get("user")
    print(user)  # {'name': 'Іван', 'age': 25}

    # Отримання із значенням за замовчуванням
    config = await storage.get_or_default("config", {"version": "1.0"})
    print(config)  # {'version': '1.0'}

    # Перевірка наявності ключа
    exists = await storage.contains_key("user")
    print(exists)  # True

    # Отримання всіх ключів
    keys = await storage.get_keys()
    print(keys)  # ['user', 'settings']

    # Видалення ключа
    await storage.remove("settings")

    # Очищення всього сховища
    await storage.clear()

ft.run(main)
```

## Підтримувані типи даних

FletStorage автоматично серіалізує та десеріалізує наступні типи Python:

| Тип | Опис | Приклад |
|------|------|---------|
| `dict` | Словники | `{"ключ": "значення"}` |
| `list` | Списки | `[1, 2, 3]` |
| `set` | Множини (зберігаються) | `{"a", "b", "c"}` |
| `str` | Рядки | `"привіт"` |
| `int`, `float` | Числа | `42`, `3.14` |
| `bool` | Булеві значення | `True`, `False` |
| `None` | Значення None | `None` |

### Робота з множинами (set)

Множини автоматично зберігаються під час збереження та отримання:
```python
# Збереження множини
tags = {"python", "flet", "async"}
await storage.set("tags", tags)

# Отримання (повертає множину, а не список!)
tags = await storage.get("tags")
print(type(tags))  # <class 'set'> ✅
print(tags)  # {'python', 'flet', 'async'}

# Множини у вкладених структурах теж працюють
data = {
    "user": "Іван",
    "tags": {"web", "mobile"},
    "categories": ["tech", "programming"]
}
await storage.set("profile", data)
profile = await storage.get("profile")
# profile["tags"] є множиною ✅
# profile["categories"] є списком ✅
```

**Технічна примітка:** Множини зберігаються внутрішньо як `{"__type__": "set", "values": [...]}`. Якщо вам потрібно зберегти словник з ключем `"__type__"`, що дорівнює `"set"`, він може бути неправильно інтерпретований як маркер множини під час десеріалізації.

## API Довідник

### `__init__(app_name: str)`

Ініціалізує сховище з унікальним простором імен.

**Параметри:**
- `app_name` (str): Унікальний простір імен для застосунку.

**Приклад:**
```python
storage = FletStorage("todo_app")
```

---

### `async set(key: str, obj: object) -> bool`

Серіалізує об'єкт у JSON та зберігає його під ключем із простором імен.

**Параметри:**
- `key` (str): Унікальний ідентифікатор ключа (без простору імен).
- `obj` (object): Будь-який об'єкт, що серіалізується в JSON (dict, list, set, str, int тощо).

**Повертає:**
- `bool`: `True`, якщо операція успішна.

**Приклад:**
```python
await storage.set("preferences", {"notifications": True})
await storage.set("tags", {"python", "flet"})  # Множини підтримуються!
```

---

### `async get(key: str) -> Any`

Отримує та десеріалізує об'єкт за його ключем.

**Параметри:**
- `key` (str): Ідентифікатор ключа для пошуку.

**Повертає:**
- `Any`: Десеріалізований об'єкт Python.

**Викидає:**
- `KeyError`: Якщо ключ не існує у сховищі.
- `ValueError`: Якщо збережені дані не є валідним JSON.

**Приклад:**
```python
try:
    data = await storage.get("preferences")
except KeyError:
    print("Ключ не знайдено")
```

---

### `async get_or_default(key: str, default: Any = None) -> Any`

Отримує значення для вказаного ключа або повертає значення за замовчуванням, якщо ключ не знайдено.

**Параметри:**
- `key` (str): Ідентифікатор ключа для пошуку.
- `default` (Any): Значення, що повертається, якщо ключ не існує. За замовчуванням `None`.

**Повертає:**
- `Any`: Десеріалізований об'єкт, якщо знайдено, інакше значення за замовчуванням.

**Викидає:**
- `ValueError`: Якщо збережені дані не є валідним JSON.

**Приклад:**
```python
config = await storage.get_or_default("config", {"version": "1.0"})
```

---

### `async contains_key(key: str) -> bool`

Перевіряє, чи існує певний ключ у просторі імен застосунку.

**Параметри:**
- `key` (str): Ідентифікатор ключа для перевірки.

**Повертає:**
- `bool`: `True`, якщо ключ існує, інакше `False`.

**Приклад:**
```python
if await storage.contains_key("user_token"):
    token = await storage.get("user_token")
```

---

### `async remove(key: str) -> bool`

Видаляє певний ключ та його значення зі сховища.

**Параметри:**
- `key` (str): Ідентифікатор ключа для видалення.

**Повертає:**
- `bool`: `True`, якщо операція успішна.

**Приклад:**
```python
await storage.remove("temp_data")
```

---

### `async get_keys() -> list[str]`

Отримує всі ключі, що належать до поточного простору імен застосунку.

**Повертає:**
- `list[str]`: Список ключів із видаленим префіксом `app_name.`.

**Приклад:**
```python
all_keys = await storage.get_keys()
print(f"Збережено {len(all_keys)} ключів")
```

---

### `async clear() -> None`

Видаляє всі ключі та значення, пов'язані з поточним простором імен застосунку. Інші простори імен у `SharedPreferences` залишаються недоторканими.

**Приклад:**
```python
await storage.clear()  # Видаляє всі дані застосунку
```

---

## Приклади використання

### Збереження налаштувань користувача
```python
async def save_user_settings(storage: FletStorage, settings: dict):
    await storage.set("settings", settings)
    print("Налаштування збережено")

async def load_user_settings(storage: FletStorage) -> dict:
    return await storage.get_or_default("settings", {
        "theme": "light",
        "language": "uk",
        "notifications": True
    })
```

### Управління списком завдань
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

### Робота з тегами (множинами)
```python
async def add_tag(storage: FletStorage, tag: str):
    tags = await storage.get_or_default("tags", set())
    tags.add(tag)
    await storage.set("tags", tags)

async def remove_tag(storage: FletStorage, tag: str):
    tags = await storage.get_or_default("tags", set())
    tags.discard(tag)
    await storage.set("tags", tags)

async def get_all_tags(storage: FletStorage) -> set:
    return await storage.get_or_default("tags", set())
```

### Кешування даних
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

## Обробка помилок
```python
async def safe_get_data(storage: FletStorage, key: str):
    try:
        data = await storage.get(key)
        return data
    except KeyError:
        print(f"Ключ '{key}' не знайдено")
        return None
    except ValueError as e:
        print(f"Помилка JSON: {e}")
        return None
```

## Найкращі практики

1. **Використовуйте описові назви просторів імен:** Виберіть унікальний `app_name`, щоб уникнути конфліктів із іншими застосунками.

2. **Обробляйте винятки:** Завжди обробляйте `KeyError` та `ValueError` при роботі з `get()`.

3. **Використовуйте `get_or_default()`:** Для необов'язкових даних це зручніше, ніж обробка винятків.

4. **Структуруйте дані:** Зберігайте пов'язані дані разом у словниках для кращої організації.

5. **Очищайте застарілі дані:** Регулярно видаляйте непотрібні ключі, щоб зберегти сховище чистим.

6. **Використовуйте множини для унікальних колекцій:** Множини автоматично зберігаються і ідеально підходять для зберігання унікальних елементів, таких як теги або категорії.

## Вимоги

- Python 3.10+
- Flet >= 0.81.0

## Ліцензія

MIT License

## Внесок

Внески вітаються! Будь ласка, надсилайте pull request на [GitHub](https://github.com/BogdanovychA/flet-storage).

## Підтримка

Якщо у вас виникли проблеми або запитання:
- Відкрийте issue на [GitHub](https://github.com/BogdanovychA/flet-storage/issues)

---

**Зроблено з ❤️ для спільноти Flet**