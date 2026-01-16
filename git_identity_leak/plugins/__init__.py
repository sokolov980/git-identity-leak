import importlib

PLUGIN_MODULES = {
    "GitHub": "git_identity_leak.plugins.github",
    "Reddit": "git_identity_leak.plugins.reddit",
    "X (formerly Twitter)": "git_identity_leak.plugins.x",
    "LinkedIn": "git_identity_leak.plugins.linkedin",
}


def load_plugins():
    plugins = []

    for name, module_path in PLUGIN_MODULES.items():
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, "collect"):
                plugins.append(module)
            else:
                print(f"[!] Plugin {name} missing collect() function. Skipping.")
        except Exception:
            print(f"[!] Plugin {name} not found. Skipping.")

    return plugins
