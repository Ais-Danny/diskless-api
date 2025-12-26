import logging
from colorama import Fore, Style
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime


class Logger:
    def __init__(self, log_dir="./logs", log_filename="log_", log_level=logging.INFO):
        """
        初始化日志配置

        :param log_dir: 日志文件夹路径
        :param log_filename: 日志文件名
        :param log_level: 设置日志级别
        """
        self.log_dir = log_dir
        
        # 检查并创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 为活跃日志文件添加当前日期
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(log_dir, f"{log_filename}{today}.log")

        # 配置日志处理器
        self.log_handler = TimedRotatingFileHandler(
            filename=self.log_file,
            when="midnight",  # 每天午夜分割日志
            interval=1,  # 间隔为1天
            backupCount=7,  # 保留最近7天的日志文件
            encoding="utf-8"  # 以 UTF-8 编码写入日志
        )

        # 设置日志格式
        formatter = logging.Formatter(
            "%(asctime)s %(name)s:%(levelname)s:%(message)s",
            datefmt="%d-%m-%Y %H:%M:%S"
        )
        self.log_handler.setFormatter(formatter)

        # 配置日志记录器
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)  # 设置日志级别
        self.logger.addHandler(self.log_handler)
        
        # 抑制第三方库的日志输出到我们的日志文件
        # 只保留WARNING级别及以上的第三方库日志
        logging.getLogger("paramiko").setLevel(logging.CRITICAL)
        logging.getLogger("websocket").setLevel(logging.CRITICAL)
        logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)
        logging.getLogger("paramiko.transport.sftp").setLevel(logging.CRITICAL)

    def _log(self, level, msg, color, prefix):
        """
        私有日志记录方法，用于处理不同级别的日志

        :param level: 日志级别
        :param msg: 日志消息
        :param color: 控制台输出的颜色
        :param prefix: 日志前缀
        """
        # 日志内容颜色化
        colored_msg = f"{color}{msg}{Style.RESET_ALL}"

        # 记录日志
        level(msg)
        # 打印到控制台（包含日期时间）
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"{color}[{current_time}] {prefix}:" + Style.RESET_ALL + colored_msg)

    def error(self, msg):
        """记录错误日志"""
        self._log(self.logger.error, msg, Fore.RED, "ERROR")

    def warning(self, msg):
        """记录警告日志"""
        self._log(self.logger.warning, msg, Fore.YELLOW, "WARNING")

    def info(self, msg):
        """记录普通日志"""
        self._log(self.logger.info, msg, Fore.WHITE, "INFO")

    def success(self, msg):
        """记录成功日志"""
        self._log(self.logger.info, msg, Fore.GREEN, "SUCCESS")

    def debug(self, msg):
        """记录调试日志"""
        self._log(self.logger.debug, msg, Fore.CYAN, "DEBUG")

    def critical(self, msg):
        """记录严重错误日志"""
        self._log(self.logger.critical, msg, Fore.MAGENTA, "CRITICAL")


# Example usage
logger: Logger = Logger(log_level=logging.INFO)
# logger.info("This is an info message.")
# logger.success("This is a success message.")
# logger.error("This is an error message.")
# logger.warning("This is a warning message.")
# logger.debug("This is a debug message.")
# logger.critical("This is a critical message.")
