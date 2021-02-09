## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: MIT-0
import json
import boto3
import logging
import os

#Logging
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#Initialise Boto3 for RDS
rdsClient = boto3.client('rds')

def lambda_handler(event, context):

    #log input event
    LOGGER.info("RdsAutoRestart Event Received, now checking if event is eligible. Event Details ==> %s", event)

    #Input
    snsMessage = json.loads(event['Records'][0]['Sns']['Message'])
    rdsInstanceId = snsMessage['Source ID']
    stepFunctionInput = {"rdsInstanceId": rdsInstanceId}
    rdsEventId = snsMessage['Event ID']

    #Retrieve RDS instance ARN
    db_instances = rdsClient.describe_db_instances(DBInstanceIdentifier=rdsInstanceId)['DBInstances']
    db_instance = db_instances[0]
    rdsInstanceArn = db_instance['DBInstanceArn']

    # Filter on the Auto Restart RDS Event

    if 'RDS-EVENT-0154' in rdsEventId:

        #log input event
        LOGGER.info("RdsAutoRestart Event detected, now verifying that instance was tagged with auto-restart-protection == yes")

        #Verify that instance is tagged with auto-restart-protection

        tagCheckPass = 'false'
        rdsInstanceTags = rdsClient.list_tags_for_resource(ResourceName=rdsInstanceArn)
        for rdsInstanceTag in rdsInstanceTags["TagList"]:
            if 'auto-restart-protection' in rdsInstanceTag["Key"]:
                if 'yes' in rdsInstanceTag["Value"]:
                    tagCheckPass = 'true'
                    #log instance tags
                    LOGGER.info("RdsAutoRestart verified that the instance is tagged auto-restart-protection = yes, now starting the Step Functions Flow")
                else:
                    tagCheckPass = 'false'


        #log instance tags
        LOGGER.info("RdsAutoRestart Event detected, now verifying that instance was tagged with auto-restart-protection == yes")

        if 'true' in tagCheckPass:

            #Initialise StepFunctions Client
            stepFunctionsClient = boto3.client('stepfunctions')

            # Start StepFunctions WorkFlow
            #stepFunctionsArn = "arn:aws:states:ap-southeast-2:512072662296:stateMachine:RdsAutoRestartWorkFlow";
            stepFunctionsArn = os.environ['STEPFUNCTION_ARN']
            stepFunctionsResponse = stepFunctionsClient.start_execution(
            stateMachineArn= stepFunctionsArn,
            name=event['Records'][0]['Sns']['MessageId'],
            input= json.dumps(stepFunctionInput)

        )

    else:

        LOGGER.info("RdsAutoRestart Event detected, and event is not eligible")

    return {
            'statusCode': 200
        }
