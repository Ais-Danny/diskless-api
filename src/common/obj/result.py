import json
from dataclasses import dataclass

@dataclass
class Result:
    code: int
    msg: str
    data: object
    def __init__(self,data=None, code :int=200, msg :str='ok'):
        self.code = code
        self.msg = msg
        self.data = data
    def to_json(self):
            json.dumps(self.__dict__)



