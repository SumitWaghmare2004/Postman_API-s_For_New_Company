#========================================================= CORRECT CV2 FOR AFD ============================================================================================


# POST = http://localhost:5002/company_id=241687975/resource_id=4433/employee

# GET , PUT , DELETE  = http://localhost:5002/company_id=241687975/resource_id=4433/employee_id=2198

# Format :- 

# {
#   "employee_name": "John Doe",
#   "designation": "Software Engineer",
#   "image_source": "C:/Users/umred/OneDrive/Desktop/Badak.jpg"
# }

#====================================================================================================================================================


import mysql.connector
import cv2
import numpy as np
import requests
from flask import Flask, jsonify, request
from PIL import Image
from io import BytesIO
import os
import random
import string

app = Flask(__name__)

# Connect to MySQL server (adjust host, user, and password as needed)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="API_Database"
    )

# Helper function to generate random employee ID (integer)
def generate_employee_id():
    return random.randint(1000, 9999)

# Helper function to generate a random 10-bit alphanumeric face_group_id
def generate_face_group_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Helper function to check if company and resource are valid and retrieve data
def check_company_and_resource(company_id, resource_id, cursor):
    query = """
    SELECT c.Company_id, c.Company_Name, r.Resource_id, r.Resource_Name 
    FROM Company_Data AS c 
    JOIN Resource_Data AS r ON c.Company_id = %s AND r.Resource_id = %s
    """
    cursor.execute(query, (company_id, resource_id))
    return cursor.fetchone()

# Function to extract face coordinates from an image using OpenCV
def extract_face_coordinates(image):
    # Convert image to grayscale (OpenCV needs grayscale for face detection)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) > 0:
        # Return the first detected face's boundary
        (x, y, w, h) = faces[0]
        face_coordinates = {
            "face_boundary": [int(x), int(y), int(w), int(h)]
        }
        return face_coordinates
    else:
        return None

# Helper function to read image from URL or file path
def read_image(image_source):
    if image_source.startswith(('http://', 'https://')):
        response = requests.get(image_source)
        img = Image.open(BytesIO(response.content))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # Convert to OpenCV BGR format
    else:
        # Handle local file system path
        if os.path.exists(image_source):
            image = cv2.imread(image_source)
            if image is not None:
                return image
        return None

# 1. Add a new employee with image processing (POST)
@app.route('/company_id=<int:company_id>/resource_id=<int:resource_id>/employee', methods=['POST'])
def add_employee(company_id, resource_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company and resource are valid
    company_resource = check_company_and_resource(company_id, resource_id, cursor)
    if not company_resource:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or resource ID'}), 403

    # Get employee data from request
    data = request.json if request.is_json else request.form
    employee_name = data.get('employee_name')
    designation = data.get('designation')
    image_source = data.get('image_source')

    if not (employee_name and designation and image_source):
        return jsonify({'message': 'All fields (employee_name, designation, image_source) are required'}), 400

    # Generate random employee ID and face_group_id
    employee_id = generate_employee_id()
    face_group_id = generate_face_group_id()

    # Read image from provided source
    image = read_image(image_source)
    if image is None:
        return jsonify({'message': 'Invalid image source or unsupported image format'}), 400

    # Extract face coordinates
    try:
        face_coordinates = extract_face_coordinates(image)
    except Exception as e:
        return jsonify({'message': f'Image processing error: {str(e)}'}), 500

    if not face_coordinates:
        return jsonify({'message': 'Face detection failed. Please provide a valid image.'}), 400

    # Insert new employee into the Employee_Data table
    query = """
    INSERT INTO Employee_Data 
    (Employee_id, Employee_Name, Designation, Company_id, Company_Name, Resource_id, Resource_Name) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        employee_id, 
        employee_name, 
        designation, 
        company_resource[0],  # Company_id
        company_resource[1],  # Company_Name
        company_resource[2],  # Resource_id
        company_resource[3]   # Resource_Name
    ))

    # Insert face coordinates into the Face_group table
    face_query = """
    INSERT INTO Face_group 
    (face_group_id, face_coordinates, company_id, resource_id) 
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(face_query, (
        face_group_id,
        str(face_coordinates),  # Convert dictionary to string for storage
        company_resource[0],  # Company_id
        company_resource[2]   # Resource_id
    ))

    conn.commit()

    response = {
        'employee_id': employee_id,
        'employee_name': employee_name,
        'designation': designation,
        'company_id': company_resource[0],
        'company_name': company_resource[1],
        'resource_id': company_resource[2],
        'resource_name': company_resource[3],
        'face_group_id': face_group_id,
        'face_coordinates': face_coordinates
    }

    cursor.close()
    conn.close()

    return jsonify(response), 201

# 2. Get employee details (GET)
@app.route('/company_id=<int:company_id>/resource_id=<int:resource_id>/employee_id=<int:employee_id>', methods=['GET'])
def get_employee(company_id, resource_id, employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company and resource are valid
    company_resource = check_company_and_resource(company_id, resource_id, cursor)
    if not company_resource:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or resource ID'}), 403

    query = """
    SELECT * FROM Employee_Data 
    WHERE Employee_id = %s AND Company_id = %s AND Resource_id = %s
    """
    cursor.execute(query, (employee_id, company_id, resource_id))
    employee = cursor.fetchone()

    cursor.close()
    conn.close()

    if employee:
        response = {
            'employee_id': employee[0],
            'employee_name': employee[1],
            'designation': employee[2],
            'company_id': employee[3],
            'company_name': employee[4],
            'resource_id': employee[5],
            'resource_name': employee[6]
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Employee not found'}), 404

# 3. Update employee details (PUT)
@app.route('/company_id=<int:company_id>/resource_id=<int:resource_id>/employee_id=<int:employee_id>', methods=['PUT'])
def update_employee(company_id, resource_id, employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company and resource are valid
    company_resource = check_company_and_resource(company_id, resource_id, cursor)
    if not company_resource:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or resource ID'}), 403

    # Get employee data from request
    data = request.json if request.is_json else request.form
    employee_name = data.get('employee_name')
    designation = data.get('designation')

    if not (employee_name or designation):
        return jsonify({'message': 'At least one field (employee_name or designation) must be provided'}), 400

    query = """
    UPDATE Employee_Data 
    SET Employee_Name = COALESCE(%s, Employee_Name), 
        Designation = COALESCE(%s, Designation) 
    WHERE Employee_id = %s AND Company_id = %s AND Resource_id = %s
    """
    cursor.execute(query, (employee_name, designation, employee_id, company_id, resource_id))
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Employee not found'}), 404

    cursor.close()
    conn.close()

    return jsonify({'message': 'Employee updated successfully'}), 200

# 4. Delete employee (DELETE)
@app.route('/company_id=<int:company_id>/resource_id=<int:resource_id>/employee_id=<int:employee_id>', methods=['DELETE'])
def delete_employee(company_id, resource_id, employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company and resource are valid
    company_resource = check_company_and_resource(company_id, resource_id, cursor)
    if not company_resource:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or resource ID'}), 403

    query = """
    DELETE FROM Employee_Data 
    WHERE Employee_id = %s AND Company_id = %s AND Resource_id = %s
    """
    cursor.execute(query, (employee_id, company_id, resource_id))
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Employee not found'}), 404

    cursor.close()
    conn.close()

    return jsonify({'message': 'Employee deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5002)


