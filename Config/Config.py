import copy
import json
from dotenv import dotenv_values

secrets = {}
def load_env(production: bool):
    global secrets
    env_file = ".env.production" if production else ".env.development"
    secrets = dotenv_values(env_file)

class PyJSON():

    def __init__(self, json: dict = None, exclude=[]):
        if json is not None:
            for k, v in json.items():
                if k not in exclude:
                    if isinstance(v, dict):
                        self.__dict__[k] = PyJSON(v)
                    else:
                        if isinstance(v, str) and "$" in v:
                            v = secrets[v.replace("$", "")]
                        self.__dict__[k] = v

    def to_json(self):
        d = copy.deepcopy(self).__dict__
        for k, v in d.items():
            if isinstance(v, PyJSON):
                d[k] = v.to_json()
        return d

    def __repr__(self):
        return json.dumps(self.to_json(), indent=2)

class Config(PyJSON):

    def __init__(self, production: bool = False):
        load_env(production=production)
        with open("Config/config.json") as config_file:
            options = json.load(config_file)
        super().__init__(options)