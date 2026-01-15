# plugins/__init__.py

import importlib

# Map internal plugin names to friendly display names for warnings
PLUGIN_NAME_MAP = {
    "reddit": "Reddit",
    "x": "X (formerly Twitter)",
    "linkedin": "LinkedIn",
    "github": "GitHub"
}

def load_plugins(plugin_list):
    """
    Dynamically load plugins by name.
    Prints a friendly warning if missing but does not crash.
    """
    plugins = []
    for plugin_name in plugin_list:
        module_path = f"plugins.{plugin_name}"
        try:
            module = importlib.import_module(module_path)
            plugins.append(module)
        except ModuleNotFoundError:
            display_name = PLUGIN_NAME_MAP.get(plugin_name, plugin_name)
            print(f"[!] Plugin {display_name} not found. Skipping.")
        except Exception as e:
            display_name = PLUGIN_NAME_MAP.get(plugin_name, plugin_name)
            print(f"[!] Error loading plugin {display_name}: {e}")
    return plugins
