import os
import platform
import subprocess
import os.path as path

def _get_nt_settings_path(appdata):
  return path.join(appdata, "Code/User/settings.json")

def get_global_settings_path():
  pf = platform.system()
  if pf == "Windows":
    return _get_nt_settings_path(os.getenv("APPDATA"))
  elif pf == "Darwin":
    return path.expanduser("~/Library/Application Support/Code/User/settings.json")
  elif pf == "Linux":
    if "WSLENV" in os.environ:
      # assume using the Windows side of VSCode
      appdata_win = subprocess.check_output(["cmd.exe", "/c", "echo", "%APPDATA%"]).decode().strip()
      appdata = subprocess.check_output(["wslpath", "-u", appdata_win]).decode().strip()
      return _get_nt_settings_path(appdata)
    else:
      return path.expanduser("~/.config/Code/User/settings.json")
  raise Exception("unknown architecture")

def _get_snap_which():
  import os
import subprocess

def _get_snap_vscode_installed_path():
  try:
    result = subprocess.run(["snap", "list", "code"], capture_output=True, text=True, check=True)
    lines = result.stdout.strip().splitlines()
    if len(lines) < 2:
      raise RuntimeError("VSCode (code) is not listed in snap")

    parts = lines[1].split()
    if len(parts) < 3:
      raise RuntimeError("Unexpected format from 'snap list code'")

    revision = parts[2]
    snap_base = f"/snap/code/{revision}/usr/share/code"

    if os.path.exists(snap_base):
      print(snap_base)
      return snap_base
    else:
      raise FileNotFoundError(f"Path does not exist: {snap_base}")

  except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Failed to run 'snap list code': {e}")
  except Exception as e:
    raise RuntimeError(f"Error while finding VSCode resource path: {e}")

def get_vscode_installed_path():
  pf = platform.system()
  code_path = None
  if pf == "Windows":
    code_path = subprocess.check_output(["cmd.exe", "/c", "which", "code"]).decode().strip()
  if pf == "Darwin":
    code_path = subprocess.check_output(["which", "code"]).decode().strip()
  if pf == "Linux":
    # WSL
    if "WSLENV" in os.environ:
      # assume using the Windows side of VSCode
      code_path_win = subprocess.check_output(["cmd.exe", "/c", "which", "code"]).decode().strip()
      code_path = subprocess.check_output(["wslpath", "-u", code_path_win]).decode().strip()
    else:
      code_path = subprocess.check_output(["which", "code"]).decode().strip()
      if code_path.startswith("/snap/"):
        return _get_snap_vscode_installed_path()

  if code_path == None:
    raise Exception("unknown architecture")
  if path.islink(code_path):
      code_path = os.readlink(code_path)
  return path.dirname(path.dirname(code_path))

def get_vscode_extension_paths():
  if "WSLENV" in os.environ:
    # assume using the Windows side of VSCode
    home_path_win = subprocess.check_output(["cmd.exe", "/c", "%USERPROFILE%"]).decode().strip()
    home_path = subprocess.check_output(["wslpath", "-u", home_path_win]).decode().strip()
    return path.join(home_path, ".vscode/extensions")
  return path.expanduser("~/.vscode/extensions")
