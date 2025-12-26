#!/bin/bash
NEW_IP="$1" # PVE IP地址
NEW_GW="$2" # PVE 网关
IFACE_FILE="$3/etc/network/interfaces" # PVE 网络配置文件位置(truenasz对应差分卷的位置)

sed -i -E "
/iface vmbr0 inet static/,/iface / {
    s|^\s*address .*|        address ${NEW_IP}|
    s|^\s*gateway .*|        gateway ${NEW_GW}|
}
" ${IFACE_FILE}

echo "vmbr0 IP updated to ${NEW_IP}"


