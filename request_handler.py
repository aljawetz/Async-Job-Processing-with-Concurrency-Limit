import json
import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')

JOB_TRACKING_TABLE = os.environ['JOB_TRACKING_TABLE']
JOB_LAMBDA_ARN = os.environ['JOB_LAMBDA_ARN']
NUM_OF_CONCURRENT_JOBS = int(os.environ['NUM_OF_CONCURRENT_JOBS'])

table = dynamodb.Table(JOB_TRACKING_TABLE)


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        delay = body.get('delay', 0)
        user_id = body.get('user_id')

        if not isinstance(delay, int) or delay <= 0 or not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid delay or user_id parameter'})
            }

        # Check and update concurrent jobs count
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET concurrent_jobs = if_not_exists(concurrent_jobs, :zero) + :inc',
            ConditionExpression='attribute_not_exists(concurrent_jobs) OR concurrent_jobs < :limit',
            ExpressionAttributeValues={
                ':zero': 0, ':inc': 1, ':limit': NUM_OF_CONCURRENT_JOBS},
            ReturnValues='UPDATED_NEW'
        )

        # Invoke the job Lambda function
        lambda_client.invoke(
            FunctionName=JOB_LAMBDA_ARN,
            InvocationType='Event',
            Payload=json.dumps({
                'body': json.dumps({
                    'delay': delay,
                    'user_id': user_id,
                    'request_id': context.aws_request_id
                })
            })
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Job submitted successfully'})
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 429,
                'body': json.dumps({'message': 'Concurrent job limit reached'})
            }
        else:
            print(f"Error: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Internal server error'})
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
