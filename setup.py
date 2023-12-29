#!/usr/bin/env python3
import os,glob,datetime,argparse
import base64,json
import hashlib,codecs,struct
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from pypush_gsa_icloud import icloud_login_mobileme, generate_anisette_headers

'''
  This file allows user to setup auth data (first time setup)
'''

def getAuth(regenerate=False, second_factor='sms'):
  CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data/auth.json"
  mobileme = icloud_login_mobileme(second_factor=second_factor)
  j = {'dsid': mobileme['dsid'], 'searchPartyToken': mobileme['delegates']['com.apple.mobileme']['service-data']['tokens']['searchPartyToken']}
  with open(CONFIG_PATH, "w") as f: json.dump(j, f)
  return (j['dsid'], j['searchPartyToken'])

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--regen', help='regenerate search-party-token', action='store_true')
  parser.add_argument('-t', '--trusteddevice', help='use trusted device for 2FA instead of SMS', action='store_true')
  args = parser.parse_args()

  # fake data, only for testing if the credentials work or not
  unixEpoch = int(datetime.datetime.now().strftime('%s'))
  startdate = unixEpoch - (60 * 60 * 24)
  data = {
    "search": [
      {
        "startDate": startdate * 1000,
        "endDate": unixEpoch * 1000,
        "ids": []
      }
    ]
  }

  r = requests.post("https://gateway.icloud.com/acsnservice/fetch",
      auth=getAuth(regenerate=args.regen, second_factor='trusted_device' if args.trusteddevice else 'sms'),
      headers=generate_anisette_headers(),
      json=data)
  res = json.loads(r.content.decode())['results']
  print(f'Response status code: {r.status_code}')
