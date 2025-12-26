from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Role(Base):
    __tablename__ = 'role'

    id = mapped_column(Integer, primary_key=True)
    role_name = mapped_column(VARCHAR(255), comment='用户类型名称')
    permissions_code = mapped_column(String(255))

    users: Mapped[List['Users']] = relationship('Users', uselist=True, back_populates='role')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE', onupdate='CASCADE', name='users_ibfk_1'),
        Index('role_id', 'role_id')
    )

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(VARCHAR(255), nullable=False)
    passwd = mapped_column(VARCHAR(255), nullable=False)
    phone = mapped_column(VARCHAR(255), nullable=False, comment='power')
    email = mapped_column(VARCHAR(255))
    last_login_time = mapped_column(DateTime)
    role_id = mapped_column(Integer)
    last_ip = mapped_column(String(255))

    role: Mapped[Optional['Role']] = relationship('Role', back_populates='users')
