from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import LoginForm # Import LoginForm ที่ถูกต้อง
import logging # Import a logging library

logger = logging.getLogger(__name__) # Create a logger instance

class DebugAccountAdapter(DefaultAccountAdapter):

    def get_login_form_class(self, request):
        # นี่คือ method ที่ allauth ใช้เพื่อเรียก LoginForm class
        # เราสามารถดักจับ form instance ที่นี่หลังจากมันถูกสร้างขึ้นได้
        # แต่การเข้าถึง instance โดยตรงใน method นี้อาจไม่ง่าย
        # วิธีที่ดีกว่าคือการ override view หรือ signal
        # อย่างไรก็ตาม เราสามารถ log ชื่อ form class ที่ถูกใช้ได้
        form_class = super().get_login_form_class(request)
        logger.debug(f"[DebugAdapter] Login form class being used: {form_class}")
        return form_class

    # คุณอาจจะ override method อื่นๆ ที่เกี่ยวข้องกับการสร้าง form
    # หรือการประมวลผล view ถ้าต้องการ debug เพิ่มเติม
    # เช่น get_form_kwargs, get_context_data ใน view ที่เกี่ยวข้อง

    # ตัวอย่างการดักจับ form ใน view ผ่าน adapter อาจจะไม่ตรงจุดนัก
    # แต่ถ้า allauth มี signal ที่ส่ง form instance เราสามารถใช้ signal receiver ได้
    # หรือวิธีที่ง่ายกว่าคือการ print field ของ form ใน template ด้วย loop ดังนี้:

    # เพิ่มโค้ดนี้ใน template login.html ชั่วคราว:
    # {% for field_name, field_object in form.fields.items %}
    #     <p>Field Name: {{ field_name }} | Widget: {{ field_object.widget }}</p>
    # {% endfor %}
    # {% for field in form %}
    # <p>Visible Field Name in form loop: {{ field.name }} | Label: {{ field.label }}</p>
    # {% endfor %}