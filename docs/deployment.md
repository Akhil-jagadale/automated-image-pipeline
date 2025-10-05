*Deployment Guide*

*Prerequisites*

AWS Account
AWS CLI installed and configured
Python 3.11+
Basic AWS knowledge (S3, Lambda, IAM, SNS)

1. Create S3 Buckets
aws s3 mb s3://your-upload-bucket
aws s3 mb s3://your-processed-bucket

2. Create IAM Role
Go to IAM → Roles → Create Role

Select AWS Service → Lambda

Attach the following policies:
AmazonS3FullAccess

AWSLambdaBasicExecutionRole

AmazonSNSFullAccess

Copy the Role ARN (needed for Lambda creation)

3. Deploy Lambda Function
Zip your Lambda code:

zip deployment.zip lambda_function.py


Create the Lambda function:
aws lambda create-function \
  --function-name ImageProcessor \
  --runtime python3.11 \
  --role arn:aws:iam::<ACCOUNT_ID>:role/LambdaImageProcessingRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{PROCESSED_BUCKET=your-processed-bucket,WATERMARK_TEXT=YourBrand}" \
  --layers arn:aws:lambda:ap-south-1:770693421928:layer:Klayers-p311-Pillow:9

4. Configure S3 Trigger

Create a JSON config config/s3-notification.json like this:

{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:<region>:<account_id>:function:ImageProcessor",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {"Name": "prefix", "Value": "uploads/"}
          ]
        }
      }
    }
  ]
}


Apply it:

aws s3api put-bucket-notification-configuration \
  --bucket your-upload-bucket \
  --notification-configuration file://config/s3-notification.json

5. Test the Setup

Upload a test image:

aws s3 cp test.jpg s3://your-upload-bucket/uploads/


Check processed files:

aws s3 ls s3://your-processed-bucket/thumb/
aws s3 ls s3://your-processed-bucket/medium/


Check Lambda logs:

aws logs tail /aws/lambda/ImageProcessor --follow
