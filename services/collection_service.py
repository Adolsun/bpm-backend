from typing import List, Optional, Tuple
from datetime import datetime

from sqlmodel import Session, select, update
from models.collection import Collection
from models.video import Video
from sqlalchemy import delete
from services.video_service import get_videos_by_collection_from_db


def create_collection_to_db(session: Session, collection_data: dict) -> Collection:
    existing = session.get(Collection, collection_data["season_id"])
    if existing:
        raise ValueError("该合集已存在，请勿重复添加")

    collection = Collection(**collection_data)
    session.add(collection)
    session.flush()
    session.refresh(collection)
    return collection


def batch_update_collection_order(session: Session, updates: List[dict]) -> int:
    for item in updates:
        stmt = (
            update(Collection)
            .where(Collection.season_id == item["season_id"])
            .values(order_index=item["order_index"])
        )
        session.execute(stmt)
    session.flush()
    return len(updates)


# 从数据库获取所有合集信息
def get_all_collections_from_db(session: Session) -> List[Tuple[Collection, Video]]:
    statement = (
        select(Collection, Video)
        .join(Video, Collection.season_id == Video.collection_id)
        .order_by(
            Collection.order_index,
            Collection.created_at.desc(),
            Collection.season_id,
            Video.order_index,
        )
    )
    results = session.exec(statement).all()
    return results


# 从数据库删除单个合集
def delete_collection_to_db(session: Session, season_id: int) -> bool:
    collection = session.get(Collection, season_id)
    if collection:
        session.delete(collection)
        return True
    return False


# 从数据库批量删除合集
def delete_collections_to_db(session: Session, season_ids: List[int]) -> int:
    stmt = delete(Collection).where(Collection.season_id.in_(season_ids))
    result = session.execute(stmt)
    deleted_count = result.rowcount  # 获取被删除的行数
    return deleted_count


# 更新合集信息
def update_collection_to_db(
    session: Session, season_id: int
) -> Tuple[dict, str, datetime, int]:
    # 查出合集中的视频
    orm_videos = get_videos_by_collection_from_db(session, season_id)
    # 根据bvid保留视频的watched_count和status
    temp_watched_status_dict = {}
    for orm_video in orm_videos:
        bvid = orm_video.bvid
        watched_count = orm_video.watched_count
        status = orm_video.status
        temp_watched_status_dict[bvid] = (watched_count, status)
    # 取出一个bvid后续使用
    bvid = orm_videos[0].bvid
    # 查出合集的创建时间created_at和order_index
    orm_collection = session.get(Collection, season_id)
    created_at, order_index = orm_collection.created_at, orm_collection.order_index
    return temp_watched_status_dict, bvid, created_at, order_index
