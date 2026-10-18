
import boto3

REGION = "us-east-1"
BUCKET = "lockbox-evidence-dg-2026-1018"
TABLE = "LockboxEvidence"

s3 = boto3.client("s3", region_name=REGION)
dynamodb = boto3.client("dynamodb", region_name=REGION)

print("Checking LOCKBOX AWS resources...")

bucket_response = s3.head_bucket(Bucket=BUCKET)
print("S3 Status:", bucket_response["ResponseMetadata"]["HTTPStatusCode"])

table_response = dynamodb.describe_table(TableName=TABLE)
table = table_response["Table"]

print("DynamoDB Table:", table["TableName"])
print("DynamoDB Status:", table["TableStatus"])

print("LOCKBOX connection check complete.")


