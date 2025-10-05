# Serverless Image Optimization Pipeline

A serverless, event-driven image processing pipeline that automatically generates optimized, watermarked thumbnails when new images are uploaded to Amazon S3. Built with **AWS Lambda, Python, and Pillow**, this system is **scalable, secure, and cost-efficient** — perfect for production-ready image handling.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)

---

## ✨ Key Features

* 🚀 **Automatic Processing** – Triggers on every new S3 upload
* 📐 **Multiple Size Variants** – Generates thumbnail (128×128), medium (512×512), and more
* 💧 **Configurable Watermark** – Overlay branding with adjustable opacity
* 📧 **Notifications** – Optional SNS/email alerts on completion
* 🔒 **Secure by Design** – IAM-based permissions, no public S3 access
* 💰 **Cost-Efficient** – Pay only per execution, typically <$2/month
* ⚡ **High Performance** – Processes most images in under 2 seconds

---

## 🏗️ Architecture

```
Image Upload → S3 Event → Lambda → Optimize + Watermark → Processed S3 Bucket → (SNS Notify)
```

**Example Output Structure:**

```
processed-bucket/
├── thumb/image.jpg    (128x128, ~95% smaller)
└── medium/image.jpg   (512x512, ~85% smaller)
```

---

## 🚀 Quick Start

### Prerequisites

* AWS Account with CLI configured
* Python 3.11+
* Basic knowledge of S3, Lambda, and IAM

### 1. Clone & Configure

```bash
git clone https://github.com/Akhil-jagadale/automated-image-pipeline.git
cd automated-image-pipeline
```

Edit `config/deployment-config.json` with your settings.

### 2. Create AWS Resources

```bash
aws s3 mb s3://your-upload-bucket
aws s3 mb s3://your-processed-bucket
```

Create an IAM role with **S3, CloudWatch Logs, and SNS** permissions.

### 3. Deploy Lambda Function

```bash
zip deployment.zip lambda_function.py

aws lambda create-function \
  --function-name ImageProcessor \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/LambdaImageProcessingRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{PROCESSED_BUCKET=your-processed-bucket,WATERMARK_TEXT=YourBrand}" \
  --layers arn:aws:lambda:ap-south-1:770693421928:layer:Klayers-p311-Pillow:9
```

### 4. Configure S3 Trigger

* Go to **S3 → Upload bucket → Properties → Event notifications**
* Create event: **All object create events → Lambda (ImageProcessor)**

### 5. Test the Pipeline

```bash
aws s3 cp test.jpg s3://your-upload-bucket/uploads/
aws s3 ls s3://your-processed-bucket/thumb/
```

View logs:

```bash
aws logs tail /aws/lambda/ImageProcessor --follow
```

---

## ⚙️ Configuration

| Variable           | Description                 | Required | Default   |
| ------------------ | --------------------------- | -------- | --------- |
| `PROCESSED_BUCKET` | Destination bucket          | ✅        | -         |
| `SNS_TOPIC_ARN`    | SNS topic for notifications | ❌        | -         |
| `WATERMARK_TEXT`   | Watermark text              | ❌        | YourBrand |

Image sizes, watermark style, and quality can be customized inside `lambda_function.py`.

---

## 📊 Performance & Cost

| Metric              | Value          |
| ------------------- | -------------- |
| Processing time     | 200–500 ms     |
| Memory usage        | ~200 MB        |
| File size reduction | 70–95%         |
| Max image size      | 10 MB          |
| Supported formats   | JPG, PNG, WebP |

**Estimated Monthly Cost (10,000 images @ 2MB each):**

* Lambda: ~$0.50
* S3 Storage + Requests: ~$0.40
* SNS Notifications: ~$0.50
* **Total:** ~**$1.40/month** (vs $50+ for EC2-based systems)

---

## 🔒 Security Best Practices

✅ Implemented

* IAM least-privilege policies
* No public bucket access
* CloudWatch logging enabled

🔒 Recommended

* Enable bucket encryption (SSE-S3 or SSE-KMS)
* Enable CloudTrail for API auditing
* Use VPC endpoints for private access
* Add Dead Letter Queue (DLQ) for failed executions

---

## 🛠️ Project Structure

```
automated-image-pipeline/
├── lambda_function.py     # Core AWS Lambda function (image processing logic)
├── config/                # Deployment configs (e.g., IAM, S3, SNS settings)
├── examples/              # Sample S3 event JSONs and test images
├── docs/                  # Extended documentation (deployment, usage, troubleshooting)
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # Project overview and instructions
```
