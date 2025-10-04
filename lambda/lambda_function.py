import os
import boto3
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

s3 = boto3.client('s3')
sns = boto3.client('sns')

PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def add_watermark(img, text="YourSite"):
    """Add a watermark in bottom-right corner."""
    watermark = Image.new("RGBA", img.size)
    draw = ImageDraw.Draw(watermark)
    font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = img.width - text_w - 8
    y = img.height - text_h - 8

    draw.text((x, y), text, fill=(255, 255, 255, 150), font=font)
    return Image.alpha_composite(img.convert("RGBA"), watermark).convert("RGB")

def process_and_upload(image_bytes, bucket, key):
    """Resize + watermark + upload versions directly, without keeping them all in memory."""
    with Image.open(BytesIO(image_bytes)) as img:
        img = img.convert("RGB")

        sizes = {"thumb": (128, 128), "medium": (512, 512)}

        for prefix, size in sizes.items():
            copy = img.copy()
            copy.thumbnail(size, Image.LANCZOS)

            copy = add_watermark(copy)

            buf = BytesIO()
            copy.save(buf, format="JPEG", quality=85)
            buf.seek(0)

            dest_key = f"{prefix}/{key.rsplit('/', 1)[-1]}"  # store with same filename
            s3.put_object(Bucket=bucket, Key=dest_key, Body=buf, ContentType="image/jpeg")
            logger.info(f"✅ Saved {bucket}/{dest_key}")

def publish_sns(subject, message):
    if SNS_TOPIC_ARN:
        try:
            sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
        except Exception as e:
            logger.warning(f"SNS publish failed: {e}")

def lambda_handler(event, context):
    for record in event.get('Records', []):
        try:
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'])
            logger.info(f"Processing s3://{bucket}/{key}")

            obj = s3.get_object(Bucket=bucket, Key=key)
            body = obj['Body'].read()

            process_and_upload(body, PROCESSED_BUCKET, key)
            publish_sns("Image processed", f"Processed {key} successfully.")

        except Exception as e:
            logger.exception(f"Error processing {key}")
            publish_sns("Image processing failed", f"Error processing {key}: {e}")