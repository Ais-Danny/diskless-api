"""
自动根据数据库表格生成实体类
-- 只能独立运行，不要在项目中直接调用
*** 生成path默认在./src/model/table_models.py
"""
import subprocess,os
# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件的父目录路径
parent_dir_path = os.path.dirname(current_file_path)
# 再上一层目录
upper_parent_dir_path = os.path.dirname(parent_dir_path)
# 改变当前工作目录到上一层目录
os.chdir(upper_parent_dir_path)
from src.model.config_model import config
database_url = (f"mysql+mysqldb://{config.mysql.username}"
                f":{config.mysql.password}"
                f"@{config.mysql.host}"
                f":{config.mysql.port}"
                f"/{config.mysql.database}")
output_file = "./src/model/table_models.py"

if __name__ == "__main__":
    subprocess.run(["sqlacodegen_v2", database_url, "--outfile", output_file])