import importlib

# Map internal plugin names to display names
PLUGIN_NAME_MAP = {
    "github": "GitHub",
    "reddit": "Reddit",
    "x": "X (formerly Twitter)",
    "linkedin": "LinkedIn",
}


def load_plugins(plugin_names):
    """
    Dynamically load plugins by name.

    Args:
        plugin_names (list[str]): Plugin module names

    Returns:
        list[module]: Loaded plugin modules
    """
    plugins = []

    for name in plugin_names:
        module_path = f"git_identity_leak.plugins.{name}"
        try:
            module = importlib.import_module(module_path)
            plugins.append(module)
        except ModuleNotFoundError:
            display = PLUGIN_NAME_MAP.get(name, name)
            print(f"[!] Plugin {display} not found. Skipping.")
        except Exception as e:
            display = PLUGIN_NAME_MAP.get(name, name)
            print(f"[!] Error loading plugin {display}: {e}")

    return plugins
