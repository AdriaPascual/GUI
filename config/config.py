from importlib import resources
import json
from logging import exception

class Config:

    config_json_path, config_json_filename = "config", "config.json"

    __instance = None
    debug = False

    @staticmethod
    def instance():
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        if Config.__instance is None:
            Config.__instance = self

            with resources.path(Config.config_json_path, Config.config_json_filename) as config_path:
                with open(config_path) as f:
                    self.data = json.load(f)
        else:
            raise exception("Config cannot have multiple instances")


def cfg_item(*items):
  d = Config.instance().data
  for k in items:
    d = d[k]
  return d