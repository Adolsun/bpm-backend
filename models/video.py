from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Integer, SmallInteger, CHAR, Enum, ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMINT


class Video(SQLModel, table=True):
    __tablename__ = "videos"

    bvid: str = Field(max_length=12, sa_column=Column(CHAR(12), primary_key=True, comment='BV号'))
    title: str = Field(max_length=50, sa_column=Column(String(50), nullable=False, comment='视频标题'))
    duration: int = Field(sa_column=Column(MEDIUMINT, nullable=False, comment='视频时长（秒）'))
    collection_id: int = Field(
        sa_column=Column(Integer, ForeignKey("collections.season_id", ondelete="CASCADE"), nullable=False,
                         comment='所属合集ID'))
    watched_count: int = Field(default=0, sa_column=Column(SmallInteger, default=0, comment='观看次数'))
    order_index: int = Field(default=0,
                             sa_column=Column(SmallInteger, default=0, comment='排序索引，用于视频在合集内的排序'))
    status: str = Field(sa_column=Column(Enum('not_watched', 'watched', 'partially_watched'),
                                         default='not_watched', comment='观看状态'))
