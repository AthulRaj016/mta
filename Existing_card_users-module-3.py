from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)

# Replace these with your RDS database connection details
rds_endpoint = 'your_rds_endpoint'
rds_database = 'your_database_name'
rds_username = 'your_username'
rds_password = 'your_password'

# Establish a connection to SQL Server
conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rds_endpoint};DATABASE={rds_database};UID={rds_username};PWD={rds_password}')

@app.route('/validate_and_fetch', methods=['POST'])
def validate_and_fetch():
    data = request.json
    serial_no = data.get('serial_no')
    transit_name = data.get('transit_name')

    # Validation query to check if the provided details exist
    validation_query = "SELECT * FROM transit_1 WHERE serial_no = ? AND transit_name = ?"

    cursor = conn.cursor()
    cursor.execute(validation_query, (serial_no, transit_name))
    transit = cursor.fetchone()

    if transit:
        # If details are valid, fetch data for the given serial number and transit name
        fetch_query = "SELECT * FROM transit_1 WHERE serial_no = ? AND transit_name = ?"
        cursor.execute(fetch_query, (serial_no, transit_name))
        fetched_data = cursor.fetchone()

        if fetched_data:
            # Process the fetched data and return it as JSON
            transit_data = {
                'serial_no': fetched_data[0],
                'transit_name': fetched_data[1],
                'balance': fetched_data[2],
                'monthly_pass': bool(fetched_data[3]),
                'expiry': str(fetched_data[4]) if fetched_data[4] else None
            }
            return jsonify(transit_data), 200
        else:
            return jsonify({'error': 'Data not found'}), 404
    else:
        return jsonify({'error': 'Transit details are not valid'}), 400

if __name__ == '__main__':
    app.run(debug=True)
