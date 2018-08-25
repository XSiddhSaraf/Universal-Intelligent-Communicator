import boto3
client = boto3.client('s3')

#if your bucket name is mybucket and the file path is test/abc.txt
#then the Bucket='mybucket' Prefix='test'

resp = client.list_objects_v2(Bucket="<your bucket name>", Prefix="<prefix of the s3 folder>") 

for obj in resp['Contents']:
    key = obj['Key']
    #to read s3 file contents as String
    response = client.get_object(Bucket="<your bucket name>",
                         Key=key)
    print(response['Body'].read().decode('utf-8'))

    #to download the file to local
    client.download_file('<your bucket name>', key, key.replace('test',''))
