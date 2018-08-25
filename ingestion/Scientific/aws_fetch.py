import boto3
client = boto3.client('s3')

#Replace your bucket name and in prefix, file name 
s3_bucket=""
file_path_with_name=""
key=""

resp = client.list_objects_v2(Bucket=s3_bucket, Prefix=file_path_with_name) 

for obj in resp['Contents']:
    key = obj['Key']

    #to download the file to local
    client.download_file(s3_bucket, key, key.replace('test',''))
