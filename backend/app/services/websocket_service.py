from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃连接 {user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 存储用户状态 {user_id: {"last_seen": datetime, "is_typing": bool}}
        self.user_status: Dict[int, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_status[user_id] = {
            "is_online": True,
            "last_seen": None,
            "is_typing": False
        }
        print(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, user_id: int):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_status:
            self.user_status[user_id]["is_online"] = False
        print(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, user_id: int, message: dict):
        """发送个人消息"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                # 连接可能已断开，清理连接
                self.disconnect(user_id)
                return False
        return False
    
    async def broadcast_message(self, message: dict, exclude_user_id: int = None):
        """广播消息给所有连接的用户"""
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections
    
    def get_online_users(self) -> List[int]:
        """获取在线用户列表"""
        return list(self.active_connections.keys())
    
    def get_user_count(self) -> int:
        """获取在线用户数量"""
        return len(self.active_connections)
    
    async def send_typing_notification(self, sender_id: int, receiver_id: int, is_typing: bool):
        """发送打字状态通知"""
        if receiver_id in self.active_connections:
            message = {
                "type": "typing",
                "sender_id": sender_id,
                "is_typing": is_typing
            }
            await self.send_personal_message(receiver_id, message)
    
    async def send_online_status_update(self, user_id: int, is_online: bool):
        """发送用户在线状态更新"""
        message = {
            "type": "user_status",
            "user_id": user_id,
            "is_online": is_online
        }
        await self.broadcast_message(message, exclude_user_id=user_id)
    
    def set_user_typing(self, user_id: int, is_typing: bool):
        """设置用户打字状态"""
        if user_id in self.user_status:
            self.user_status[user_id]["is_typing"] = is_typing
    
    def get_user_status(self, user_id: int) -> dict:
        """获取用户状态"""
        return self.user_status.get(user_id, {
            "is_online": False,
            "last_seen": None,
            "is_typing": False
        })


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
