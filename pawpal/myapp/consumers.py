# work/dsi202/pawpal/myapp/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User # หรือ get_user_model()
# from asgiref.sync import sync_to_async # ถ้าต้องการเรียกใช้ Django ORM แบบ sync ใน consumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.user = self.scope["user"] # ดึงข้อมูลผู้ใช้ที่ login อยู่ (ถ้ามีการตั้งค่า AuthMiddlewareStack)

        # === การจัดการกลุ่มแชท (Chat Room) แบบง่าย ===
        # ในตัวอย่างนี้ เราจะให้ทุกคนเชื่อมต่อเข้า "ห้อง" เดียวกันก่อน
        # ในระบบจริง อาจจะต้องมีตรรกะการสร้างห้องสำหรับ user-admin แต่ละคู่
        self.room_name = 'admin_chat' # ชื่อห้องกลางสำหรับ user คุยกับ admin
        self.room_group_name = f'chat_{self.room_name}'

        # เข้าร่วมกลุ่มห้องแชท
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept() # ยอมรับการเชื่อมต่อ WebSocket

        # # (Optional) แจ้งผู้ใช้คนอื่นในห้องว่ามีคนใหม่เข้ามา (ถ้าต้องการ)
        # if self.user.is_authenticated:
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'chat_message', # ชี้ไปที่ method chat_message ด้านล่าง
        #             'message': f'{self.user.username} has joined the chat.',
        #             'sender_username': 'System'
        #         }
        #     )

    async def disconnect(self, close_code):
        # # (Optional) แจ้งผู้ใช้คนอื่นในห้องว่ามีคนออกไป (ถ้าต้องการ)
        # if self.user.is_authenticated:
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'chat_message',
        #             'message': f'{self.user.username} has left the chat.',
        #             'sender_username': 'System'
        #         }
        #     )

        # ออกจากกลุ่มห้องแชท
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # รับข้อความจาก WebSocket (จาก Client)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        sender = self.scope.get("user", None) # ดึงผู้ใช้ที่ส่งข้อความ

        sender_username = "Anonymous"
        is_admin_sender = False
        if sender and sender.is_authenticated:
            sender_username = sender.username
            is_admin_sender = sender.is_staff # ตรวจสอบว่าเป็น admin หรือไม่

        # TODO: บันทึกข้อความลง Database (ถ้าต้องการ)
        # ควรทำแบบ Asynchronous หรือใช้ sync_to_async ถ้ามีการเรียก ORM
        # await self.save_message(sender, message_content, is_admin_sender)

        # ส่งข้อความไปยังกลุ่มห้องแชท
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # ชี้ไปที่ method chat_message ด้านล่าง
                'message': message_content,
                'sender_username': sender_username,
                'is_admin': is_admin_sender
            }
        )

    # รับข้อความจากกลุ่มห้องแชท และส่งต่อไปยัง WebSocket (ไปยัง Client)
    async def chat_message(self, event):
        message = event['message']
        sender_username = event.get('sender_username', 'Unknown')
        is_admin = event.get('is_admin', False)

        # ส่งข้อความไปยัง WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username,
            'is_admin': is_admin
            # สามารถเพิ่มข้อมูลอื่นๆ เช่น timestamp ได้
        }))

    # # (Optional) ตัวอย่างฟังก์ชันสำหรับบันทึกข้อความลง Database (ต้องสร้าง Model ก่อน)
    # @sync_to_async
    # def save_message(self, sender, message_content, is_admin_sender):
    #     from .models import ChatMessage # สมมติว่ามี Model ชื่อ ChatMessage
    #     ChatMessage.objects.create(
    #         sender=sender if sender and sender.is_authenticated else None,
    #         content=message_content,
    #         is_admin_message=is_admin_sender
    #     )