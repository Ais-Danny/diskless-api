from typing import Tuple

from src.utils.ssh.ssh_client import SSHClient
from src.model.config_model import config

def get_pve_init_script(vmid,mac:str):
    return f'''#!/bin/bash
VMID="{vmid}"
NEW_MAC="{mac}"
qm set $VMID --net0 virtio=$NEW_MAC,bridge=vmbr0
'''


def vm_pv_config_revise(ip, mac,nfs_path)->Tuple[bool, str]:
    """
    修改VM PC的NFS配置
    ip: PVE IP地址 
    mac: PVE中windows的网mac 
    nfs_path: NFS共享路径 例:/mnt/iscsi/pve_client/101
    """
    # 初始化SSH客户端
    ssh = SSHClient(host=config.diskless.truenas_host, username=config.diskless.truenas_user, password=config.diskless.truenas_password)
    # 执行命令
    result,output=ssh.upload_file(local_path="./resource/change_vm_pve_config.sh", remote_path="/tmp/vm_pv_config_revise.sh")
    if not result:
        return False,f"Failed to upload file: {output}"
    ssh.execute_command("chmod +x /tmp/vm_pv_config_revise.sh")
    result,output=ssh.execute_command(f"bash /tmp/vm_pv_config_revise.sh {ip}/24 {ip.rsplit('.', 1)[0]}.1 {nfs_path}")
    # 生成PVE初始化脚本内容
    init_script_content = get_pve_init_script("100", mac)
    # 写入rc.local文件
    result,output = ssh.execute_command(f"echo '{init_script_content}' > {nfs_path}/etc/rc.local")
    if not result:
        return False, f"Failed to write rc.local: {output}"
    # 设置执行权限
    result,output = ssh.execute_command(f"chmod +x {nfs_path}/etc/rc.local")
    if not result:
        return False, f"Failed to set executable permission: {output}"
    return True, ''


