## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: MIT-0
import json
import logging
import boto3

#Logging
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#Initialise Boto3 for RDS
rdsClient = boto3.client('rds')


def lambda_handler(event, context):
    
    #log input event
    LOGGER.info(event)
    
    rdsInstanceId = event['rdsInstanceId']
    
    #Stop RDS instance
    rdsClient.stop_db_instance(DBInstanceIdentifier=rdsInstanceId)
    
    #Tagging
    
    
    return {
        'statusCode': 200,
        'rdsInstanceId': rdsInstanceId
    }
