## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: MIT-0
from ast import If
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

    #Mapping The EventBridge event inputs
    rdsEvent = event

    ## This is the unique identifier of the RDS event. This will be used as a unique identifier for the StepFunction Workflow Execution
    eventId = rdsEvent['id']

    ## Extract the resource ID
    rdsResourceId = rdsEvent['detail']['SourceIdentifier']

    ## The RDS Event Identifier. IN this solution, we are concerned with RDS-EVENT-0153 and RDS-EVENT-0154
    rdsEventId = rdsEvent['detail']['EventID']
    ## SourceType can be CLUSTER in case of Aurora and DB_INSTANCE in case of RDS instance.
    sourceType = rdsEvent['detail']['SourceType']
    ## SourceArn is the resource Arn for either RDS or Aurora
    sourceArn = rdsEvent['detail']['SourceArn']

    ##Prepare the StepFunctions Input. We're passing the Id of the resource as well as the type, either Aurora or RDS. 
    stepFunctionInput = {"rdsInstanceId": rdsResourceId, "sourceType": sourceType}

    # Filter on the Auto Restart RDS Event or Aurora Cluster
    # RDS-EVENT-0154 in case of RDS Instances and RDS-EVENT-0153 in case of Aurora
    if 'RDS-EVENT-0154' in rdsEventId or 'RDS-EVENT-0153' in rdsEventId:

        #log input event
        LOGGER.info("RdsAutoRestart Event detected, now verifying that instance was tagged with auto-restart-protection == yes")

        #Verify that instance is tagged with auto-restart-protection

        tagCheckPass = 'false'
        rdsResourceTags = rdsClient.list_tags_for_resource(ResourceName=sourceArn)
        for rdsResourceTag in rdsResourceTags["TagList"]:
            if 'auto-restart-protection' in rdsResourceTag["Key"]:
                if 'yes' in rdsResourceTag["Value"]:
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
            stepFunctionsArn = os.environ['STEPFUNCTION_ARN']
            stepFunctionsResponse = stepFunctionsClient.start_execution(
            stateMachineArn= stepFunctionsArn,
            name=eventId,
            input= json.dumps(stepFunctionInput)

        )
    # In case of Aurora Cluster we're looking for RDS-EVENT-0153
    
    else:

        LOGGER.info("RdsAutoRestart Event detected, and event is not eligible")

    return {
            'statusCode': 200
        }
