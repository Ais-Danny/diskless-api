"""
实体类与配置文件双向映射
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml
from cattrs import structure, unstructure

@dataclass(order=True)
class Pve:
    vm_pc_mac_prefix: str="1a:2b:3c:4d:5e" # windows mac地址(防止启动时mac地址冲突,最后一位根据ip动态改变)
    pve_base: str = 'data/pve_base' #父数据集
    pve_client: str = 'data/pve_client' #差分数据集(客户端)

@dataclass(order=True)
class Diskless:
    truenas_host: str = '127.0.0.1' #truenas服务器ip
    truenas_user: str = 'root'
    truenas_password: str = 'skycode'
    pve: Pve = field(default_factory=Pve)

@dataclass(order=True)
class Jwt:
    key: str = 'JwtKey123'
    token_expire_minutes: int = 120
    refresh_key:str = 'JwtRefreshKey123'
    refresh_token_expire_minutes:int = 7200 #长token过期时长

@dataclass
class Mysql:
    host: str = '127.0.0.1'
    port: int = 3306
    username: str = 'root'
    password: str = 'root'
    database: str = 'aisdanny_db'
    pool_size: int = 10     #连接池大小
    max_overflow: int = 20  #连接池队列大小

@dataclass(order=True)
class Project:
    name:str = 'dev'
    dist: str = './dist'    #前端静态目录
    port: int = 8080        #flask端口
    md5_salt:str = 'aisdanny'   #md5盐值
    diskless: Diskless = field(default_factory=Diskless)
    jwt: Jwt = field(default_factory=Jwt)
    mysql: Mysql = field(default_factory=Mysql)
@dataclass
class Config:

    model:str='dev'
    configs:List[Project]=field(default_factory=list)
    def get_config(self):
        for _config in self.configs:
            if _config.name == self.model:
                return _config
            
    def load(self, path='config.yaml'):
        if Path(path).exists():
            with open(path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
                loaded = structure(data, Config)
                return loaded
        else:
            # 如果文件不存在，才写入默认值
            self.configs.append(Project(name=self.model))
            self.save(path)
            return self

    def save(self, path='config.yaml'):
        with open(path, 'w') as f:
            # 使用 sort_keys=False 保持字典顺序
            yaml.dump(unstructure(self), f, sort_keys=False)

#配置文件实体类
config_entity =  Config().load()
config:Project = config_entity.get_config()
config_entity.save() #更新配置文件