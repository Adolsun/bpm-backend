from typing import Dict, Any, List

from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session
from requests.exceptions import HTTPError, RequestException
from pydantic import BaseModel
from loguru import logger

from config import BILIBILI_API_BASE, BILIBILI_HEADERS
from database import get_session
from services.collection_service import (
    create_collection_to_db,
    get_collection_from_db,
    delete_collection_to_db,
    delete_collections_to_db,
    get_all_collections_from_db,
    update_collection_to_db,
)
from services.video_service import create_video_to_db, update_video_watched_count_to_db
from models.video import Video
from utils.bilibiliApi import get_collection_data_and_episodes

router = APIRouter()


class CreateCollectionRequest(BaseModel):
    bvid: str


class UpdateCollectionRequest(BaseModel):
    season_id: int


class DeleteCollectionsRequest(BaseModel):
    season_ids: List[int]


class UpdateVideoStatusRequest(BaseModel):
    season_id: int
    videos: List[Video]
    option: int


# 创建合集 - 从B站API获取信息并保存到数据库
@router.post("/collection", status_code=status.HTTP_201_CREATED)
async def create_collection(
    request: CreateCollectionRequest, session: Session = Depends(get_session)
):
    try:
        collection_data, episodes = get_collection_data_and_episodes(request.bvid)
        created_collection = create_collection_to_db(session, collection_data)

        created_collection_dict = created_collection.model_dump()

        videos_to_create: List[Dict[str, Any]] = []
        for idx, episode in enumerate(episodes):
            video_data = {
                "bvid": episode["bvid"],  # bvid
                "title": episode["title"],  # 标题
                "duration": episode["arc"]["duration"],  # 时长
                "collection_id": collection_data["season_id"],
                "order_index": idx,
            }
            videos_to_create.append(video_data)
        # 保存视频到数据库
        created_videos = create_video_to_db(session, videos_to_create)
        created_videos_list = [
            created_video.model_dump() for created_video in created_videos
        ]
        created_collection_dict["videos"] = created_videos_list

        # 所有操作成功，提交事务
        session.commit()
        logger.info(
            f"合集创建成功: season_id={collection_data['season_id']}, title={collection_data['title']}"
        )

        return {
            "status": "success",
            "code": 200,
            "message": "合集创建成功",
            "data": created_collection_dict,
        }

    except HTTPError as http_err:
        logger.error(f"HTTPError: {http_err}")
        raise
    except RequestException as e:
        logger.error(f"RequestException: {e}")
        raise
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"合集已存在: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"创建合集失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统繁忙，请稍后再试",
        )


# 删除单个合集
@router.delete("/collection/{season_id}", status_code=status.HTTP_200_OK)
async def delete_single_collection(
    season_id: int, session: Session = Depends(get_session)
):
    try:
        is_delete = delete_collection_to_db(session, season_id)
        if is_delete:
            session.commit()
            return {
                "status": "success",
                "code": 200,
                "message": "删除成功",
                "data": None,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="合集不存在",
            )
    except HTTPException:
        raise
    except Exception as e:
        # print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统繁忙，请稍后再试",
        )


# 批量删除合集
@router.delete("/collection", status_code=status.HTTP_200_OK)
async def delete_collections(
    request: DeleteCollectionsRequest, session: Session = Depends(get_session)
):
    try:
        deleted_count = delete_collections_to_db(session, request.season_ids)
        session.commit()
        return {"status": "success", "code": 200, "message": "删除成功", "data": None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统繁忙，请稍后再试",
        )


# 获取所有合集及其中的视频信息
@router.get("/collection", status_code=status.HTTP_200_OK)
async def get_collections(session: Session = Depends(get_session)):
    try:
        results = get_all_collections_from_db(session)

        if not results:
            return {
                "status": "success",
                "code": 200,
                "message": "获取所有合集信息成功",
                "data": None,
            }

        collections_dict: Dict[int, Dict[str, Any]] = {}
        for collection_obj, video_obj in results:
            collection_id = collection_obj.season_id

            # 如果这个 collection_id 还没有在字典里，则初始化它
            if collection_id not in collections_dict:
                collection_dict = collection_obj.model_dump()
                collection_dict["videos"] = []  # 初始化一个空的视频列表
                collections_dict[collection_id] = collection_dict

            collections_dict[collection_id]["videos"].append(video_obj.model_dump())

        data = list(collections_dict.values())

        return {
            "status": "success",
            "code": 200,
            "message": "获取所有合集信息成功",
            "data": data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统繁忙，请稍后再试",
        )


# 获取单个合集及其中的视频信息
@router.get("/collection/{season_id}", status_code=status.HTTP_200_OK)
async def get_collection(season_id: int, session: Session = Depends(get_session)):
    try:
        results = get_collection_from_db(session, season_id)
        # 这个函数要注意后续变化
        if not results:
            return {
                "status": "success",
                "code": 200,
                "message": "获取合集信息成功",
                "data": None,
            }
        data = []
        for collection_obj, video_obj in results:
            data.append(video_obj.model_dump())
        return {
            "status": "success",
            "code": 200,
            "message": "获取合集信息成功",
            "data": data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统繁忙，请稍后再试",
        )


# 更新视频观看次数和状态
@router.patch("/video", status_code=status.HTTP_200_OK)
async def update_video(
    request: UpdateVideoStatusRequest, session: Session = Depends(get_session)
):
    try:
        season_id = request.season_id
        videos = request.videos
        option = request.option
        collection_obj, video_objs = update_video_watched_count_to_db(
            session, season_id, videos, option
        )
        collection_dict = collection_obj.model_dump()
        collection_dict["videos"] = [video_obj.model_dump() for video_obj in video_objs]
        # print(video_objs)
        session.commit()
        return {
            "status": "success",
            "code": 200,
            "message": "获取合集信息成功",
            "data": collection_dict,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    except Exception as e:
        logger.exception(f"更新视频失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统繁忙，请稍后再试",
        )


# 更新一个合集
@router.post("/collection/update", status_code=status.HTTP_200_OK)
async def update_collection(
    request: UpdateCollectionRequest, session: Session = Depends(get_session)
):
    try:
        temp_watched_status_dict, bvid, created_at, order_index = (
            update_collection_to_db(session, request.season_id)
        )
        is_delete = delete_collection_to_db(session, request.season_id)
        if is_delete:
            session.flush()
            collection_data, episodes = get_collection_data_and_episodes(bvid)
            collection_data["created_at"] = created_at
            collection_data["order_index"] = order_index
            created_collection = create_collection_to_db(session, collection_data)
            created_collection_dict = created_collection.model_dump()
            videos_to_create: List[Dict[str, Any]] = []
            for idx, episode in enumerate(episodes):
                episode_bvid = episode["bvid"]
                video_data = {
                    "bvid": episode_bvid,  # bvid
                    "title": episode["title"],  # 标题
                    "duration": episode["arc"]["duration"],  # 时长
                    "collection_id": collection_data["season_id"],
                    "order_index": idx,
                }
                if episode_bvid in temp_watched_status_dict:
                    status_info = temp_watched_status_dict[episode_bvid]
                    # 添加到 video_data 中
                    video_data["watched_count"] = status_info[0]
                    video_data["status"] = status_info[1]
                videos_to_create.append(video_data)
            # 保存视频到数据库
            created_videos = create_video_to_db(session, videos_to_create)
            created_videos_list = [
                created_video.model_dump() for created_video in created_videos
            ]
            created_collection_dict["videos"] = created_videos_list

            # 所有操作成功，提交事务
            session.commit()

            return {
                "status": "success",
                "code": 200,
                "message": "合集更新成功",
                "data": created_collection_dict,
            }

    except Exception as e:
        logger.exception(f"更新合集失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统繁忙，请稍后再试",
        )
