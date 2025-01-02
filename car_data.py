from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# 連接到PostgreSQL資料庫
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1234",  # 這裡填入你的 PostgreSQL 密碼
        database='violations_db'
    )
    return conn

@app.route('/')
def index():
    vehicle_number = request.args.get('vehicle_number', 'AAA-1234')
    
    # 從資料庫檢索資料
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 改正查詢資料表名稱
    cursor.execute('SELECT * FROM vehicle_owner_info WHERE license_plate = %s', (vehicle_number,))
    person_data = cursor.fetchone()
    
    cursor.execute('SELECT * FROM violation_records WHERE vehicle_number = %s', (vehicle_number,))
    violation_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('car_data.html', person_data=person_data, violation_data=violation_data, vehicle_number=vehicle_number)

if __name__ == '__main__':
    app.run(debug=True)
