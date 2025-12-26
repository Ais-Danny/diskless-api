"""
加盐MD5加密
"""
import base64
import hashlib

from src.model.config_model import config

salt = base64.b64decode(config.md5_salt)

def hash_password(password):
    # 将盐和密码组合后进行哈希
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)
    return str(hashed_password.hex())
def check_password( stored_hashed_password:str, input_password:str):
    hash_to_check = hashlib.pbkdf2_hmac('sha256', input_password.encode('utf-8'), salt, 10000)
    return hash_to_check.hex() == stored_hashed_password