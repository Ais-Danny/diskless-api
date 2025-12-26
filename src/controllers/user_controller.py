from flask import Blueprint, request, jsonify

import src.services.user_service as user_service
from flask_restx import Api
from src.main import user_bp
from src.main import api


@api.doc(description='用户登录接口')
@user_bp.route('/login', methods=['POST'])
def login():
    phone = request.json['phone']
    password = request.json['password']
    data = user_service.login(phone, password)
    return jsonify(data), data.code


@user_bp.route('/registration', methods=['POST'])
def registration():
    phone = request.json['phone']
    password = request.json['password']
    username = request.json['username']
    data = user_service.registration(username, phone, password)
    return jsonify(data), data.code


@user_bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    token = request.authorization.token
    data = user_service.refresh_token(token)
    return jsonify(data), data.code
