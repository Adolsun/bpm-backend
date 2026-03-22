from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.collection_video.router import router as collection_video_router
import uvicorn
import os
from loguru import logger

os.makedirs("logs", exist_ok=True)

if len(logger._core.handlers) <= 1:
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )

app = FastAPI()

origins = ["http://localhost:5173"]

# --- CORS 配置 ---
# 允许所有来源（开发时方便，生产环境请配置更严格的规则）
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(collection_video_router, tags=["合集视频管理"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
