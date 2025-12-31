from ast import Or
import os
from src.utils.truenas import truenas_api
from src.model.config_model import config
from src.utils.truenas.truenas_api import TrueNASEntity
from src.services.diskless.pve_init import vm_pv_config_revise


def create_diff_directory(ip):
    """
    根据IP地址创建差分目录
    1. 查询对应的差分目录是否存在(存在则删除)
    2. 使用IP最后一位创建指定数据集快照的差分目录（例如/mnt/iscsi/pve_client/202）

    """
    # 解析IP最后一位
    try:
        ip_last_octet = ip.split('.')[-1]
        # 转换为两位十六进制表示（小写）
        if not ip_last_octet.isdigit():
            raise ValueError(f"Invalid IP address format: {ip}")
    except Exception as e:
        raise ValueError(f"Failed to parse IP address: {str(e)}")
    
    # 初始化TrueNAS API客户端
    client = TrueNASEntity()
    # 定义源数据集和快照信息
    result, data = client.find_snapshots_order_by_time(config.diskless.pve.pve_base)
    if result is False:
        return False, "Failed to find snapshots"
    snapshot_name = f"{data[0]["name"]}"  # 快照名称
    new_dataset=f"{config.diskless.pve.pve_client}/{ip_last_octet}" #差分数据集名称
    pc_mac=f"{config.diskless.pve.vm_pc_mac_prefix}:{f"{int(ip_last_octet):02x}"}"
    # 创建差分目录
    result, msg = client.clone_dataset_from_snapshot(snapshot_name, new_dataset, overwrite=True)
    if result is False:
        return False, f"Failed to clone dataset from snapshot: {msg}"

    nfs_dir= f"/mnt/{new_dataset}"
    # 创建NFS共享
    result, msg = client.create_nfs_share(nfs_dir, comment=f"VM PC {pc_mac}")
    if result is False or msg is None:
        return False, f"Failed to create NFS share"
    # 修改pve启动ip
    result, msg = vm_pv_config_revise(ip,pc_mac,nfs_dir)
    if result is False:
        return False, f"Failed to change VM PV config: {msg}"
        
    return True, nfs_dir


def start_base_os(ip:str):
    """
    启动母盘OS系统
    """
    ip_last_octet = ip.split('.')[-1]
    pc_mac=f"{config.diskless.pve.vm_pc_mac_prefix}:{f"{int(ip_last_octet):02x}"}"
    nfs_root=f'/mnt/{config.diskless.pve.pve_base}'
    result, msg = vm_pv_config_revise(ip,pc_mac,nfs_root)
    if result is False:
        return False, f"Failed to change VM PV config: {msg}"
    return True, nfs_root
