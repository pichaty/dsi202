# work/dsi202/pawpal/myapp/quiz_data.py (สร้างไฟล์ใหม่)

QUIZ_DATA = [
    {
        'id': 1,
        'text': "คืนวันศุกร์ในอุดมคติของคุณคือ?",
        'answers': [
            {'text': "ปาร์ตี้ใหญ่กับเพื่อนๆ", 'tags': ['Dog', 'Energetic', 'Social']},
            {'text': "นอนขดตัวอ่านหนังสือ/ดูหนังดีๆ", 'tags': ['Cat', 'Calm', 'Independent']},
            {'text': "ดินเนอร์เงียบๆ กับเพื่อนสนิท", 'tags': ['Dog', 'Calm', 'Social', 'Cat']}, # อาจมีได้หลาย tag
            {'text': "ลองหากิจกรรมผจญภัยใหม่ๆ", 'tags': ['Dog', 'Energetic']},
        ]
    },
    {
        'id': 2,
        'text': "เวลาเจอคนใหม่ๆ คุณมักจะ:",
        'answers': [
            {'text': "ตื่นเต้นและกระตือรือร้นที่จะคุย", 'tags': ['Dog', 'Social', 'Energetic']},
            {'text': "ช่างสังเกตและสงวนท่าทีเล็กน้อยในตอนแรก", 'tags': ['Cat', 'Calm', 'Independent']},
            {'text': "เป็นมิตร แต่ชอบกลุ่มเล็กๆ มากกว่า", 'tags': ['Dog', 'Calm', 'Social', 'Cat']},
            {'text': "ระมัดระวังและใช้เวลาในการเปิดใจ", 'tags': ['Cat', 'Independent']},
        ]
    },
    {
        'id': 3,
        'text': "คุณรู้สึกอย่างไรกับการกอด?",
        'answers': [
            {'text': "ชอบมาก! กอดได้ตลอดเวลา", 'tags': ['Dog', 'Affectionate', 'Social']},
            {'text': "แล้วแต่อารมณ์และตามใจฉัน", 'tags': ['Cat', 'Independent']},
            {'text': "ชอบเป็นบางครั้ง แต่ก็ต้องการพื้นที่ส่วนตัว", 'tags': ['Dog', 'Independent', 'Cat', 'Affectionate']},
            {'text': "ไม่ค่อยชอบเท่าไหร่", 'tags': ['Cat', 'Independent']},
        ]
    },
    # --- เพิ่มคำถาม 4-10 ที่นี่ในรูปแบบเดียวกัน ---
    {
        'id': 4,
        'text': "ระดับพลังงานโดยทั่วไปของคุณ:",
        'answers': [
            {'text': "สูง! พร้อมลุยเสมอ", 'tags': ['Energetic', 'Dog']},
            {'text': "ปานกลาง มีช่วงคึกคักสลับกับพักผ่อน", 'tags': ['Energetic', 'Calm']},
            {'text': "ค่อนข้างผ่อนคลายและสงบ", 'tags': ['Calm', 'Cat']},
            {'text': "เหมือนเป็นผู้เชี่ยวชาญด้านการงีบ", 'tags': ['Calm', 'Cat']},
        ]
    },
    {
        'id': 5,
        'text': "สภาพแวดล้อมในบ้านที่คุณชอบคือ?",
        'answers': [
            {'text': "กว้างขวาง มีพื้นที่ให้วิ่งเล่น", 'tags': ['Dog', 'Energetic', 'Large','friendly']},
            {'text': "อบอุ่น สบาย อาจมีมุมรับแดด", 'tags': ['Cat', 'Calm']},
            {'text': "เป็นระเบียบเรียบร้อย", 'tags': ['Cat']},
            {'text': "ไม่สำคัญ ตราบใดที่มีคนที่รักอยู่ด้วย", 'tags': ['Dog', 'Social', 'Affectionate']},
        ]
    },
     {
        'id': 6,
        'text': "คุณรับมือกับปัญหาอย่างไร?",
        'answers': [
            {'text': "เผชิญหน้าตรงๆ อาจจะเสียงดังบ้างเล็กน้อย", 'tags': ['Dog', 'Energetic']},
            {'text': "วิเคราะห์อย่างรอบคอบก่อนตัดสินใจ", 'tags': ['Cat', 'Independent']},
            {'text': "ขอความช่วยเหลือหรือการสนับสนุนจากเพื่อน", 'tags': ['Dog', 'Social']},
            {'text': "หาที่เงียบๆ เพื่อคิดทบทวน", 'tags': ['Cat', 'Calm', 'Independent']},
        ]
    },
    {
        'id': 7,
        'text': "วิธีการเล่นที่คุณชอบที่สุด?",
        'answers': [
            {'text': "วิ่งเล่น เกมที่ต้องเคลื่อนไหว", 'tags': ['Dog', 'Energetic']},
            {'text': "ของเล่นลับสมอง เกมวางแผน หรือฝึกซุ่มโจมตี", 'tags': ['Cat', 'Independent']},
            {'text': "เล่นเบาๆ และมีปฏิสัมพันธ์กัน", 'tags': ['Calm', 'Social','friendly']},
            {'text': "แค่ดูคนอื่นเล่นก็พอใจแล้ว", 'tags': ['Calm', 'Cat']},
        ]
    },
    {
        'id': 8,
        'text': "คุณรักอิสระแค่ไหน?",
        'answers': [
            {'text': "มาก - ชอบทำอะไรด้วยตัวเอง", 'tags': ['Cat', 'Independent']},
            {'text': "ค่อนข้าง - ให้ความสำคัญกับเวลาส่วนตัว แต่ก็ชอบมีเพื่อน", 'tags': ['Dog', 'Independent', 'Cat', 'Social']},
            {'text': "ไม่มาก - ชอบอยู่กับคนอื่นมากกว่า", 'tags': ['Dog', 'Social', 'Affectionate','friendly']},
        ]
    },
    {
        'id': 9,
        'text': "อะไรฟังดูน่าดึงดูดใจกว่า?",
        'answers': [
            {'text': "เดินเล่นยาวๆ ในสวนสาธารณะ", 'tags': ['Dog', 'Energetic']},
            {'text': "งีบหลับอุ่นๆ ในที่ที่มีแดดส่อง", 'tags': ['Cat', 'Calm']},
            {'text': "เรียนรู้เทคนิคหรือทักษะใหม่ๆ", 'tags': ['Dog']},
            {'text': "สำรวจมุมที่ซ่อนอยู่", 'tags': ['Cat', 'Independent']},
        ]
    },
    {
        'id': 10,
        'text': "เพื่อนคู่ใจในอุดมคติของคุณคือคนแบบไหน?",
        'answers': [
            {'text': "พร้อมสำหรับการผจญภัยเสมอ", 'tags': ['Dog', 'Energetic']},
            {'text': "เคารพความต้องการพื้นที่ส่วนตัวของคุณ", 'tags': ['Cat', 'Independent']},
            {'text': "ซื่อสัตย์และอยู่เคียงข้างคุณเสมอ", 'tags': ['Dog', 'Affectionate']},
            {'text': "สงบและอ่อนโยน", 'tags': ['Cat', 'Calm']},
        ]
    }
]

# Mapping ระหว่าง tag กับฟิลด์ใน Pet model (ตัวอย่าง)
TAG_TO_PET_FILTER = {
    'Dog': {'pet_type': 'Dog'}, # ใช้ pet_type แทน species
    'Cat': {'pet_type': 'Cat'}, # ใช้ pet_type แทน species
    # ใช้ icontains ค้นหาใน personality field (TextField)
    # อาจต้องปรับ keyword ให้ตรงกับข้อมูลใน database ของคุณ
    'Energetic': {'personality__icontains': 'energetic''playful' 'active'}, # หรือ 'playful', 'active', 'ร่าเริง', 'พลังเยอะ'
    'Calm': {'personality__icontains': 'calm' 'relaxed'},        # หรือ 'quiet', 'relaxed', 'สงบ', 'เรียบร้อย'
    'Social': {'personality__icontains': 'social' 'friendly' 'sociable'},      # หรือ 'friendly', 'sociable', 'เข้ากับคนง่าย', 'เข้ากับสัตว์อื่นง่าย'
    'Independent': {'personality__icontains': 'independent'},# หรือ 'alone', 'สันโดษ'
    'Affectionate': {'personality__icontains': 'affectionate''loving'},# หรือ 'cuddly', 'loving', 'ขี้อ้อน'
    # ไม่มีฟิลด์ size โดยตรง อาจจะ map ยาก หรือ map กับ age/breed ถ้าเป็นไปได้
    'Large': {}, # อาจจะปล่อยว่าง หรือลอง map กับ breed ที่มักจะตัวใหญ่
    'Small': {}, # อาจจะปล่อยว่าง หรือลอง map กับ breed ที่มักจะตัวเล็ก หรือ age='Puppy'/'Kitten'
}