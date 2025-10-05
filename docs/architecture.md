# System Architecture

This project follows an **event-driven serverless architecture** on AWS.

## Flow
1. **Image Upload** → User uploads an image to the **Upload S3 Bucket**.
2. **S3 Event Trigger** → The upload triggers an **AWS Lambda** function.
3. **Lambda Processing** → The function:
   - Resizes the image (128x128, 512x512, etc.)
   - Adds a watermark
   - Optimizes file size
4. **Processed S3 Bucket** → Processed images are stored here.
5. **SNS Notification** → An email or message is sent to notify completion.

## Architecture Diagram
User → S3 (upload bucket) → Lambda → S3 (processed bucket) → SNS


## Design Goals
- **Scalable** (serverless, auto-scales with demand)
- **Cost-Efficient** (pays only for executions)
- **Secure** (least-privilege IAM roles, no public buckets)
- **Fast** (processes images in <2 seconds)
