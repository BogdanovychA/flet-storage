# Flet Storage

A lightweight, asynchronous utility for simplified client-side storage management in [Flet](https://flet.dev) applications.

This package provides a clean wrapper around Flet's `SharedPreferences`, adding automatic JSON serialization so you can store complex Python objects (dicts, lists) without manual conversion.

## Features

- **Automatic JSON Serialization:** Store and retrieve dictionaries and lists directly.
- **Asynchronous API:** Built to work seamlessly with Flet's async architecture.
- **Namespaced Storage:** Easily organize data by `app_name` to avoid collisions.
- **Simplified Syntax:** Clean, functional approach to persistent data.

## Installation

```bash
pip install flet-storage