import logging
import os

from flask import Flask, Blueprint
from flask_restx import Api
import src.controllers.interceptors
from src.model.config_model import config

# flask蓝图
user_bp = Blueprint('user', __name__)
diskless_bp = Blueprint('diskless', __name__)


# 先创建应用
app = Flask(__name__,
            static_folder=os.path.abspath(config.dist),
            static_url_path=''
            )
app.json.ensure_ascii = False  # 禁用ascii编码

# 初始化API（模块级别，供控制器导入使用）
api = Api(app,
          version='1.0',
          title='Sample API',
          description='A sample API',
          doc="/doc"
          )

# 导入控制器（在蓝图注册前导入，确保路由被添加到蓝图）
try:
    import src.controllers.user_controller
    import src.controllers.diskless.diskless_controller
except ImportError as e:
    logging.error(f"Failed to import controllers: {e}")

def create_app():
    # 注册蓝图
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(diskless_bp, url_prefix='/api/v1/diskless')
    return app


app = create_app()


def start():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # 设置为ERROR级别，这样只有错误信息会被打
    # 拦截器
    app.before_request(src.controllers.interceptors.before)
    app.run(
        host='0.0.0.0',
        port=config.port,
        threaded=True,
        debug=False,
        use_reloader=False,
    )
