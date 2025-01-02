from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# 配置 PostgreSQL 連接
db = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="1234",  # 這裡填入你的 PostgreSQL 密碼
    database="violations_db"
)

@app.route('/')
def index():
    return render_template('identify.html')

@app.route('/violation', methods=['GET', 'POST'])
def violation():
    if request.method == 'POST':
        license_plate = request.form.get('license_plate')
        car_type = request.form.get('car')
        violation_reason = request.form.get('violation_reason')
        violation_result = request.form.get('violation')
        reason = request.form.get('reason')

        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO violation_people (license_plate, car_type, violation_reason, violation_result, reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (license_plate, car_type, violation_reason, violation_result, reason))
        db.commit()
        cursor.close()

        return jsonify(success=True)
    return render_template('violation.html')

if __name__ == '__main__':
    app.run(debug=True)
