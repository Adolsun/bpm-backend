from typing import Dict, Any

import requests
from requests.exceptions import HTTPError, RequestException
from fastapi import HTTPException, status

from config import BILIBILI_API_BASE, BILIBILI_HEADERS


def get_collection_data_and_episodes(bvid: str):
    target_url = f"{BILIBILI_API_BASE}/x/web-interface/view"
    params = {"bvid": bvid}

    # 使用配置中的请求头
    headers = BILIBILI_HEADERS

    try:
        # 向 B 站 API 发送请求
        response = requests.get(target_url, params=params, headers=headers)

        # 检查 B 站 API 的响应状态
        response.raise_for_status()  # 如果状态码不是 2xx，这里会抛出异常

        data: Dict[str, Any] = response.json()['data']
        ugc_season = data.get('ugc_season', None)
        if not ugc_season:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该视频不是合集内容"
            )

        up_name = data['owner']['name']  # up名字
        season_title = ugc_season['title']  # 合集标题
        sections = ugc_season['sections'][0]
        season_id = sections['season_id']  # 合集id
        episodes = sections['episodes']
        collection_data = {
            'season_id': season_id,
            'title': season_title,
            'total_episodes': len(episodes),
            'up_name': up_name,
        }
        return collection_data, episodes
    except HTTPError as http_err:
        # 捕获 HTTP 状态码错误 (4xx, 5xx)
        # print(f"HTTP error from Bilibili API: {http_err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="无法连接B站API，请稍后再试")
    except RequestException as e:
        # 捕获其他请求异常（如网络错误、超时等）
        # print(f"Error fetching from Bilibili API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="B站API请求超时，请稍后再试")
    except HTTPException:
        raise
