from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)

# Database Configuration
db_config = {
    'Driver': '{ODBC Driver 17 for SQL Server}',  # Ensure this driver is installed
    'Server': 'ANSHAD',
    'Database': 'bikes',
    'Trusted_Connection': 'yes'
}

def get_db_connection():
    """Establish and return a database connection."""
    conn_str = (
        f"Driver={db_config['Driver']};"
        f"Server={db_config['Server']};"
        f"Database={db_config['Database']};"
        f"Trusted_Connection={db_config['Trusted_Connection']};"
    )
    return pyodbc.connect(conn_str)

# Route to fetch products
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch products
        query = "SELECT * FROM products"
        cursor.execute(query)

        # Convert result to list of dictionaries
        columns = [column[0] for column in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return jsonify({'status': 'success', 'data': products}), 200
    except pyodbc.Error as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
