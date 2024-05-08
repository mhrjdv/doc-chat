import os
import json
import boto3
from aws_lambda_powertools import Logger

# Initialize AWS clients
s3 = boto3.client('s3')
ddb = boto3.resource("dynamodb")
document_table = ddb.Table(os.environ["DOCUMENT_TABLE"])
memory_table = ddb.Table(os.environ["MEMORY_TABLE"])
logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    document_id = event["pathParameters"]["documentid"]
    bucket_name = os.environ["S3_BUCKET"]  # Assume the bucket name is stored in an environment variable

    # Perform authorization and other business logic checks
    # Example: Verify the user has permission to delete the document
    document_response = document_table.get_item(
        Key={"userid": user_id, "documentid": document_id}
    )
    if 'Item' not in document_response:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Document not found"})
        }

    # Perform the delete operation on S3
    try:
        s3.delete_object(Bucket=bucket_name, Key=document_id)
        # Optionally, delete metadata from DynamoDB or perform other cleanup
        document_table.delete_item(
            Key={"userid": user_id, "documentid": document_id}
        )
        logger.info(f"Document {document_id} deleted successfully")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Document deleted successfully"})
        }
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Failed to delete document"})
        }
