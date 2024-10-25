#==========================================================================================================================================================================

#                                               CORRECT CODE CRUD ON THE 

# POST = http://localhost:5001/company_id=241687975/authorization_token=RpyAXo9-yBAXYj-PEMFJ-M52p5JcMUy
# GET , PUT , DELETE = http://localhost:5001/company_id=241687975/resource_id=4433?authorization_token=RpyAXo9-yBAXYj-PEMFJ-M52p5JcMUy


# Format_of_Json_raw :- 
        # {
        # "resource_name": "My New Resource"
        # }

#===================================================================================================================================================

from flask import Flask, jsonify, request
import mysql.connector
import random

app = Flask(__name__)

# Connect to MySQL server (adjust host, user, and password as needed)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Replace with your MySQL server host
        user="root",       # Replace with your MySQL user
        password="root",   # Replace with your MySQL password
        database="api_database"  # Use your API_Database
    )

# Helper function to generate random resource ID (integer)
def generate_resource_id():
    return random.randint(10000, 99999)

# Helper function to check company authorization
def check_company_authorization(company_id, auth_token, cursor):
    query = "SELECT * FROM company_data WHERE company_id = %s AND authorization_token = %s"
    cursor.execute(query, (company_id, auth_token))
    return cursor.fetchone()

# Helper function to find resource by ID in the database
def find_resource(resource_id, cursor):
    query = "SELECT * FROM resource_data WHERE resource_id = %s"
    cursor.execute(query, (resource_id,))
    return cursor.fetchone()

# 1. Add a new resource (POST)
@app.route('/company_id=<int:company_id>/authorization_token=<auth_token>', methods=['POST'])
def add_resource(company_id, auth_token):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company_id and auth_token are valid
    company = check_company_authorization(company_id, auth_token, cursor)
    if not company:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or authorization token'}), 403

    # Get resource data from request
    new_resource = request.json
    resource_name = new_resource.get('resource_name')

    if not resource_name:
        return jsonify({'message': 'Resource name is required'}), 400

    # Generate random resource ID
    resource_id = generate_resource_id()

    # Insert new resource into the database, along with company_id and Company_Name
    query = "INSERT INTO resource_data (resource_id, resource_name, company_id, company_name) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (resource_id, resource_name, company_id, company[1]))  # company[1] is the Company_Name
    conn.commit()

    response = {
        'resource_id': resource_id,
        'resource_name': resource_name,
        'company_id': company_id,
        'company_name': company[1]
    }

    cursor.close()
    conn.close()

    return jsonify(response), 201

# 2. Read a resource by ID (GET)
@app.route('/company_id=<int:company_id>/resource_id=<int:resource_id>', methods=['GET'])
def get_resource(company_id, resource_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company_id and auth_token are valid before accessing the resource
    auth_token = request.args.get('authorization_token')  # Get the auth_token from query params
    company = check_company_authorization(company_id, auth_token, cursor)
    if not company:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or authorization token'}), 403

    # Find the resource by resource_id
    resource = find_resource(resource_id, cursor)
    
    if resource:
        # If resource is found, return resource details
        resource_data = {
            'resource_id': resource[0],
            'resource_name': resource[1],
            'company_id': resource[2],
            'company_name': resource[3]
        }
        cursor.close()
        conn.close()
        return jsonify(resource_data), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Resource not found'}), 404

# 3. Update resource details (PUT)
@app.route('/company_id=<int:company_id>/resource_id=<int:resource_id>', methods=['PUT'])
def update_resource(company_id, resource_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company_id and auth_token are valid before updating the resource
    auth_token = request.args.get('authorization_token')  # Get the auth_token from query params
    company = check_company_authorization(company_id, auth_token, cursor)
    if not company:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or authorization token'}), 403

    # Find the resource by resource_id
    resource = find_resource(resource_id, cursor)
    
    if resource:
        # Get new data from the request
        updated_data = request.json
        resource_name = updated_data.get('resource_name', resource[1])  # Keep old name if not provided

        # Update resource in the database
        query = "UPDATE resource_data SET resource_name = %s WHERE resource_id = %s"
        cursor.execute(query, (resource_name, resource_id))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({'message': 'Resource updated successfully'}), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Resource not found'}), 404

# 4. Delete a resource (DELETE)
@app.route('/company_id=<int:company_id>/resource_id=<int:resource_id>', methods=['DELETE'])
def delete_resource(company_id, resource_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if company_id and auth_token are valid before deleting the resource
    auth_token = request.args.get('authorization_token')  # Get the auth_token from query params
    company = check_company_authorization(company_id, auth_token, cursor)
    if not company:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Invalid company ID or authorization token'}), 403

    # Find the resource by resource_id
    resource = find_resource(resource_id, cursor)
    
    if resource:
        # Delete the resource from the database
        query = "DELETE FROM resource_data WHERE resource_id = %s"
        cursor.execute(query, (resource_id,))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({'message': 'Resource deleted successfully'}), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Resource not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)


#==========================================================================================================================================================================
