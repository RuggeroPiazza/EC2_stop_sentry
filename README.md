# Introduction
Stop Ec2 Sentry function:

The Lambda function is triggered by a scheduled event, 
detects all the instances running including the tag "environment : Test" and proceed to stop them.
An email notification containing information about those changes is then sent to the Admin.


# Workflow
1. On the date scheduled, an EventBridge scheduled event trigger the Lambda function.
2. The function detects all the running instances tagged as part of the Test environment.
3. The script stop all those instances.
4. An email notification is sent via SNS with information about the change, confirming the success or the failure of the task.


# Pre-requisite
- Running instances containing the following tag: "environment : Test"
- IAM role for the Lambda with relative permissions.
- os, json, boto3, botocore, logging modules installed.


# Instructions
1. ***Launch an instance*** and ***add a tag***.
Launch one or more instances. At this stage, the only requirements is that all the instances must be tagged as follow:
Key: environment
Value: Test
Please remember that tags are ***case sensitive***, so make sure to follow the same string format everywhere.


2. ***Create the IAM policy***.
Create a new IAM policy as follow:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "*"
        }
    ]
}
``` 


3. ***Create a Lambda execution role***.
After creating the role, make sure you attach to it the policy created on step 2.


4. ***Create the SNS Topic***:
Create a new topic, Standard type.
Name it.
Any other setting can be left as default.
Create now a Subscription:
Under “Protocol” select Email and under “endpoint” insert the email address.
Any other setting can be left as default.
Create the subscription. 
Confirm subscription by clicking on the link sent to the email address used in the subscription.
Copy the SNS Topic ARN on your clipboard.


5. ***Create the Lambda*** Function.
Add the code provided.
Update the global variable "REGION" at the beginning of the script. 
Go on the configuration section of the Lambda function and create the following environment variables: 

    Key: environment, Value: Test

    Key: sns_topic_arn, Value: insert the SNS topic ARN 

    Remember to save and ***deploy*** all the changes.


6. ***Create a scheduled EventBridge Rule*** as trigger:
Go on Amazon EventBridge.
Create a scheduled event and specify the details.
At this stage, you can choose the best schedule that fits your need:
a one-time schedule has a specific date and time.
A recurring schedule has two schedule type: 
Cron-based: a cron espression must be used that runs at a specific time, such as 8:00 am on the first Monday of every month.
Rate-based: a schedule taht runs at regular rate, such as every 10 mins.

    Select the Lambda function as a target.


7. ***Test*** the function:
With the EventBridge event enabled, at the specific date and time selected, the Lambda function will be triggered.
If all configured properly, you should see the instances move to the "stopping" stage and receive an email notification.
Please check the CloudWatch Logs for any output from the Lambda function.