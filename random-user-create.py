import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import random
import string
from faker import Faker
import uuid

load_dotenv()
REGION = os.getenv('REGION')
USER_POOL_ID = os.getenv('USER_POOL_ID')
APP_CLIENT_ID = os.getenv('APP_CLIENT_ID')

def create_cognito_client(region):
    return boto3.client('cognito-idp', region_name=region)


def register_user(cognito_client, user_pool_id, username, password, custom_attributes=None):
    try:
        response = cognito_client.sign_up(
            ClientId=APP_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=custom_attributes,
        )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    
def confirm_user_signup(cognito_client, user_pool_id, username):
    try:
        response = cognito_client.admin_confirm_sign_up(
            UserPoolId=user_pool_id,
            Username=username
        )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None

def main(tenant_email, tenant_name, tenant_id, tenant_tier):

    for _ in range(10):

        cognito_client = create_cognito_client(REGION)
        # username=Faker().email()
        account, domain = tenant_email.split("@")
        username = f"{account}+{Faker().user_name()}@{domain}"
        password='@Dev1234'

        custom_attributes = [
            {
                'Name': 'custom:tenant_id',
                # 'Value': str(uuid.uuid4()).split('-')[4]
                'Value': tenant_id
            },
            {
                'Name': 'custom:tenant_name',
                # 'Value': Faker().company()
                'Value': tenant_name
            },
            {
                'Name': 'custom:tenant_tier',
                'Value': tenant_tier
            },
            {
                'Name': 'custom:user_role',
                'Value': 'Staff'
            }                
        ]

        response = register_user(cognito_client, USER_POOL_ID, username, password, custom_attributes)
        if response:
            print(response)
            print(f"User {username} created successfully.")

            confirmation_response = confirm_user_signup(cognito_client, USER_POOL_ID, username)
            if confirmation_response:
                print(confirmation_response)
                print(f"User {username} confirmed successfully.")
            else:
                print("Failed to confirm user.")

        else:
            print("Failed to create user.")

if __name__ == "__main__":
    email = 'jinseo.jang+manager@gmail.com'
    company = 'aws'
    tenant_id = 'TENANTGZQxat8dr'
    tier = 'premium'
    main(tenant_email=email, tenant_name=company, tenant_id=tenant_id, tenant_tier=tier)
