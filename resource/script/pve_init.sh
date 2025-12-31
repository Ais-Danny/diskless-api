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

#删除动态信息
rm -rf $3/etc/udev/rules.d/60-persistent-net.rules
truncate -s 0 $3/etc/machine-id
rm -rf $3/var/lib/dbus/machine-id
rm -rf $3/var/lib/systemd/network/*
rm -rf $3/tmp/*
rm -rf $3/run/*
rm -rf $3/proc/*
rm -rf $3/sys/*
rm -rf $3/dev/*


# # udev 网卡持久化规则（旧 Debian/Ubuntu）
# rm -f $3/etc/udev/rules.d/70-persistent-net.rules
# rm -f $3/etc/udev/rules.d/60-persistent-net.rules
# # machine-id（必须保留文件但清空）
# truncate -s 0 $3/etc/machine-id
# rm -f $3/var/lib/dbus/machine-id
# # systemd-networkd 的旧配置（如果你用它）
# rm -rf $3/var/lib/systemd/network/*
# # DHCP 租约
# rm -rf $3/var/lib/dhcp/*
# rm -rf $3/var/lib/NetworkManager/*
# # 临时目录
# rm -rf $3/tmp/*