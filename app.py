import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from auth import get_tenantid
import psycopg2

app = Flask(__name__)
api = Api(app)

load_dotenv()

HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')

db_connection = {
    'host': HOST,
    'database': DB_NAME,
    'user': DB_USER,
    'password': DB_PWD
}

def get_db_connection():
    conn = psycopg2.connect(**db_connection)
    return conn

def insert_user(conn, user_data):
    cursor = conn.cursor()

    query = '''
        INSERT INTO users (user_name, tenant_id, user_role, tenant_name)
        VALUES (%s, %s, %s, %s);
    '''

    cursor.execute(query, (user_data['user_name'], user_data['tenant_id'], user_data['role'], user_data['tenant_name']))
    conn.commit()
    cursor.close()


def insert_tenant(conn, tenant_data):
    cursor = conn.cursor()

    query_check = '''
    SELECT * FROM tenants
    WHERE tenant_id = %s;
    '''


    cursor.execute(query_check, (tenant_data['tenant_id'],))
    existing_tenant = cursor.fetchone()

    if existing_tenant:
        cursor.close()
        return None, f"Tenant {tenant_data['tenant_id']} already exists"
    
    else:
        query_insert = '''
            INSERT INTO tenants (tenant_id, tenant_name, onboarding_date, status, tier)
            VALUES (%s, %s, NOW(), %s, %s);
        '''

        cursor.execute(query_insert, (tenant_data['tenant_id'], tenant_data['tenant_name'], tenant_data['status'],tenant_data['tier']))
        conn.commit()
        cursor.close()
    

        return tenant_data['tenant_id'], "Tenant created"

class RegisterTenantUser(Resource):
    @get_tenantid
    def post(self, tenant_id):
        data = request.get_json()

        print("here2", data)
        user_data = {
            'tenant_name': data.get('tenant_name'),
            'role': data.get('role'),
            'user_name': data.get('user_name'),
            'tenant_id': data.get('tenant_id')
        }

        tenant_data = {
            'tenant_id': data.get('tenant_id'),
            'tenant_name': data.get('tenant_name'),
            'status': 'active',
            'tier': data.get('tier')
        }

        conn = get_db_connection()
        tenant_id, message = insert_tenant(conn, tenant_data)
        print(tenant_id, message)

        insert_user(conn, user_data)
        conn.close()

        return {'message': 'User and tenant data created'}, 201


api.add_resource(RegisterTenantUser, '/api/users')