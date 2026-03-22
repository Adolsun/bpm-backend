from typing import List, Optional, Tuple
from sqlmodel import Session, select
from models.video import Video
from models.collection import Collection


# 将视频数据写入数据库
def create_video_to_db(session: Session, videos_to_create: list) -> list[Video]:
    video_objects = [Video(**video_data) for video_data in videos_to_create]
    session.add_all(video_objects)
    session.flush()
    return video_objects


# 根据合集ID从数据库获取视频列表
def get_videos_by_collection_from_db(session: Session, collection_id: int) -> List[Video]:
    statement = select(Video).where(Video.collection_id == collection_id)
    videos = session.exec(statement).all()
    return videos


# 更新视频观看次数
def update_video_watched_count_to_db(
        session: Session,
        season_id: int,
        videos: List[Video],
        option: int
) -> [Collection, List[Video]]:
    video_bvids = [video.bvid for video in videos]
    statement = select(Video).where(Video.bvid.in_(video_bvids))
    orm_videos = session.exec(statement).all()
    if option == 1:
        for video in orm_videos:
            video.watched_count += 1
            if video.status != 'watched':
                video.status = 'watched'
    elif option == 2:
        for video in orm_videos:
            if video.watched_count == 0:
                if video.status == 'partially_watched':
                    video.status = 'not_watched'
                continue
            video.watched_count -= 1
            if video.watched_count == 0:
                video.status = 'not_watched'
    elif option == 0:
        for video in orm_videos:
            if video.watched_count != 0:
                continue
            video.status = 'partially_watched'
    else:
        raise ValueError('非法option')
    session.flush()
    statement1 = select(Collection).where(Collection.season_id == season_id)
    collection = session.exec(statement1).first()
    statement2 = select(Video).where(Video.collection_id == season_id)
    orm_videos = session.exec(statement2).all()
    return collection, orm_videos
