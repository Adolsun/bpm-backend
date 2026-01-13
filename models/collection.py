from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Integer, SmallInteger, DateTime, text


class Collection(SQLModel, table=True):
    __tablename__ = "collections"

    season_id: int = Field(sa_column=Column(Integer, primary_key=True, comment='合集ID'))
    title: str = Field(max_length=100, sa_column=Column(String(100), nullable=False, comment='合集标题'))
    total_episodes: int = Field(sa_column=Column(SmallInteger, nullable=False, comment='合集总集数'))
    up_name: str = Field(max_length=16, sa_column=Column(String(16), comment='UP主名称'))
    order_index: int = Field(default=0, sa_column=Column(SmallInteger, default=0, comment='排序索引，用于拖动排序'))
    created_at: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间'))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"),
                         server_onupdate=text("CURRENT_TIMESTAMP"), comment='最后修改时间'))
    last_sync_at: datetime = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='最后同步时间'))
