import json
import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

JOB_TRACKING_TABLE = os.environ['JOB_TRACKING_TABLE']
table = dynamodb.Table(JOB_TRACKING_TABLE)


def lambda_handler(event, context):
    try:
        # Extract user_id from the event detail
        detail = json.loads(event['detail'])
        user_id = detail.get('user_id')

        if not user_id:
            print("Error: user_id not found in event detail")
            return

        # Decrement the concurrent jobs count
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET concurrent_jobs = concurrent_jobs - :dec',
            ExpressionAttributeValues={':dec': 1},
            ReturnValues='UPDATED_NEW'
        )

        print(f"Successfully decremented concurrent_jobs for user {user_id}")
        print(f"New concurrent_jobs value: {response['Attributes'].get('concurrent_jobs')}")

    except ClientError as e:
        print(f"Error updating DynamoDB: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
