# src/flyshell/startup/plugin_env.py

from pathlib import Path
from flyshell import constants as c
from flyshell import data


def _resolve_plugin_dir_name(target_name: str) -> tuple[str, object | None]:
    target_lower = target_name.strip().lower()
    if hasattr(c, "PLUGINS"):
        if target_lower in c.PLUGINS:
            plugin = c.PLUGINS[target_lower]
            dir_name = plugin.context.get("plugin_dir_name") or target_lower
            dir_name = (
                Path(dir_name).stem
                if "\\" in str(dir_name) or "/" in str(dir_name)
                else str(dir_name)
            )
            return (dir_name, plugin)
        for cmd_name, plugin in c.PLUGINS.items():
            p_display = getattr(plugin, "name", "").lower()
            p_dir = str(plugin.context.get("plugin_dir_name", "")).lower()
            p_dir_clean = Path(p_dir).stem
            if target_lower in (cmd_name.lower(), p_display, p_dir, p_dir_clean):
                resolved_dir = plugin.context.get("plugin_dir_name") or cmd_name
                resolved_dir = (
                    Path(resolved_dir).stem
                    if "\\" in str(resolved_dir) or "/" in str(resolved_dir)
                    else str(resolved_dir)
                )
                return (resolved_dir, plugin)
    return (target_name.strip(), None)


def get_plugin_api_keys(plugin_name_or_dir: str) -> dict[str, str]:
    all_env = data.read_env_file()
    dir_name, _ = _resolve_plugin_dir_name(plugin_name_or_dir)
    prefixes = {
        f"{dir_name.lower()}_",
        f"{plugin_name_or_dir.strip().lower()}_",
    }
    other_prefixes = set()
    if hasattr(c, "PLUGINS"):
        for cmd_name, plugin in c.PLUGINS.items():
            other_dir = str(plugin.context.get("plugin_dir_name") or cmd_name).lower()
            for candidate in (f"{other_dir}_", f"{cmd_name.lower()}_"):
                if candidate not in prefixes:
                    other_prefixes.add(candidate)
    plugin_keys = {}
    for raw_k, val in all_env.items():
        k_lower = raw_k.lower()
        for prefix in prefixes:
            if k_lower.startswith(prefix):
                if any(
                    len(other) > len(prefix) and k_lower.startswith(other)
                    for other in other_prefixes
                ):
                    break
                key_name = raw_k[len(prefix) :]
                plugin_keys[key_name] = val
                break
    return plugin_keys


def get_all_keys() -> tuple[int, str]:
    env_path = data.get_env_path()
    if not env_path.exists():
        return (1, f"File Config Error: Environment file not found at '{env_path}'")
    try:
        all_env = data.read_env_file()
        if not all_env:
            return (0, "No API keys configured.")
        lines = ["Configured API keys:"]
        for k, v in sorted(all_env.items()):
            lines.append(f"{k} = {v}")
        return (0, "\n".join(lines))
    except Exception as e:
        return (1, f"File Error: An unknown error occurred: {e}")


def get_plugin_keys_formatted(target_name: str) -> tuple[int, str]:
    if not target_name or not isinstance(target_name, str):
        return (1, "Command Error: A valid plugin name must be provided.")
    env_path = data.get_env_path()
    if not env_path.exists():
        return (1, f"File Config Error: Environment file not found at '{env_path}'")
    dir_name, plugin = _resolve_plugin_dir_name(target_name)
    configured_keys = get_plugin_api_keys(target_name)
    required_keys = (getattr(plugin, "api_keys", None) or []) if plugin else []
    if not configured_keys and not required_keys:
        return (0, f"No API keys found or required for plugin '{target_name}'.")
    lines = [f"API Keys for plugin '{target_name}' (folder: '{dir_name}'):"]
    lower_configured = {k.lower(): (k, v) for k, v in configured_keys.items()}
    seen_keys = set()
    for req in required_keys:
        req_lower = req.lower()
        seen_keys.add(req_lower)
        if req_lower in lower_configured:
            orig_k, val = lower_configured[req_lower]
            lines.append(f"{orig_k} = {val} [Required]")
        else:
            lines.append(f"{req} = [MISSING / NOT SET] [Required]")
    for k_lower, (orig_k, val) in sorted(lower_configured.items()):
        if k_lower not in seen_keys:
            lines.append(f"{orig_k} = {val} [Optional/Extra]")
    return (0, "\n".join(lines))


def set_plugin_api_key(plugin_name: str, key_name: str, value: str) -> tuple[int, str]:
    if not plugin_name or not key_name:
        return (1, "Command Error: Both plugin name and key name are required.")
    dir_name, _ = _resolve_plugin_dir_name(plugin_name)
    target_key = f"{dir_name.strip().lower()}_{key_name.strip().upper()}"
    ok, info = data.set_env_entry(target_key, value)
    if not ok:
        return (1, info)
    return (0, f"SUCCESS! {info} key '{target_key}'")


def remove_plugin_api_key(plugin_name: str, key_name: str) -> tuple[int, str]:
    if not plugin_name or not key_name:
        return (1, "Command Error: Both plugin name and key name are required.")
    dir_name, _ = _resolve_plugin_dir_name(plugin_name)
    target_key = f"{dir_name.strip().lower()}_{key_name.strip().upper()}"
    ok, info = data.delete_env_entry(target_key)
    if not ok:
        return (1, info)
    return (0, f"SUCCESS! Removed key '{target_key}' from Flyshell environment.")
