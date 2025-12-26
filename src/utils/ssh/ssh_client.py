import paramiko
from typing import Tuple, Optional, Dict, Any


class SSHClient:
    """
    SSH客户端类，用于执行远程命令
    """
    
    def __init__(self, host: str, port: int = 22, username: str = "root", password: Optional[str] = None, key_filename: Optional[str] = None):
        """
        初始化SSH客户端
        
        :param host: 远程主机IP地址或主机名
        :param port: SSH端口，默认为22
        :param username: 登录用户名，默认为root
        :param password: 登录密码（与key_filename二选一）
        :param key_filename: SSH私钥文件路径（与password二选一）
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.client: Optional[paramiko.SSHClient] = None
        self._connect()
    
    def _connect(self) -> None:
        """
        建立SSH连接
        """
        try:
            self.client = paramiko.SSHClient()
            # 自动添加未知主机的密钥
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接到远程主机
            if self.key_filename:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_filename,
                    timeout=2
                )
            else:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=2
                )
        except Exception as e:
            raise ConnectionError(f"SSH连接失败: {str(e)}")
    
    def execute_command(self, command: str,timeout: int = 3) -> Tuple[bool, Dict[str, Any]]:
        """
        执行远程命令
        
        :param command: 要执行的命令
        :return: (success, result) 元组，result包含stdout、stderr和退出码
        """
        try:
            if not self.client:
                self._connect()
            
            # 执行命令
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            
            # 读取输出
            stdout_content = stdout.read().decode("utf-8", errors="replace").strip()
            stderr_content = stderr.read().decode("utf-8", errors="replace").strip()
            exit_code = stdout.channel.recv_exit_status()
            
            # 判断执行是否成功
            success = exit_code == 0
            
            return success, {
                "stdout": stdout_content,
                "stderr": stderr_content,
                "exit_code": exit_code,
                "command": command
            }
        except Exception as e:
            return False, {
                "stdout": "",
                "stderr": f"执行命令失败: {str(e)}",
                "exit_code": -1,
                "command": command
            }
    
    def upload_file(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """
        上传文件到远程主机
        
        :param local_path: 本地文件路径
        :param remote_path: 远程文件路径
        :return: (success, message) 元组
        """
        try:
            if not self.client:
                self._connect()
            
            # 创建SFTP客户端
            sftp = self.client.open_sftp()
            
            # 上传文件
            sftp.put(local_path, remote_path)
            sftp.close()
            
            return True, f"文件上传成功: {local_path} -> {remote_path}"
        except Exception as e:
            return False, f"文件上传失败: {str(e)}"
    
    def download_file(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """
        从远程主机下载文件
        
        :param remote_path: 远程文件路径
        :param local_path: 本地文件路径
        :return: (success, message) 元组
        """
        try:
            if not self.client:
                self._connect()
            
            # 创建SFTP客户端
            sftp = self.client.open_sftp()
            
            # 下载文件
            sftp.get(remote_path, local_path)
            sftp.close()
            
            return True, f"文件下载成功: {remote_path} -> {local_path}"
        except Exception as e:
            return False, f"文件下载失败: {str(e)}"
    
    def close(self) -> None:
        """
        关闭SSH连接
        """
        if self.client:
            self.client.close()
            self.client = None
    
    def __del__(self) -> None:
        """
        对象销毁时自动关闭连接
        """
        self.close()
    
    def __enter__(self) -> "SSHClient":
        """
        支持上下文管理器
        """
        if not self.client:
            self._connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        上下文管理器退出时关闭连接
        """
        self.close()