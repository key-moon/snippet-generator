from argparse import ArgumentParser
import json
from pathlib import Path
from typing import Any, Mapping, Tuple, Type
from snippet_generator.loader.loader import Loader
from snippet_generator.loader.sourceloader import SourceLoader
from snippet_generator.target.target import SnippetTargetBase
from snippet_generator.target.vscode import VSCodeSnippet

# TODO: config 系を切り出す(マージ / Union[str, list[str]] to list[str] 等)

LOADERS: Mapping[str, Tuple[Type[Loader], Mapping[str, Any]]] = {
  "default": (SourceLoader, {
    "header-separator": ":? +",
    "header-signature": "HEADER",
    "variables-separator": ":? +",
    "variables-signature": "VARIABLES",
    "body-signature": "BODY",
  })
}

SNIPPET_TARGETS: Mapping[str, Tuple[Type[SnippetTargetBase], Mapping[str, Any]]] = {
  "vscode": (VSCodeSnippet, {
    "snippet-keys": {
      "name": "name",
      "prefix": "prefix",
      "description": "description",
      "isFileTemplate": "template",
      "language": "language"
    },
    "package": {
      "name": "snippet",
      "version": "0.0.1",
      "publisher": "",
      "engines": "^1.0.0"
    }
  })
}

def main():
  parser = ArgumentParser()
  parser.add_argument("directory")
  parser.add_argument("destination")
  parser.add_argument("--config", default=None)
  parser.add_argument("--target", nargs="*", default=None)

  res = parser.parse_args()

  srcdir = Path(res.directory)

  config_path = srcdir / "config.json" if res.config is None else res.config
  with open(config_path, "r") as f:
    config = json.load(f)

  if not isinstance(config, dict):
    raise TypeError("config") 
  
  loader_config = config.get("loader", {})
  if not isinstance(loader_config, dict):
    raise TypeError("config.loader")

  loader_name = "default"
  loader_class, default_config = LOADERS[loader_name]
  loader = loader_class({**default_config, **loader_config})

  snippets = {}
  for file in srcdir.rglob("*"):
    if file == config_path: continue
    if not file.is_file():
      continue
    print(file)
    snippet = loader.load(file)
    if "name" not in snippet.header and "title" not in snippet.header:
      print(f"[!] invalid snippet src file: {file}")
      continue
    snippets[file] = snippet
    continue

  targets_config = config.get("targets", {})
  if not isinstance(targets_config, dict):
    raise TypeError("config.targets")
  targets = res.target if res.target is not None else targets_config.keys()
  for target_name in targets:
    if target_name not in SNIPPET_TARGETS:
      raise KeyError("target does not exists", target_name)
  
  for target_name in targets_config:
    target_class, default_config = SNIPPET_TARGETS[target_name]
    target = target_class({**default_config, **targets_config.get(target_name, {})})
    target.dumps(snippets, res.destination)
