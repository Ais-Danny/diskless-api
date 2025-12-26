from truenas_api_client import Client,LegacyClient,JSONRPCClient
from src.model.config_model import config


class TrueNASEntity:
    def __init__(self):
        self._client: LegacyClient | JSONRPCClient | None = None
        self._connect()

    def _connect(self):
        """创建连接并登录"""
        self._client = Client(uri=f"ws://{config.diskless.truenas_host}/api/current")
        self._client.__enter__()  # 手动进入上下文
        self._client.call(
            "auth.login",
            config.diskless.truenas_user,
            config.diskless.truenas_password,
        )

    @property
    def c(self) -> LegacyClient | JSONRPCClient:
        if self._client is None:
            raise RuntimeError("TrueNAS client not connected")
        return self._client
    # ========= 生命周期管理 =========

    def close(self):
        """手动关闭（推荐显式调用）"""
        if self._client:
            self._client.__exit__(None, None, None)
            self._client = None

    def __del__(self):
        """对象销毁时自动关闭（兜底）"""
        try:
            self.close()
        except Exception:
            pass

    # ========= 业务封装 =========
    def find_snapshots_order_by_time(self, snapshot_name: str | None = None) -> tuple[bool, any]:
        """
        按时间顺序查询快照
        :param snapshot_name: 筛选条件
        :return: (success, result) 元组
        """
        try:
            if snapshot_name:
                result = self.c.call(
                    "pool.snapshot.query",
                    [["name", "rin", f"{snapshot_name}"]],
                    {
                        "select": [
                            "name",
                            "dataset",
                            "snapshot_name",
                            "createtxg",
                        ],
                        "order_by": ["-createtxg"]   # 按创建时间降序
                    }
                )
            else:
                result = self.c.call("pool.snapshot.query")
            return True, result
        except Exception as e:
            return False, f"query snapshots error: {str(e)}"

    def clone_dataset_from_snapshot(
            self,
            snapshot_full_name: str,
            new_dataset: str,
            overwrite: bool = False
    ) -> tuple[bool, any]:
        """
        根据快照创建新的数据集（ZFS clone，差分卷）
        :param snapshot_full_name: 完整快照名 dataset@snapshot  例如 iscsi/pve_nfs@pve_base
        :param new_dataset: 新数据集名 例如 iscsi/pve_nfs/client01
        :param overwrite: 如果目标数据集已存在，是否覆盖（删除后重新创建）
        :return: (success, result) 元组
        """
        try:
            # 检查快照是否存在
            success, snapshot_exists = self.snapshot_exists(snapshot_full_name)
            if not success:
                return False, f"check snapshot exists error: {snapshot_exists}"
            if not snapshot_exists:
                return False, f"source snapshot {snapshot_full_name} not exists."
            
            # 检查目标数据集是否存在
            success, dataset_exists = self.dataset_exists(new_dataset)
            if not success:
                return False, f"check dataset exists error: {dataset_exists}"
            if dataset_exists:
                if overwrite:
                    # 允许覆盖，先删除现有数据集
                    success, delete_result = self.delete_dataset(new_dataset, recursive=True)
                    if not success:
                        return False, f"delete dataset error: {delete_result}"
                else:
                    return False, f"target dataset {new_dataset} already exists."
            # 执行克隆操作
            result = self.c.call(
                "pool.snapshot.clone",
                {
                    "snapshot": snapshot_full_name,
                    "dataset_dst": new_dataset
                }
            )
            return True, result
        except Exception as e:
            return False, f"Copy error: {str(e)}"
            
    def dataset_exists(self, dataset: str) -> tuple[bool, any]:
        """
        查询数据集是否存在
        :param dataset: 数据集名称
        :return: (success, result) 元组
        """
        try:
            result = self.c.call(
                "pool.dataset.query",
                [["name", "=", dataset]]
            )
            return True, len(result) > 0
        except Exception as e:
            return False, f"dataset exists query error: {str(e)}"

    def snapshot_exists(self, snapshot: str) -> tuple[bool, any]:
        """
        查询快照是否存在
        :param snapshot: 快照名称
        :return: (success, result) 元组
        """
        try:
            result = self.c.call(
                "pool.snapshot.query",
                [["name", "=", snapshot]]
            )
            return True, len(result) > 0
        except Exception as e:
            return False, f"snapshot exists query error: {str(e)}"

    def delete_dataset(self, dataset: str, recursive: bool = False) -> tuple[bool, any]:
        """
        删除 ZFS 数据集
        :param dataset: 数据集完整名称 例如 iscsi/pve_nfs/client01
        :param recursive: 是否递归删除（包含子数据集、快照）
        :return: (success, result) 元组
        """
        try:
            result = self.c.call(
                "pool.dataset.delete",
                dataset,
                {
                    "recursive": recursive
                }
            )
            return True, result
        except Exception as e:
            return False, f"delete dataset error: {str(e)}"


#region nfs模块
    def create_nfs_share(self, path: str, comment: str = "", networks: list[str] = None, hosts: list[str] = None, ro: bool = False) -> tuple[bool, any]:
        """
        创建 NFS 共享
        :param path: 要导出的本地路径 例如 /mnt/iscsi/pve_client/101
        :param comment: 与共享关联的用户注释
        :param networks: 允许访问共享的授权网络列表（CIDR格式）
        :param hosts: 允许访问共享的IP/主机名列表
        :param ro: 是否以只读方式导出共享
        :return: (success, result) 元组
        """
        try:
            result, exists = self.nfs_share_exists(path)
            if result is True and exists is True:
                return True, True
            # 设置默认值
            if networks is None:
                networks = []
            if hosts is None:
                hosts = []
            
            # 执行创建NFS共享操作
            result = self.c.call(
                "sharing.nfs.create",
                {
                    "path": path,
                    "comment": comment,
                    "networks": networks,
                    "hosts": hosts,
                    "ro": ro,
                    "maproot_user": "root",
                    "maproot_group": "root",
                }
            )
            return True, result
        except Exception as e:
            return False, f"create nfs share error: {str(e)}"
    
    def delete_nfs_share(self, path: str) -> tuple[bool, any]:
        """
        删除指定路径的NFS共享（删除所有匹配该路径的共享）
        :param path: 要删除的NFS共享路径
        :return: (success, result) 元组，result为删除结果列表
        """
        try:
            # 首先查询所有匹配该路径的NFS共享
            query_result = self.c.call(
                "sharing.nfs.query",
                [["path", "=", path]]
            )
            
            # 如果没有找到匹配的共享
            if not query_result:
                return True, []
            
            # 遍历所有匹配的共享，逐个删除
            delete_results = []
            for share in query_result:
                share_id = share.get("id")
                if share_id:
                    delete_result = self.c.call("sharing.nfs.delete", share_id)
                    delete_results.append({
                        "share_id": share_id,
                        "path": share.get("path"),
                        "result": delete_result
                    })
            return True, delete_results
        except Exception as e:
            return False, f"delete nfs share error: {str(e)}"
    
    def nfs_share_exists(self, path: str) -> tuple[bool, any]:
        """
        检查 NFS 共享是否存在
        :param path: 要检查的NFS共享路径
        :return: (success, result) 元组，result为True表示存在，False表示不存在
        """
        try:
            # 执行查询NFS共享操作
            result = self.c.call(
                "sharing.nfs.query",
                [["path", "=", path]]
            )
            return True, len(result) > 0
        except Exception as e:
            return False, f"check nfs share exists error: {str(e)}"
    
#endregion
