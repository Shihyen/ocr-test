# importing the requests library 
import requests 
import json
  

access_token = None
def get_auth_header():
    global access_token
    header = {}
    if not access_token:
        access_token = get_access_token()
    header["accept"] = "application/json"
    header["Authorization"] = "{} {}".format(access_token["token_type"], access_token["access_token"])
    header["Content-Type"] = "application/json"
    return header


def get_access_token():
    url = "https://dev-member-api.cwg.tw/v1.0/client/token"
    payload = {
        "client_id": 4,
        "client_secret": 'DUV4ABnktbs2eN30de8CyWKB9kPCeEVDxwWZxJyk'
    }
    res = requests.post(url = url, data = payload) 
    data = json.loads(res.text)
    if data['success']:
        return data['items'][0]
    else:
        return None

def check_email_exists(email):
    url = "https://dev-member-api.cwg.tw/v1.0/member/email/exist"
    payload = {
        "email": email
    }
    res = requests.post(url = url, json = payload, headers=get_auth_header()) 
    data = json.loads(res.text)
    print(data)

email = 'shihyen@cw.com.tw'

check_email_exists(email)



