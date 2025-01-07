from flask import Flask, request, render_template, jsonify
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

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

@app.route('/')
def index():
    license_plate = request.args.get('license_plate', 'AAA-1234')
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # 車主資料
        cursor.execute('SELECT * FROM vehicle_owner_info WHERE license_plate=%s', (license_plate,))
        person_data_row = cursor.fetchone()
        
        if person_data_row:
            # 依你表格欄位順序對應
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
        
        # 只抓 violation_records 裡最新一筆
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

@app.route('/generate_fine', methods=['POST'])
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
        # 新增一筆
        cursor.execute('''
            INSERT INTO violation_records (license_plate, owner_name, date, location, description, fine_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (license_plate, owner_name, date, location, description, fine_amount))
        conn.commit()
        cursor.close()
        conn.close()

        # 產生PDF
        file_name = generate_pdf(license_plate, owner_name, date, location, description, fine_amount)
        
        # 在Windows自動開啟
        if os.name == 'nt':
            os.startfile(file_name)

        return jsonify(success=True, file_name=file_name)
    else:
        return jsonify(success=False, message="連線資料庫失敗")

def generate_pdf(plate, owner, date, loc, desc, fine):
    file_name = f"{plate}_violation_ticket.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    c.drawString(100, 750, f"License Plate: {plate}")
    c.drawString(100, 730, f"Owner Name: {owner}")
    c.drawString(100, 710, f"Date: {date}")
    c.drawString(100, 690, f"Location: {loc}")
    c.drawString(100, 670, f"Description: {desc}")
    c.drawString(100, 650, f"Fine Amount: {fine}")
    c.showPage()
    c.save()
    print(f"PDF 生成: {file_name}")
    return file_name

if __name__ == '__main__':
    app.run(debug=True)