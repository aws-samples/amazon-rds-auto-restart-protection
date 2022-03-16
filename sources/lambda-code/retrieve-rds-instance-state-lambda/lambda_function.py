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
    
    resourceId = event['rdsInstanceId']
    sourceType = event['sourceType']

    if sourceType.lower() == 'cluster':
        db_state= rdsClient.describe_db_clusters(DBClusterIdentifier=resourceId)['DBClusters'][0]['Status']    
    elif sourceType.lower() == 'db_instance':
        db_state = rdsClient.describe_db_instances(DBInstanceIdentifier=resourceId)['DBInstances'][0]['DBInstanceStatus']

    return {
        'statusCode': 200,
        'rdsInstanceState': db_state,
        'rdsInstanceId': resourceId,
        'sourceType': sourceType
    }
