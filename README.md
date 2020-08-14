## Amazon RDS auto-restart protetcion

This is a plug and play solution to automatically stop your RDS instance once restarted by AWS in order not to fall behind maintaince activities. 

### Deployment

The solution is deployed using AWS CloudFormation

Keep in mind, application is deployed per region per account.

1. Create an S3 bucket. For more information, see [create bucket](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html)
2. Add the 4 files under sources/ to the newly created S3 bucket.
3. In AWS CloudFormation, start deploying deployment/cloudformationstage01.json. This template includes all needed IAM policies. For more information, see [create stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html)
4. Once step 3 is successful, start deploying deployment/cloudformationstage01.json. This template deploys: Lambda, StepFunctions and SNS. For more information, see [create stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html)
5. Under RDS, create an RDS event subscription (All Instances, category: notification) and hook it up to the created SNS Topic.
6. Finally, tag your RDS instance with auto-restart-protection = yes. Instances with the tag, will be automatically stopped once restarted after 7-days.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

