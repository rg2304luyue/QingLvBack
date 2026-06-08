"""
清律健康后端启动脚本
在 PyCharm 中直接右键运行此文件即可启动
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
