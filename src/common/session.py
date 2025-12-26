from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.model.config_model import config

DATABASE_URL = (f"mysql+mysqldb://"
                f"{config.mysql.username}:"
                f"{config.mysql.password}@"
                f"{config.mysql.host}:"
                f"{config.mysql.port}/"
                f"{config.mysql.database}")
engine = create_engine(DATABASE_URL,
                       pool_size=config.mysql.pool_size,
                       max_overflow=config.mysql.max_overflow)

SessionFactory = scoped_session(sessionmaker(bind=engine))
class MySqlSession(object)  :
    def __init__(self):
        self.session = None

    def __enter__(self):
        self.session = SessionFactory()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 检查是否有异常发生，如果有，则回滚事务
        if exc_type is not None:
            self.session.rollback()
        self.session.close()


