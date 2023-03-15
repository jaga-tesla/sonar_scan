import boto3
from datetime import datetime, timedelta
import time

AWS_REGION = "us-east-1"
client = boto3.client('logs', region_name=AWS_REGION)

query = "stats count(*) by srcAddr, dstAddr | filter interfaceId in ['eni-07de7e666ad4304dc'] | filter srcAddr in ['172.0.21.187','172.0.21.95','18.214.85.154','100.26.7.172']"

log_group = 'VPC-Innova-Flow-Logs'

today = datetime.now()
data = today.replace(hour=0, minute=0, second=0) - timedelta(1)
start = data
end = today.replace(hour=23, minute=59, second=59) - timedelta(1)

print ("Starting time : ", start)
print ("Ending time : ", end)

start_query_response = client.start_query(
    logGroupName=log_group,
    startTime=int(start.timestamp()),
    endTime=int(end.timestamp()),
    queryString=query,
)

query_id = start_query_response['queryId']

response = None



while response == None or response['status'] == 'Running':
    time.sleep(1)
    response = client.get_query_results(
        queryId=query_id
    )
print ("********************RESULT************************")
for i in response['results'] :
    print ("IP : ", i[0]['value'])
    print ("Count : ", i[2]['value'])
    print ("****************************")

