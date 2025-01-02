import os
import psycopg2
from flask import Flask, request, render_template, jsonify, send_from_directory
from fpdf import FPDF

app = Flask(__name__)

# 檢查並創建存放罰單的目錄
if not os.path.exists("tickets"):
    os.mkdir("tickets")

# 連接到 PostgreSQL 資料庫
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1234",  # 這裡填入你的 PostgreSQL 密碼
        dbname="violations_db"
    )

@app.route('/')
def index():
    return render_template('invoice.html')  # 導向 HTML 網頁檔案

@app.route('/vehicle-info', methods=['GET'])
def get_vehicle_info():
    license_plate = request.args.get('license_plate')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT description, fine_amount FROM violation_records WHERE license_plate = %s", (license_plate,))
    violations = cursor.fetchall()

    if violations:
        violations_list = []
        for violation in violations:
            violations_list.append({
                'description': violation[0],
                'fine_amount': violation[1]
            })
        cursor.close()
        conn.close()

        return jsonify({'license_plate': license_plate, 'violations': violations_list})
    else:
        cursor.close()
        conn.close()
        return jsonify({"error": "查無此車輛資料"}), 404

@app.route('/generate-ticket', methods=['POST'])
def generate_ticket():
    data = request.json
    license_plate = data.get("license_plate")
    owner_name = data.get("owner_name")
    description = data.get("description")
    fine_amount = data.get("fine_amount")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('msyh', '', 'msyh.ttf', uni=True)  # 使用支持中文的字體
    pdf.set_font('msyh', '', 12)

    pdf.cell(200, 10, txt="交通違規罰單", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(0, 10, f"車牌號碼: {license_plate}", ln=True)
    pdf.cell(0, 10, f"車主姓名: {owner_name}", ln=True)
    pdf.cell(0, 10, f"違規原因: {description}", ln=True)
    pdf.cell(0, 10, f"罰款金額: {fine_amount} 元", ln=True)

    # 保存 PDF 文件
    pdf_file = f"tickets/{license_plate}_ticket.pdf"
    pdf.output(pdf_file, dest='F')

    return jsonify({"message": "罰單生成成功", "pdf_file": pdf_file}), 200

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('tickets', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
