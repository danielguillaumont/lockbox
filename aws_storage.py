
import boto3
import hashlib
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

from config import AWS_REGION, S3_BUCKET, DYNAMODB_TABLE


s3 = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)


def calculate_sha256(file_path):
    checksum = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(65536)

            if not chunk:
                break

            checksum.update(chunk)

    return checksum.hexdigest()


def get_case_evidence(case_id):
    response = table.query(
        KeyConditionExpression=Key("case_id").eq(case_id)
    )
    return response.get("Items", [])


def add_evidence(case_id, file_path, description):
    path = Path(file_path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    evidence_id = "EVD-" + uuid4().hex[:10].upper()
    s3_key = f"cases/{case_id}/{evidence_id}/{path.name}"

    file_hash = calculate_sha256(path)

    s3.upload_file(str(path), S3_BUCKET, s3_key)

    item = {
        "case_id": case_id,
        "evidence_id": evidence_id,
        "filename": path.name,
        "s3_key": s3_key,
        "description": description,
        "file_size": path.stat().st_size,
        "sha256": file_hash,
        "uploaded_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
    }

    try:
        table.put_item(Item=item)
    except Exception:
        s3.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        raise

    return item


def download_evidence(case_id, evidence_id):
    response = table.get_item(
        Key={
            "case_id": case_id,
            "evidence_id": evidence_id
        }
    )

    item = response.get("Item")

    if not item:
        return None

    filename = Path(item["filename"]).name

    download_path = (
        Path("downloads") /
        case_id /
        evidence_id /
        filename
    )

    download_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    s3.download_file(
        S3_BUCKET,
        item["s3_key"],
        str(download_path)
    )

    expected_hash = item.get("sha256")

    if expected_hash:
        actual_hash = calculate_sha256(download_path)

        if actual_hash != expected_hash:
            download_path.unlink()
            raise ValueError(
                "SHA-256 integrity check failed. "
                "The downloaded file does not match "
                "the original evidence."
            )

    return download_path


def delete_evidence(case_id, evidence_id):
    response = table.get_item(
        Key={
            "case_id": case_id,
            "evidence_id": evidence_id
        }
    )

    item = response.get("Item")

    if not item:
        return None

    s3.delete_object(
        Bucket=S3_BUCKET,
        Key=item["s3_key"]
    )

    table.delete_item(
        Key={
            "case_id": case_id,
            "evidence_id": evidence_id
        }
    )

    return item

