from flask import Flask, request, render_template, jsonify, Blueprint
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
index_bp = Blueprint('index', __name__, template_folder='templates')
# 配置 PostgreSQL 数据库连接信息
DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "1234",  # 替换为你的 PostgreSQL 密码
    "database": "violations_db"
}

# 获取数据库连接
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return None
@app.route('/process_image', methods=['POST'])
def process_image():
    # 模拟车牌识别逻辑
    license_plate = "9692M3"  # 模拟车牌识别结果
    print(f"识别的车牌号: {license_plate}")  # 打印日志
    return jsonify({'plate': license_plate})

@app.route('/vehicle_owner_info', methods=['GET'])
def get_vehicle_owner_info():
    license_plate = request.args.get('license_plate')
    print(f"收到的车牌号: {license_plate}")  # 打印接收到的车牌号

    if not license_plate:
        return jsonify({'error': 'License plate not provided'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 查询车主资料
        cursor.execute("SELECT * FROM vehicle_owner_info WHERE license_plate = %s", (license_plate,))
        person_data = cursor.fetchone()
        print(f"车主数据: {person_data}")  # 打印查询到的车主数据

        # 查询违章记录
        cursor.execute("SELECT * FROM violation_records WHERE license_plate = %s", (license_plate,))
        violation_data = cursor.fetchall()
        print(f"违章记录: {violation_data}")  # 打印查询到的违章记录

        return jsonify({
            'person_data': person_data,
            'violation_data': violation_data
        })
    except Exception as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'error': 'Failed to retrieve data'}), 500
    finally:
        cursor.close()
        conn.close()



    