from typing import Dict, Any

import requests
from requests.exceptions import HTTPError, RequestException
from fastapi import HTTPException, status
from loguru import logger

from config import BILIBILI_API_BASE, BILIBILI_HEADERS


def get_collection_data_and_episodes(bvid: str):
    target_url = f"{BILIBILI_API_BASE}/x/web-interface/view"
    params = {"bvid": bvid}

    headers = BILIBILI_HEADERS

    try:
        logger.info(f"请求B站API: bvid={bvid}")
        response = requests.get(target_url, params=params, headers=headers)

        response.raise_for_status()

        data: Dict[str, Any] = response.json()["data"]
        ugc_season = data.get("ugc_season", None)
        if not ugc_season:
            logger.warning(f"该视频不是合集内容: bvid={bvid}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该视频不是合集内容"
            )

        up_name = data["owner"]["name"]
        season_title = ugc_season["title"]
        sections = ugc_season["sections"][0]
        season_id = sections["season_id"]
        episodes = sections["episodes"]
        collection_data = {
            "season_id": season_id,
            "title": season_title,
            "total_episodes": len(episodes),
            "up_name": up_name,
        }
        logger.info(
            f"获取合集信息成功: season_id={season_id}, title={season_title}, episodes={len(episodes)}"
        )
        return collection_data, episodes
    except HTTPError as http_err:
        logger.error(f"B站API HTTP错误: {http_err}, bvid={bvid}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法连接B站API，请稍后再试",
        )
    except RequestException as e:
        logger.error(f"B站API请求异常: {e}, bvid={bvid}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="B站API请求超时，请稍后再试",
        )
    except HTTPException:
        raise
