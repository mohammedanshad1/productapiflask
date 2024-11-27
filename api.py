from flask import Flask, jsonify, request
import pyodbc
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for SQL Server
db_config = {
    'Driver': '{ODBC Driver 17 for SQL Server}',
    'Server': 'ANSHAD',
    'Database': 'bikes',
    'Trusted_Connection': 'yes'
}

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    """Establish and return a database connection."""
    conn_str = (
        f"Driver={db_config['Driver']};"
        f"Server={db_config['Server']};"
        f"Database={db_config['Database']};"
        f"Trusted_Connection={db_config['Trusted_Connection']};"
    )
    return pyodbc.connect(conn_str)

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to insert a product with an image
@app.route('/api/products', methods=['POST'])
def add_product():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image file uploaded'}), 400

    image = request.files['image']
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')

    if not (name and price and description):
        return jsonify({'status': 'error', 'message': 'Missing product details'}), 400

    if image and allowed_file(image.filename):
        try:
            # Save the image to the uploads folder
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            # Save the product details and image path in the database
            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO products (name, price, description, image_path)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (name, price, description, image_path))
            conn.commit()

            return jsonify({'status': 'success', 'message': 'Product added successfully'}), 201
        except Exception as err:
            return jsonify({'status': 'error', 'message': str(err)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

# Route to fetch all products
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch products
        query = "SELECT id, name, price, description, image_path FROM products"
        cursor.execute(query)
        
        # Convert results to a list of dictionaries
        columns = [column[0] for column in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return jsonify({'status': 'success', 'data': products}), 200
    except pyodbc.Error as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
