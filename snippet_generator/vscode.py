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
