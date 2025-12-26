from flask import Blueprint, request, Response
from src.model.config_model import config
import src.services.diskless.diskless_service as diskless_service

from src.utils.logs import logger
# 避免循环导入，使用局部导入

# 导入蓝图和api
from src.main import diskless_bp
from src.main import api

@api.doc(description='根据数据集快照创建到指定对应的差分目录接口')
@diskless_bp.route('/create_diff', methods=['GET'])
def create_diff():
    ip = request.args.get('ip')
    mac = request.args.get('mac')
    logger.info(f"客户端登录请求中: ip={ip}, mac={mac} (pve登录信息)")
    if not ip or not mac:
        return Response('Error: Missing required parameters (ip and mac)', status=400, mimetype='text/plain')
    
    try:
        # 调用service层创建差分目录
        result,nfs_root   =  diskless_service.create_diff_directory(ip)
        if result is False:
            return Response(f'Error: {nfs_root}', status=500, mimetype='text/plain')
        
        # 返回ipxe能直接执行的格式，设置环境变量
        ipxe_script =f'''#!ipxe
kernel http://${{ipxe_server}}/pxe/pve/vmlinuz ip=dhcp root=/dev/nfs nfsroot={config.diskless.truenas_host}:{nfs_root},vers=3,tcp,rw cloud-init=disabled  net.ifnames=0 biosdevname=0
initrd http://${{ipxe_server}}/pxe/pve/initrd.img
boot
'''
        logger.success(f"Generated ipxe script for {ip} with nfs_root {nfs_root},登录成功")

        return Response(ipxe_script, status=200, mimetype='text/plain')
    except Exception as e:
        return Response(f'Error: {str(e)}', status=500, mimetype='text/plain')
