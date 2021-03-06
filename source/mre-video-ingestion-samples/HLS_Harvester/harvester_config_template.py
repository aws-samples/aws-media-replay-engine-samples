EC2_INSTANCE_TYPE="<Type of the EC2 instance to launch for the HLS Harvester>"
SUBNET_ID="<ID of the Private subnet (with route to the NAT Gateway) to launch the HLS Harvester EC2 instance in>"
SECURITY_GROUPS_IDS="<Comma separated list of Security group IDs to attach to the HLS Harvester EC2 instance>"
MRE_REGION="<Region (formatted like us-east-1) where MRE has been deployed>"
SQS_QUEUE_URL="<URL of the MREEventHarvestingQueue SQS Queue>"
SQS_WAIT_TIME_SECS="<Duration (in seconds) for which the SQS client waits for a message to arrive in the queue before returning>"
API_KEY="<Auth key for the source HLS endpoint URL>"
CHUNK_SIZE="<Size (in seconds) of the HLS chunk to be outputted in S3>"
DESTINATION_S3_BUCKET="<Name of the MediaLiveDestinationBucket S3 bucket created by the MRE framework>"
