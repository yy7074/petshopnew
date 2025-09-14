#!/usr/bin/env python3
"""
初始化消息演示数据
"""

import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import User, SystemNotification, UserNotification, Conversation, Message
from datetime import datetime, timedelta
import random

def create_demo_data():
    """创建演示数据"""
    db: Session = SessionLocal()
    
    try:
        print("开始创建消息演示数据...")
        
        # 获取现有用户
        users = db.query(User).limit(5).all()
        if len(users) < 2:
            print("需要至少2个用户才能创建消息数据")
            return
        
        print(f"找到 {len(users)} 个用户")
        
        # 创建系统通知
        notifications_data = [
            {
                "title": "欢迎使用拍宠有道",
                "content": "欢迎来到拍宠有道！在这里您可以参与宠物拍卖，发现心仪的宠物。",
                "notification_type": "system",
                "target_type": "all",
                "priority": 1,
            },
            {
                "title": "新品上架通知",
                "content": "有新的精品宠物上架了，快来看看吧！限时拍卖，机会难得。",
                "notification_type": "auction",
                "target_type": "all",
                "priority": 2,
            },
            {
                "title": "拍卖即将结束",
                "content": "您关注的拍品即将结束，请抓紧时间出价！",
                "notification_type": "auction",
                "target_type": "user",
                "target_ids": [users[0].id] if users else [],
                "priority": 3,
            },
            {
                "title": "订单支付提醒",
                "content": "您有一笔订单待支付，请及时完成支付以免订单被取消。",
                "notification_type": "payment",
                "target_type": "user", 
                "target_ids": [users[1].id] if len(users) > 1 else [],
                "priority": 2,
            },
            {
                "title": "订单发货通知",
                "content": "您的订单已发货，预计3-5个工作日内送达，请注意查收。",
                "notification_type": "order",
                "target_type": "user",
                "target_ids": [users[0].id] if users else [],
                "priority": 1,
            }
        ]
        
        created_notifications = []
        for notif_data in notifications_data:
            notification = SystemNotification(**notif_data)
            db.add(notification)
            db.flush()  # 获取ID
            created_notifications.append(notification)
            print(f"创建系统通知: {notification.title}")
        
        # 为用户创建通知记录
        for notification in created_notifications:
            if notification.target_type == "all":
                # 为所有用户创建通知
                for user in users:
                    user_notification = UserNotification(
                        user_id=user.id,
                        notification_id=notification.id,
                        is_read=random.choice([True, False])  # 随机已读状态
                    )
                    db.add(user_notification)
            elif notification.target_type == "user" and notification.target_ids:
                # 为指定用户创建通知
                for user_id in notification.target_ids:
                    user_notification = UserNotification(
                        user_id=user_id,
                        notification_id=notification.id,
                        is_read=random.choice([True, False])
                    )
                    db.add(user_notification)
        
        # 创建对话和消息
        if len(users) >= 2:
            # 创建几个对话
            conversations_data = [
                (users[0].id, users[1].id),
                (users[0].id, users[2].id) if len(users) > 2 else (users[0].id, users[1].id),
                (users[1].id, users[2].id) if len(users) > 2 else (users[0].id, users[1].id),
            ]
            
            for user1_id, user2_id in conversations_data:
                if user1_id == user2_id:
                    continue
                    
                # 检查对话是否已存在
                existing_conv = db.query(Conversation).filter(
                    ((Conversation.user1_id == user1_id) & (Conversation.user2_id == user2_id)) |
                    ((Conversation.user1_id == user2_id) & (Conversation.user2_id == user1_id))
                ).first()
                
                if existing_conv:
                    continue
                
                conversation = Conversation(
                    user1_id=min(user1_id, user2_id),
                    user2_id=max(user1_id, user2_id),
                    last_message_time=datetime.now() - timedelta(hours=random.randint(1, 24))
                )
                db.add(conversation)
                db.flush()
                
                print(f"创建对话: 用户{user1_id} <-> 用户{user2_id}")
                
                # 为对话创建一些消息
                messages_content = [
                    "你好，这个宠物还在吗？",
                    "在的，您感兴趣的话可以来看看",
                    "好的，什么时候方便？",
                    "明天下午怎么样？",
                    "可以的，地址发给我一下",
                    "好的，稍等我发给您"
                ]
                
                message_count = random.randint(3, len(messages_content))
                for i in range(message_count):
                    # 交替发送者
                    sender_id = user1_id if i % 2 == 0 else user2_id
                    receiver_id = user2_id if i % 2 == 0 else user1_id
                    
                    message = Message(
                        conversation_id=conversation.id,
                        sender_id=sender_id,
                        receiver_id=receiver_id,
                        content=messages_content[i],
                        message_type="text",
                        is_read=random.choice([True, False]),
                        created_at=datetime.now() - timedelta(hours=random.randint(0, 12))
                    )
                    db.add(message)
                    
                    # 更新对话的最后消息
                    if i == message_count - 1:
                        conversation.last_message_id = message.id
                        conversation.last_message_time = message.created_at
                        
                        # 更新未读计数
                        if not message.is_read:
                            if message.receiver_id == conversation.user1_id:
                                conversation.user1_unread_count += 1
                            else:
                                conversation.user2_unread_count += 1
        
        # 提交所有更改
        db.commit()
        print("消息演示数据创建完成！")
        
        # 显示统计信息
        notification_count = db.query(SystemNotification).count()
        user_notification_count = db.query(UserNotification).count()
        conversation_count = db.query(Conversation).count()
        message_count = db.query(Message).count()
        
        print(f"统计信息:")
        print(f"- 系统通知: {notification_count}")
        print(f"- 用户通知记录: {user_notification_count}")
        print(f"- 对话: {conversation_count}")
        print(f"- 消息: {message_count}")
        
    except Exception as e:
        print(f"创建演示数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
