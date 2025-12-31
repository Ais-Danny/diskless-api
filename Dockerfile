# 使用官方 Python 镜像
FROM python:3.13.1
# 设置工作目录
WORKDIR /app
# 设置时区
ENV TZ=Asia/Shanghai
# 复制项目文件到镜像中
COPY . /app
# 使用阿里云源安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
# 暴露端口
EXPOSE 8080
# 默认启动命令
CMD ["python", "/app/app.py"]
