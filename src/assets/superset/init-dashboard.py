import requests

endpoint = "http://superset-lb.default.svc.cluster.local:8088"
username = "api"
password = "superset#api+User"

def getJwtToken(endpoint, username, password):
    jwt_token = ""
    req_url = endpoint+"/api/v1/security/login"
    #request jwt access token
    req_params = {
    "password": password,
    "provider": "db",
    "refresh": "false",
    "username": username
    }
    resp_token = requests.post(req_url, json=req_params)
    # Check the response
    if resp_token.status_code == 200:
        print("APP-INFO: Got JWT access token successfully!")
        jwt_token = resp_token.json()["access_token"]
        # print("JWT-Token: " + jwt_token)
    else:
        print("APP-ERROR: Failed requesting JWT access token. Status code:", resp_token.status_code, resp_token.content)
        exit(1)
    return jwt_token

def importDashboard(endpoint, jwt_token, filePath):
    # Path to the file you want to upload
    post_url = endpoint+"/api/v1/dashboard/import/"
    # Send the file in the request
    files = {'formData': (open(filePath, 'rb'))}
    resp_file = requests.post(post_url, files=files, headers={"Authorization": f"Bearer  {jwt_token}"})
    
    # Check the response
    if resp_file.status_code == 200:
        print("APP-INFO: File uploaded successfully!")
    else:
        print("APP-ERROR: Failed uploading the file. Status code:", resp_file.status_code, resp_file.content)
        exit(1)

try: 
    jwt_token = getJwtToken(endpoint=endpoint, username=username, password=password)
    importDashboard(endpoint=endpoint, jwt_token=jwt_token, filePath="/scripts/dashboard_export.zip")
    print("APP-INFO: Finished job")
    exit(0)
except Exception as e:
    print("APP-EXEPTION: ", e)
    exit(1)

