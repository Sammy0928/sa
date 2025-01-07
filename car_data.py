from flask import Flask, request, render_template, jsonify, send_file
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

app = Flask(__name__)

# 配置 PostgreSQL 連接，請填入你的使用者名稱和密碼
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="1234",  # 這裡填入你的 PostgreSQL 密碼
            database="violations_db"
        )
        return conn
    except Exception as e:
        print(f"連接資料庫時發生錯誤：{e}")
        return None

@app.route('/')
def index():
    license_plate = request.args.get('license_plate', 'AAA-1234')
    
    # 從資料庫檢索資料
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        # 查詢 vehicle_owner_info 資料表
        cursor.execute('SELECT * FROM vehicle_owner_info WHERE license_plate = %s', (license_plate,))
        person_data = cursor.fetchone()

        # 查詢 violation_records 資料表
        cursor.execute('SELECT * FROM violation_records WHERE license_plate = %s', (license_plate,))
        violation_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 將查詢結果轉換為字典格式
        if person_data:
            person_data = {
                'license_plate': person_data[0],
                'owner_name': person_data[1],
                'phone': person_data[2],
                'gender': person_data[3],
                'birth_date': person_data[4],
                'address': person_data[5],
                'registration_date': person_data[6],
                'photo_url': person_data[7],
                'vehicle_model': person_data[8],
                'vehicle_color': person_data[9],
                'vehicle_brand': person_data[10]
                
            }
        
        # 將違規紀錄轉換為字典格式列表
        violation_data = [
            {
                'date': record[3],
                'location': record[4],
                'description': record[5],
                'fine_amount': record[6]
            }
            for record in violation_data
        ]
    else:
        person_data = None
        violation_data = []

    return render_template('car_data.html', person_data=person_data, violation_data=violation_data, license_plate=license_plate)

@app.route('/generate_fine', methods=['POST'])
def generate_fine():
    license_plate = request.form.get('license_plate')
    owner_name = request.form.get('owner_name')
    date = request.form.get('date')
    location = request.form.get('location')
    description = request.form.get('description')
    fine_amount = request.form.get('fine_amount')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO violation_records (license_plate, owner_name, date, location, description, fine_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (license_plate, owner_name, date, location, description, fine_amount))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Generate and save the PDF
        file_name = generate_pdf(license_plate, owner_name, date, location, description, fine_amount)
        
        # Automatically open the PDF
        os.startfile(file_name)
        
        return jsonify(success=True, file_name=file_name)
    else:
        return jsonify(success=False)

def generate_pdf(license_plate, owner_name, date, location, description, fine_amount):
    file_name = f"{license_plate}_violation_ticket.pdf"
    p = canvas.Canvas(file_name, pagesize=letter)
    p.drawString(100, 750, f"License Plate: {license_plate}")
    p.drawString(100, 730, f"Owner Name: {owner_name}")
    p.drawString(100, 710, f"Date: {date}")
    p.drawString(100, 690, f"Location: {location}")
    p.drawString(100, 670, f"Description: {description}")
    p.drawString(100, 650, f"Fine Amount: {fine_amount}")
    p.showPage()
    p.save()
    
    print(f"PDF 生成完成！檔案儲存為：{file_name}")
    return file_name

if __name__ == '__main__':
    app.run(debug=True)
