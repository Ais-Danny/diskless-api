from datetime import datetime

from flask import request

from src.common.encrypt.salting import hash_password, check_password
from src.common.encrypt.token import create_token, create_refresh_token, refresh_decode_jwt
from src.common.obj.result import Result
from src.common.session import MySqlSession
from src.model import table_models


def registration(username: str, phone: str, password: str) -> Result:
    with MySqlSession() as session:
        if session.query(table_models.Users).filter_by(phone=phone).first() is None:
            user = table_models.Users(username=username, phone=phone, passwd=hash_password(password))
            session.add(user)
            session.commit()
            result = Result('注册成功')
        else:
            result = Result('', 401, f'{phone} 用户已存在')
        return result

def login(phone: str, password: str):
    with MySqlSession() as session:
        # 查询用户是否存在并验证密码
        user = session.query(table_models.Users).filter_by(phone=phone).first()
        if user and check_password(user.passwd, password):
            # 更新用户登录信息
            user.last_ip = request.remote_addr
            user.last_login_time = datetime.now()
            session.commit()
            # 生成并返回Token
            token_info = {
                'token': create_token(user.id, user.role_id),
                'refresh_token': create_refresh_token(user.id, user.role_id)
            }
            return Result(token_info)
        else:
            # 密码不正确或用户不存在
            return Result('用户名或密码错误', 401, 'error')

def refresh_token(token:str):
    user_data= refresh_decode_jwt(token)
    if user_data is not None:
        return Result(create_token(user_data.user_id,user_data.role_id))
    else:
        return Result('',401,'refresh token 无效或已过期,请重新登录')

class UserService:
    user_id:int
    role_id: int
    def __init__(self):
        pass