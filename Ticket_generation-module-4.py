from flask import Flask, jsonify, request
import pyqrcode
from io import BytesIO
import pyodbc

app = Flask(__name__)

# AWS RDS SQL Server configuration
server = 'your_server_endpoint'
database = 'your_database_name'
username = 'your_username'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'

# Minimum balance required for ticket generation
min_balance_required = 5.0

def check_balance(user_serial_no):
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()

        cursor.execute(f"SELECT balance FROM transit_1 WHERE serial_no = ?", user_serial_no)
        row = cursor.fetchone()

        if row:
            balance = row[0]
            return balance

        return None  # User not found

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    user_serial_no = request.json.get('serial_no')

    balance = check_balance(user_serial_no)

    if balance is None:
        return jsonify({'error': 'User not found'}), 404

    if balance >= min_balance_required:
        # Generate QR code with user's details
        qr_data = f"Serial No: {user_serial_no}"
        qr = pyqrcode.create(qr_data)

        # Convert QR code to bytes
        qr_img = BytesIO()
        qr.png(qr_img, scale=8)
        qr_img.seek(0)

        return jsonify({'qr_code': qr_img.getvalue().decode('ISO-8859-1')}), 200
    else:
        return jsonify({'error': 'Insufficient balance to generate ticket'}), 403

if __name__ == '__main__':
    app.run(debug=True)
