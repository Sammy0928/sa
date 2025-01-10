from flask import Blueprint, render_template, request, jsonify
import psycopg2
from psycopg2 import pool

# 創建藍圖
identify_bp = Blueprint('identify', __name__, template_folder='templates')

# 配置 PostgreSQL 連接池
db_pool = pool.SimpleConnectionPool(
    1, 20,  # 最小和最大連接數
    host="localhost",
    user="postgres",
    password="1234",  # 替換為你的 PostgreSQL 密碼
    database="violations_db"
)

@identify_bp.route('/')
def index():
    """渲染首頁"""
    return render_template('identify.html')

@identify_bp.route('/violation', methods=['GET', 'POST'])
def violation():
    if request.method == 'POST':
        try:
            # 获取表单数据
            license_plate = request.form.get('license_plate')
            car_type = request.form.get('car')
            violation_reason = request.form.get('violation_reason')
            violation_result = request.form.get('violation')
            reason = request.form.get('reason')
            reviewer_signature = request.form.get('reviewer_signature')

            # 验证必要字段
            if not license_plate or not car_type:
                return jsonify(success=False, error="車牌號和車輛類型是必填項目"), 400

            # 数据库操作
            conn = db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO violation_people (license_plate, car_type, violation_reason, violation_result, reason, reviewer_signature)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (license_plate, car_type, violation_reason, violation_result, reason, reviewer_signature))
            conn.commit()
            return jsonify(success=True, message="資料已成功提交！")
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            return jsonify(success=False, error=f"資料提交失敗: {str(e)}"), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                db_pool.putconn(conn)

    # 如果是 GET 请求，渲染 HTML 页面
    return render_template('violation.html')


@identify_bp.route('/data', methods=['GET'])
def get_data():
    """查詢資料並返回 JSON 格式"""
    change = int(request.args.get('change', 0))
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM violation_people OFFSET %s LIMIT 1", (change,))
        record = cursor.fetchone()
        if not record:
            return jsonify(error="No data found"), 404

        # 假設資料庫欄位順序與以下字段對應
        data = {
            "license_plate": record[0],
            "car_type": record[1],
            "violation_reason": record[2],
            "violation": record[3],
            "reason": record[4],
            "reviewer_signature": record[5],
        }
        return jsonify(data)
    except psycopg2.Error as e:
        return jsonify(error=str(e)), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            db_pool.putconn(conn)
