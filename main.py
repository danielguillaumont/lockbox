
from botocore.exceptions import ClientError

from aws_storage import (
    add_evidence,
    get_case_evidence,
    download_evidence,
    delete_evidence
)


def show_menu():
    print("\n" + "=" * 45)
    print("           LOCKBOX")
    print("       Cloud Evidence Locker")
    print("=" * 45)
    print("1. Add evidence")
    print("2. View evidence by case")
    print("3. Download evidence")
    print("4. Delete evidence")
    print("5. Exit")
    print("-" * 45)


def valid_id(value):
    return bool(value) and all(
        char.isalnum() or char == "-"
        for char in value
    )


def add_evidence_menu():
    case_id = input("Case ID (e.g. CASE-001): ").strip().upper()
    file_path = input("File path: ").strip()
    description = input("Description: ").strip()

    if not valid_id(case_id) or not file_path:
        print("Enter a valid Case ID and file path.")
        return

    try:
        item = add_evidence(case_id, file_path, description)

        print("\nEvidence uploaded successfully!")
        print("Case ID:", item["case_id"])
        print("Evidence ID:", item["evidence_id"])
        print("Filename:", item["filename"])
        print("S3 Location:", item["s3_key"])

    except FileNotFoundError as error:
        print(error)
    except ClientError as error:
        print("AWS error:", error.response["Error"]["Message"])
    except Exception as error:
        print("Upload failed:", error)


def view_evidence():
    case_id = input("Enter Case ID: ").strip().upper()

    if not valid_id(case_id):
        print("Enter a valid Case ID.")
        return

    try:
        records = get_case_evidence(case_id)
    except ClientError as error:
        print("AWS error:", error.response["Error"]["Message"])
        return

    if not records:
        print(f"No evidence found for {case_id}.")
        return

    print(f"\nEvidence for {case_id}:")

    for record in records:
        print("-" * 45)
        print("Evidence ID:", record["evidence_id"])
        print("Filename:", record.get("filename", "Unknown"))
        print("Description:", record.get("description", "None"))
        print("Uploaded:", record.get("uploaded_at", "Unknown"))


def download_evidence_menu():
    case_id = input("Enter Case ID: ").strip().upper()
    evidence_id = input("Enter Evidence ID: ").strip().upper()

    if not valid_id(case_id) or not valid_id(evidence_id):
        print("Enter valid Case and Evidence IDs.")
        return

    try:
        path = download_evidence(case_id, evidence_id)

        if path is None:
            print("Evidence record not found.")
            return

        print("\nEvidence downloaded successfully!")
        print("Saved to:", path)

    except ClientError as error:
        print("AWS error:", error.response["Error"]["Message"])
    except Exception as error:
        print("Download failed:", error)


def delete_evidence_menu():
    case_id = input("Enter Case ID: ").strip().upper()
    evidence_id = input("Enter Evidence ID: ").strip().upper()

    if not valid_id(case_id) or not valid_id(evidence_id):
        print("Enter valid Case and Evidence IDs.")
        return

    print("\nWARNING: This will permanently delete:")
    print("Case ID:", case_id)
    print("Evidence ID:", evidence_id)
    print("Both the S3 file and DynamoDB record will be deleted.")

    confirmation = input("Type DELETE to confirm: ").strip()

    if confirmation != "DELETE":
        print("Deletion cancelled.")
        return

    try:
        item = delete_evidence(case_id, evidence_id)

        if item is None:
            print("Evidence record not found.")
            return

        print("\nEvidence deleted successfully!")
        print("Case ID:", item["case_id"])
        print("Evidence ID:", item["evidence_id"])
        print("Filename:", item["filename"])

    except ClientError as error:
        print("AWS error:", error.response["Error"]["Message"])
        print("Check both AWS services before retrying.")
    except Exception as error:
        print("Deletion failed:", error)
        print("Check both AWS services before retrying.")


def main():
    while True:
        show_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            add_evidence_menu()
        elif choice == "2":
            view_evidence()
        elif choice == "3":
            download_evidence_menu()
        elif choice == "4":
            delete_evidence_menu()
        elif choice == "5":
            print("Exiting LOCKBOX. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()

