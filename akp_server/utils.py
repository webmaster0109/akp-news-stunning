import boto3

def botofun():
  client = boto3.client(
      's3',
      endpoint_url='https://e160dbaa7bba5fcb8adecf4dfc188c7d.r2.cloudflarestorage.com',
      aws_access_key_id='5ed6f04c968b1b147486cde1396ea200',
      aws_secret_access_key='1b5d57bfa1fc00bd6fd43c3728874ae5332c641b4997d7a6465b3f5972dbc5b7',
      region_name='auto',
      config=boto3.session.Config(signature_version='s3v4')
  )

  # Test connection
  try:
      response = client.list_objects_v2(Bucket='akp')
      print("Connection successful!")
      print(response)
  except Exception as e:
      print(f"Connection failed: {e}")