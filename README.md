## Amazon RDS auto-restart protection

This is a plug and play solution to automatically stop your RDS instance once restarted by AWS in order not to fall behind maintenance activities. At the moment, this solution is not compatible with Aurora. 

### Deployment

The solution is deployed using AWS CloudFormation

Keep in mind, application is deployed per region per account.

1. Create an S3 bucket to upload your artifacts. For more information, see [create bucket](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html).
2. Add the following files to the newly created S3 bucket:
* `stop-rds-instance-state-machine.json` under `sources/stepfunctions-code`
* 3 `.zip` files under `sources/lambda-code-deployment-packages`
> Lambda `.py` files are also available under `sources/lambda-code`. For more information on how to create a .zip deployment package, see [python package](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html).
3. In AWS CloudFormation, start deploying deployment/master-template.yaml. For more information, see [create stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html).
4. Under RDS, create an RDS event subscription with the follwing configurations:
* Target: Arn and select the SNS Topic `SnsTopicRdsEvent` created by the CloudFormation deployment.
* Source type: Instances. You can either specify the list of instances or you can choose All.
* Under event categories, make sure you select 'notifications'. 
5. Finally, tag your RDS instance with `auto-restart-protection = yes`. Instances with the tag, will be automatically stopped once restarted after 7-days.

## Configure notifications

The CloudFormation deployment creates an SNS topic `SnsTopicWorkFlowNotification` to which the AWS StepFunctions state machine publishes the workflow execution notification. Go to the SNS console (or CLI) and subscribe to the topic using SMS, E-mail or else. You'll receive successful as well as failed notifications. 

## Test your deployment

In order to test the solution, create a test RDS instance, tag it with `auto-restart-protection` tag and set the tag value to `yes`. While the RDS instance is still in starting state, test the Lambda function —  `start-statemachine-execution-lambda` with a sample event that simulates that the instance was started as it exceeded the maximum time to remain stopped (RDS-EVENT-0154). 

### To invoke a function

* Sign in to the AWS Management Console and open the Lambda console at https://console.aws.amazon.com/lambda.
* In navigation pane, choose **Functions**.
* In **Functions pane**, choose `start-statemachine-execution-lambda`.
* In the upper right corner, choose **Test**.
* In the **Configure test event** page, choose **Create new test event** and in **Event template**, leave the default **Hello World** option. Enter an **Event name** and use the following sample event template. Only replace the two `<RDS instance id>` parameters with the the correct instance id, rest of the parameters are not validated:

    ```
    {
    "Records": [
        {
        "EventSource": "aws:sns",
        "EventVersion": "1.0",
        "EventSubscriptionArn": "<RDS event subscription arn>",
        "Sns": {
            "Type": "Notification",
            "MessageId": "10001-2d55da-9a73-5e42d46748c0",
            "TopicArn": "<SNS Topic Arn>",
            "Subject": "RDS Notification Message",
            "Message": "{\"Event Source\":\"db-instance\",\"Event Time\":\"2020-07-09 15:15:03.031\",\"Identifier Link\":\"https://console.aws.amazon.com/rds/home?region=<region>#dbinstance:id=<RDS instance id>\",\"Source ID\":\"<RDS instance id>\",\"Event ID\":\"http://docs.amazonwebservices.com/AmazonRDS/latest/UserGuide/USER_Events.html#RDS-EVENT-0154\",\"Event Message\":\"DB instance started\"}",
            "Timestamp": "2020-07-09T15:15:03.991Z",
            "SignatureVersion": "1",
            "Signature": "YsuM+L6N8rk+pBPBWoWeRcSuYqo/BN5v9D2lyoSg0B0uS46Q8NZZSoZWaIQi25TXfHY3RYXCXF9WbVGXiWa4dJs2Mjg46anM+2j6z9R7BDz0vt25qCrCyWhmWtc7yeETrlwa0jCtR/wxXFFexRwynqlZeDfvQpf/x+KNLrnJlT61WZ2FMTHYs124RwWU8NY3pm1Os0XOIvm8rfv3ywm1ccZfP4rF7Lfn+2EK6a0635Z/5aiyIlldNZxbgRYTODJYroO9INTlF7NPzVV1Y/K0E9aaL/wQgLZNquXQGCAxPFWy5lxJKeyUocOWcG48KJGIBUC36JJaqVdIilbZ9HvxTg==",
            "SigningCertUrl": "https://sns.<region>.amazonaws.com/SimpleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem",
            "UnsubscribeUrl": "https://sns.<region>.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=*<arn>*",
            "MessageAttributes": {}
        }
        }
    ]
    }


> `start-statemachine-execution-lambda` uses the SNS `MessageId` parameter as name for the AWS Step Functions execution. The name field is unique for a certain period of time, accordingly, with every test run the MessageId parameter value must be changed. 

* Choose **Create** and then choose **Test**. Each user can create up to 10 test events per function. Those test events are not available to other users.
* AWS Lambda executes your function on your behalf. The handler in your Lambda function receives and then processes the sample event.
* Upon successful execution, view results in the console.
* The **Execution result** section shows the execution status as *succeeded* and also shows the function execution results, returned by the return statement. 

Now, verify the execution of the AWS Step Functions state machine:

**To verify an AWS Step Functions state machine execution status:**

* Sign in to the AWS Management Console and open the Amazon RDS console at https://console.aws.amazon.com/states/home.
* In navigation pane, choose **State machines**.
* In the **State machine** pane, choose stop-rds-instance-statemachine.
* In the **Executions** pane, choose the execution with the *Name *value passed in the test event `MessageId` parameter. 
* In the **Visual workflow** pane, the real-time execution status is displayed.
* Under the **Step details** tab, all details related to inputs, outputs and exceptions are displayed.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

