from sqlmodel import create_engine, Session
from contextlib import contextmanager
from config import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session