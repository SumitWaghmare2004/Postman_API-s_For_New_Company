
#==========================================================================================================================================================================

# POST = http://127.0.0.1:5001/company
#GET , PUT , DELETE = http://localhost:5001/company_id=241687975/authorization_token=RpyAXo9-yBAXYj-PEMFJ-M52p5JcMUy

# Format_of_Json_raw :-  
                        # {
                        #  "company_name": "Tech Innovators"
                        # }

#==========================================================================================================================================================================

#                                                     Code_For_Exact_ID's and Token's

#==========================================================================================================================================================================

from flask import Flask, jsonify, request
import mysql.connector
import random
import string

app = Flask(__name__)

# Connect to MySQL server (adjust host, user, and password as needed)
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Replace with your MySQL server host
        user="root",       # Replace with your MySQL user
        password="root",   # Replace with your MySQL password
        database="api_database"  # Use your database
    )

# Helper function to generate random authorization token in the format "x1dsdwe-wrssdz-vcf12-sgqnw21212"
def generate_auth_token():
    part1 = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    part2 = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    part3 = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    part4 = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{part1}-{part2}-{part3}-{part4}"

# Helper function to generate a random company ID that fits in the INT range
def generate_company_id():
    # Maximum 9 digits to fit within the INT range
    return random.randint(100000000, 2147483647)


# Helper function to find company by ID in the database
def find_company(company_id, auth_token, cursor):
    query = "SELECT * FROM Company_Data WHERE Company_Id = %s AND Authorization_Token = %s"
    cursor.execute(query, (company_id, auth_token))
    return cursor.fetchone()

# 1. Create a new company (POST) with Authorization Token
@app.route('/company', methods=['POST'])
def add_company():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get company data from request
    new_company = request.json
    company_name = new_company.get('company_name')
    
    if not company_name:
        return jsonify({'message': 'Company name is required'}), 400

    # Generate a random 10-digit company_id
    company_id = generate_company_id()

    # Generate and store authorization token
    generated_token = generate_auth_token()

    # Insert new company into the database with the generated token
    query = "INSERT INTO Company_Data (Company_Id, Company_Name, Authorization_Token) VALUES (%s, %s, %s)"
    cursor.execute(query, (company_id, company_name, generated_token))
    conn.commit()

    response = {
        'company_id': company_id,
        'company_name': company_name,
        'authorization_token': generated_token
    }

    cursor.close()
    conn.close()

    return jsonify(response), 201

# 2. Read companies (GET by ID and Authorization Token)
@app.route('/company_id=<int:company_id>/authorization_token=<auth_token>', methods=['GET'])
def get_company(company_id, auth_token):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find the company by company_id and authorization token
    company = find_company(company_id, auth_token, cursor)
    
    if company:
        # If company is found, return company details
        company_data = {
            'company_id': company[0],
            'company_name': company[1],
            'authorization_token': company[2]
        }
        cursor.close()
        conn.close()
        return jsonify(company_data), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Company not found or invalid authorization token'}), 404

# 3. Update company details by ID (PUT)
@app.route('/company_id=<int:company_id>/authorization_token=<auth_token>', methods=['PUT'])
def update_company(company_id, auth_token):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find the company by company_id and authorization token
    company = find_company(company_id, auth_token, cursor)
    
    if company:
        # Get new data from the request
        updated_data = request.json
        company_name = updated_data.get('company_name', company[1])  # Keep old name if not provided
        
        # Update company in the database
        query = "UPDATE Company_Data SET Company_Name = %s WHERE Company_Id = %s"
        cursor.execute(query, (company_name, company_id))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({'message': 'Company updated successfully'}), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Company not found or invalid authorization token'}), 404

# 4. Delete a company by ID (DELETE)
@app.route('/company_id=<int:company_id>/authorization_token=<auth_token>', methods=['DELETE'])
def delete_company(company_id, auth_token):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find the company by company_id and authorization token
    company = find_company(company_id, auth_token, cursor)
    
    if company:
        # Delete the company from the database
        query = "DELETE FROM Company_Data WHERE Company_Id = %s"
        cursor.execute(query, (company_id,))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({'message': 'Company deleted successfully'}), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'Company not found or invalid authorization token'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)

