# Plugin loader: will not crash if plugins are missing

from pathlib import Path
import importlib

def load_plugins(plugin_list):
    plugins = []
    for plugin_name in plugin_list:
        module_path = f"git_identity_leak.plugins.{plugin_name}"
        try:
            module = importlib.import_module(module_path)
            plugins.append(module)
        except ModuleNotFoundError:
            print(f"[!] Plugin {plugin_name} not found. Skipping.")
        except Exception as e:
            print(f"[!] Error loading plugin {plugin_name}: {e}")
    return plugins
