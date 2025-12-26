from datetime import datetime, timedelta, timezone

import jwt

from src.model.config_model import config

SECRET_KEY= config.jwt.key
REFRESH_SECRET_KEY =config.jwt.refresh_key
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = config.jwt.token_expire_minutes
ACCESS_REFRESH_TOKEN_EXPIRE_MINUTES = config.jwt.refresh_token_expire_minutes # 刷新令牌过期时间

#添加修改字段时，需同步修改续签token函数
class Token:
    user_id: int
    role_id:int
    exp:datetime  # 超时时长
    def __init__(self, user_id: int,role_id:int,exp):
        self.user_id = user_id
        self.role_id = role_id
        self.exp=exp
    def to_dict(self):
        return self.__dict__
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

def create_token(user_id: int,role_id:int):
    try:
        data = Token(user_id,role_id,datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        encoded_jwt = jwt.encode(data.to_dict(), SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(str(e))
        return None

def decode_jwt(token: str) -> Token | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return Token.from_dict(payload)
    except Exception as e:
        print(str(e))
        return None

def create_refresh_token(user_id: int,role_id:int):
    try:
        data = Token(user_id,role_id,datetime.now(timezone.utc) + timedelta(minutes=ACCESS_REFRESH_TOKEN_EXPIRE_MINUTES))
        encoded_jwt = jwt.encode(data.to_dict(), REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(str(e))
        return None

def refresh_decode_jwt(token: str) -> Token | None:
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return Token.from_dict(payload)
    except Exception as e:
        print(str(e))
        return None

#续签token
def renew_token(refresh_token:str)->str|None:
    user_data=refresh_decode_jwt(refresh_token)
    if user_data is not None:
        return create_token(user_data.user_id,user_data.role_id)
    else:
        return None