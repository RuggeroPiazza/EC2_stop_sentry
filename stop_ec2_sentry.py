import os
import json
import logging
import boto3
import botocore

# logging
log = logging.getLogger()
log.setLevel(logging.INFO)

# global variables
SNS_TOPIC_ARN = os.environ.get("sns_topic_arn")
REGION = "eu-west-2"
ENVIRONMENT_TAG = os.environ.get("environment")

# instantiate boto3 clients
ec2_client = boto3.client('ec2', region_name=REGION)
sns_client = boto3.client('sns')


def lambda_handler(event, context):
    ids, count = check_running_instances()
    if ids:
        if stop_running_instances(ids):
            log.info("stop_instances: successful")
            if send_notification(count):
                log.info("SNS publish: successful")
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': "Successful requests."})
                }
            log.info("SNS publish: an error occurred")
            return {
                'statusCode': 206,
                'body': json.dumps({'error': "An error occurred in the SNS publish request."})
            }
        log.info("stop_instances: an error occurred")
        if not send_notification(count, False):
            return {
                'statusCode': 500,
                'body': json.dumps({'error': "An error occurred, all requests failed."})
            }
        return {
            'statusCode': 206,
            'body': json.dumps({'error': "An error occurred in the stop_instance request."})
        }
    log.info("describe_instances: an error occurred")
    raise Exception("describe_instances could't find any instance ID's or not running instances found")


def check_running_instances():
    filters = [
        {'Name' : "tag:environment",'Values' : [ENVIRONMENT_TAG]},
        {'Name' : "instance-state-name",'Values' : ['running']},
    ]
    try:
        response = ec2_client.describe_instances(Filters=filters)
        instances_id = []
        for instance in response['Reservations']:
            instances_id.append(instance['Instances'][0]['InstanceId'])
        count = len(instances_id)
        return instances_id, count
    except botocore.exceptions.ClientError as error:
        log.error(f"Boto3 API returned error: {error}")
        return False


def stop_running_instances(instances_id):
    try:
        ec2_client.stop_instances(InstanceIds=instances_id)
        return True
    except botocore.exceptions.ClientError as error:
        log.error(f"Boto3 API returned error: {error}")
        return False


def send_notification(count, success=True):
    message = "Some requests have failed. The Lambda function couldn't perform the task.\n"
    subject = "WARNING: Auto-Mitigation unsuccessful"
    if success:
        message = "The lambda function was triggered successfully.\n"
        subject = "AUTO-MITIGATION: successfull"
    
    message += (
        f"{count} running instances found and stopped.\n"
        f"Region: {REGION}\n"
        f"Environment: {ENVIRONMENT_TAG}"
        )
    try:
        sns_client.publish(TargetArn=SNS_TOPIC_ARN, Message=message, Subject=subject)
        return True 
    except botocore.exceptions.ClientError as error:
        log.error(f"Boto3 API returned error: {error}")
        return False
