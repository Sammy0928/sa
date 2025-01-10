from flask import Flask, request, render_template, jsonify, Blueprint
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
import os

# 註冊中文字型
pdfmetrics.registerFont(TTFont('MingLiu', 'C:/Users/user/Documents/GitHub/sa/SA/mingliu.ttf'))

# 建立 Flask 應用程式
app = Flask(__name__)
invoice_bp = Blueprint('invoice', __name__, template_folder='templates')

# 資料庫連線函式
def get_db_connection():
    try:
        return psycopg2.connect(
            host="localhost",
            user="postgres",
            password="1234",
            database="violations_db"
        )
    except Exception as e:
        print(f"資料庫連線失敗: {e}")
        return None

# 首頁路由
@invoice_bp.route('/')
def index():
    license_plate = request.args.get('license_plate', 'AAA-1234')
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # 查詢車主資料
        cursor.execute('SELECT * FROM vehicle_owner_info WHERE license_plate=%s', (license_plate,))
        person_data_row = cursor.fetchone()
        
        if person_data_row:
            person_data = {
                'license_plate': person_data_row[0],
                'owner_name':    person_data_row[1],
                'phone':         person_data_row[2],
                'gender':        person_data_row[3],
                'birth_date':    person_data_row[4],
                'address':       person_data_row[5],
                'registration_date': person_data_row[6],
                'photo_url':     person_data_row[7]
            }
        else:
            person_data = None
        
        # 查詢最新一筆違規資料
        cursor.execute('''
            SELECT *
            FROM violation_records
            WHERE license_plate = %s
            ORDER BY date DESC
            LIMIT 1
        ''', (license_plate,))
        row = cursor.fetchone()
        
        if row:
            violation_data = {
                'date': row[3],
                'location': row[4],
                'description': row[5],
                'fine_amount': row[6]
            }
        else:
            violation_data = None
        
        cursor.close()
        conn.close()
    else:
        person_data = None
        violation_data = None

    return render_template('invoice.html',
                           license_plate=license_plate,
                           person_data=person_data,
                           violation_data=violation_data)

# 生成 PDF 路由
@invoice_bp.route('/generate_fine', methods=['POST'])
def generate_fine():
    license_plate = request.form.get('license_plate')
    owner_name    = request.form.get('owner_name')
    date          = request.form.get('date')
    location      = request.form.get('location')
    description   = request.form.get('description')
    fine_amount   = request.form.get('fine_amount')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # 新增違規紀錄
        cursor.execute('''
            INSERT INTO violation_records (license_plate, owner_name, date, location, description, fine_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (license_plate, owner_name, date, location, description, fine_amount))
        conn.commit()
        cursor.close()
        conn.close()

        # 產生 PDF
        file_name = generate_pdf(license_plate, owner_name, date, location, description, fine_amount)
        
        # 在 Windows 自動開啟 PDF
        if os.name == 'nt':
            os.startfile(file_name)

        return jsonify(success=True, file_name=file_name)
    else:
        return jsonify(success=False, message="連線資料庫失敗")

# PDF 生成函式
def generate_pdf(plate, owner, date, loc, desc, fine):
    file_name = f"{plate}_violation_ticket.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter  # 頁面尺寸：612 x 792 points

    # 設定背景顏色
    c.setFillColor(HexColor("#f8c9dd"))
    c.rect(0, 0, width, height, fill=True)

    # 恢復文字顏色
    c.setFillColor(HexColor("#000000"))

    # 添加標題
    c.setFont("MingLiu", 20)
    c.drawCentredString(width / 2, height - 50, "台北市政府警察局")
    c.setFont("MingLiu", 18)
    c.drawCentredString(width / 2, height - 80, "違反道路交通管理事件通知單")
    c.setFont("MingLiu", 14)
    c.drawCentredString(width / 2, height - 100, "（本聯繳款憑證執行）")

    # 添加車主與違規資訊
    c.setFont("MingLiu", 12)
    c.drawString(60, height - 140, f"車牌號碼：{plate}")
    c.drawString(60, height - 170, f"車主姓名：{owner}")
    c.drawString(60, height - 200, f"違規日期：{date}")
    c.drawString(60, height - 230, f"違規地點：{loc}")
    c.drawString(60, height - 260, f"違規事項：{desc}")
    c.drawString(60, height - 290, f"罰款金額：{fine}")

    # 添加違規照片框
    photo_path = "C:/Users/user/Documents/GitHub/sa/SA/A01.jpg"  # 替換為實際照片路徑
    c.drawImage(photo_path, 300, height - 400, width=200, height=120, mask='auto')

    # 注意事項
    c.setFont("MingLiu", 12)  # 調整字體大小
    c.drawString(60, height - 330, "注意事項：")
    c.setFont("MingLiu", 10)
    c.drawString(70, height - 360, "1. 本單為繳款憑證，請攜帶至指定單位繳費。")
    c.drawString(70, height - 380, "2. 如需申訴，請於期限內依規定提出申訴書。")
    c.drawString(70, height - 400, "3. 若未於期限內繳納罰款，將依法處理。")

    # 底部簽章區域
    c.setFont("MingLiu", 12)
    c.drawString(60, height - 480, "填單人：")
    c.drawString(400, height - 480, "職務章：")
    c.rect(390, height - 500, 120, 30)  # 職務章框位置調整

    # 模擬印章（置於最上層）
    stamp_path = "C:/Users/user/Documents/GitHub/sa/SA/第拾壹組.png"  # 替換為實際印章路徑
    c.drawImage(stamp_path, width - 150, height - 180, width=100, height=100, mask='auto')

    # 保存 PDF
    c.save()
    print(f"PDF 已生成: {file_name}")
    return file_name

if __name__ == '__main__':
    app.run(debug=True)
