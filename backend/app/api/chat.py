from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio

from ..core.database import get_db
from ..core.security import get_current_user, get_current_user_optional
from ..models.user import User
from ..schemas.chat import (
    MessageCreate, MessageResponse, ConversationResponse, 
    ConversationListResponse, MessageListResponse, ProductConsultRequest,
    ConsultationResponse
)
from ..services.chat_service import ChatService
from ..services.websocket_service import WebSocketManager

router = APIRouter()
chat_service = ChatService()
websocket_manager = WebSocketManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket连接端点"""
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 处理不同类型的消息
            if message_data.get("type") == "message":
                # 发送消息
                message = await chat_service.send_message(
                    db=db,
                    sender_id=user_id,
                    receiver_id=message_data["receiver_id"],
                    content=message_data["content"],
                    message_type=message_data.get("message_type", "text")
                )
                
                # 广播消息给接收者
                await websocket_manager.send_personal_message(
                    message_data["receiver_id"],
                    {
                        "type": "new_message",
                        "message": message.dict()
                    }
                )
                
                # 确认发送给发送者
                await websocket_manager.send_personal_message(
                    user_id,
                    {
                        "type": "message_sent",
                        "message": message.dict()
                    }
                )
            
            elif message_data.get("type") == "typing":
                # 打字状态通知
                await websocket_manager.send_personal_message(
                    message_data["receiver_id"],
                    {
                        "type": "typing",
                        "sender_id": user_id,
                        "is_typing": message_data.get("is_typing", True)
                    }
                )
            
            elif message_data.get("type") == "read":
                # 标记消息已读
                await chat_service.mark_messages_as_read(
                    db, message_data["conversation_id"], user_id
                )
                
                # 通知对方消息已读
                conversation = await chat_service.get_conversation(
                    db, message_data["conversation_id"], user_id
                )
                if conversation:
                    other_user_id = conversation.user1_id if conversation.user2_id == user_id else conversation.user2_id
                    await websocket_manager.send_personal_message(
                        other_user_id,
                        {
                            "type": "messages_read",
                            "conversation_id": message_data["conversation_id"],
                            "reader_id": user_id
                        }
                    )
                    
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)

@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取对话列表"""
    return await chat_service.get_user_conversations(db, current_user.id, page, page_size)

@router.post("/conversations")
async def create_conversation(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建对话"""
    if other_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能与自己创建对话")
    
    conversation = await chat_service.get_or_create_conversation(db, current_user.id, other_user_id)
    return {"conversation_id": conversation.id, "message": "对话创建成功"}

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取对话详情"""
    conversation = await chat_service.get_conversation(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除对话"""
    success = await chat_service.delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在或无权限删除")
    return {"message": "对话删除成功"}

@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取对话消息列表"""
    return await chat_service.get_conversation_messages(db, conversation_id, current_user.id, page, page_size)

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送消息（HTTP接口）"""
    try:
        # 验证对话权限
        conversation = await chat_service.get_conversation(db, conversation_id, current_user.id)
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        # 确定接收者
        receiver_id = conversation.user1_id if conversation.user2_id == current_user.id else conversation.user2_id
        
        # 发送消息
        message = await chat_service.send_message(
            db=db,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=message_data.content,
            message_type=message_data.message_type,
            conversation_id=conversation_id
        )
        
        # 通过WebSocket通知接收者
        await websocket_manager.send_personal_message(
            receiver_id,
            {
                "type": "new_message",
                "message": message.dict()
            }
        )
        
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/messages", response_model=MessageResponse)
async def send_direct_message(
    receiver_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """直接发送消息（创建对话）"""
    if receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能向自己发送消息")
    
    try:
        message = await chat_service.send_message(
            db=db,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=message_data.content,
            message_type=message_data.message_type
        )
        
        # 通过WebSocket通知接收者
        await websocket_manager.send_personal_message(
            receiver_id,
            {
                "type": "new_message", 
                "message": message.dict()
            }
        )
        
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记消息已读"""
    success = await chat_service.mark_message_as_read(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在或已读")
    return {"message": "消息已标记为已读"}

@router.put("/conversations/{conversation_id}/read")
async def mark_conversation_as_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记对话所有消息已读"""
    success = await chat_service.mark_messages_as_read(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"message": "对话消息已全部标记为已读"}

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除消息"""
    success = await chat_service.delete_message(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在或无权限删除")
    return {"message": "消息删除成功"}

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取未读消息数量"""
    count = await chat_service.get_unread_message_count(db, current_user.id)
    return {"count": count}

@router.post("/upload-image")
async def upload_chat_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传聊天图片"""
    try:
        image_url = await chat_service.upload_chat_image(file, current_user.id)
        return {"image_url": image_url, "message": "图片上传成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="图片上传失败")

@router.get("/search")
async def search_messages(
    keyword: str = Query(..., min_length=1),
    conversation_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """搜索消息"""
    return await chat_service.search_messages(
        db, current_user.id, keyword, conversation_id, page, page_size
    )

@router.post("/consult", response_model=ConsultationResponse)
async def send_product_consultation(
    request: ProductConsultRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送商品咨询"""
    try:
        # 验证不能向自己咨询（为了测试方便，暂时注释掉）
        # if request.seller_id == current_user.id:
        #     raise HTTPException(status_code=400, detail="不能向自己发送咨询")
        
        # 发送咨询消息
        message = await chat_service.send_product_consultation(db, current_user.id, request)
        
        # 通过WebSocket通知卖家
        await websocket_manager.send_personal_message(
            request.seller_id,
            {
                "type": "new_consultation",
                "message": message.dict(),
                "product_id": request.product_id
            }
        )
        
        return ConsultationResponse(
            conversation_id=message.conversation_id,
            message_id=message.id,
            message="咨询消息发送成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/online-status/{user_id}")
async def get_user_online_status(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取用户在线状态"""
    is_online = websocket_manager.is_user_online(user_id)
    status = websocket_manager.get_user_status(user_id)
    return {
        "user_id": user_id,
        "is_online": is_online,
        "status": status
    }