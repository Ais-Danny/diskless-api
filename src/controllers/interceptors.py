"""
请求拦截器
"""

import re
from flask import request, jsonify, g

from src.common.encrypt.token import decode_jwt
from src.common.obj.result import Result

WHITE_LIST = [
    '/api/v1/users/login',
    '/api/v1/users/registration',
    '/api/v1/users/refresh_token',
    '/',
    '/doc*',
    '/swagger*',

    "/api/v1/diskless/*"
]
METHOD_WHITE_LIST = ['OPTIONS']


def before():
    if is_path_allowed(request.path) or request.method in METHOD_WHITE_LIST:
        pass
    else:
        try:
            # 获取并验证token
            if request.authorization != '' and request.authorization is not None:
                token = request.authorization.token
                user_data = decode_jwt(token)
                if user_data is not None:
                    g.user_data = user_data
                    pass
                else:
                    return jsonify(Result('', 401, 'token error')), 401
            else:
                return jsonify(Result('', 401, 'not token')), 401
        except Exception as e:  # 处理其他非预期异常
            print(str(e))
            return jsonify(Result('', 500, '')), 500


def is_path_allowed(path):
    # 处理WHITE_LIST中的条目，将含'*'的转换为正则表达式
    regex_patterns = []
    for item in WHITE_LIST:
        if '*' in item:
            # 如果'*'不在开头，我们需要保留前面的部分，并将'*'替换为'.*'来匹配任意字符序列
            if item.index('*') != 0:
                prefix = re.escape(item[:item.index('*')])
                suffix = item[item.index('*') + 1:]
                if suffix:  # 如果'*'后面有字符，加上结尾的字符
                    regex_item = '^{}.*{}'.format(prefix, re.escape(suffix))
                else:  # 如果'*'是最后一个字符，匹配任何以prefix开头的路径
                    regex_item = '^{}.*'.format(prefix)
            else:  # 如果'*'在开头，匹配所有以suffix开始的路径
                suffix = item[item.index('*') + 1:]
                regex_item = '^{}.*'.format(re.escape(suffix))
            regex_patterns.append(regex_item)
        else:
            # 完全匹配的路径，保持原样
            regex_patterns.append('^{}$'.format(re.escape(item)))

    # 使用正则表达式匹配路径
    for pattern in regex_patterns:
        if re.match(pattern, path):
            return True
    # 若无匹配项，则返回False，表示路径不允许
    return False
