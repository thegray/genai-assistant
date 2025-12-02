$env:INGESTION_MODE="s3"
$env:S3_BUCKET="axrail-bot-content"
$env:AWS_REGION="ap-southeast-1"

python -m ingestion.main
