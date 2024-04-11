#!/usr/bin/env python3
import os,glob,datetime,argparse
import sys,random
import base64,json
import hashlib,codecs,struct
import requests
from flask import Flask, request, jsonify, render_template
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from pypush_gsa_icloud import icloud_login_mobileme, generate_anisette_headers

DEBUG = True

def sha256(data):
  digest = hashlib.new("sha256")
  digest.update(data)
  return digest.digest()

def decrypt(enc_data, algorithm_dkey, mode):
  decryptor = Cipher(algorithm_dkey, mode, default_backend()).decryptor()
  return decryptor.update(enc_data) + decryptor.finalize()

def decode_tag(data):
  latitude = struct.unpack(">i", data[0:4])[0] / 10000000.0
  longitude = struct.unpack(">i", data[4:8])[0] / 10000000.0
  confidence = int.from_bytes(data[8:9], 'big')
  status = int.from_bytes(data[9:10], 'big')
  return {'lat': latitude, 'lon': longitude, 'conf': confidence, 'status':status}

class NoAuthException(Exception):
  pass

def getAuth():
  CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data/auth.json"
  if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f: j = json.load(f)
  else:
    raise NoAuthException
  return (j['dsid'], j['searchPartyToken'])

# flask app
app = Flask(__name__)

@app.route('/get_locations', methods=['POST'])
def get_locations():
  # Check auth
  try:
    auth_data = getAuth()
  except NoAuthException:
    return jsonify({
      "error": "Cannot find auth.json. Please run setup.py to generate it"
    })
  # Get the JSON body of the request
  data = request.get_json()
  # Extract the 'keys' field from the JSON body
  keys = data.get('keys', [])
  hours = int(data.get('hours', 24))
  table_priv_keys = {}
  table_tag_ids = {}
  for key in keys:
    tag_id = key['tag_id'] # Friendly ID used for internal purpose
    priv_key = key['priv_key'] # Private key in base64
    adv_key = key['adv_key'] # Advertisement key in base64
    adv_hash = key['adv_hash'] # Hashed adv key in base64
    # save to lookup table
    table_tag_ids[adv_hash] = tag_id
    table_priv_keys[adv_hash] = priv_key
  # prepare the request
  unixEpoch = int(datetime.datetime.now().strftime('%s'))
  startdate = unixEpoch - (60 * 60 * hours)
  data = {
    "search": [
      {
        "startDate": startdate * 1000,
        "endDate": unixEpoch * 1000,
        # the server takes adv_hash as ID
        "ids": list(table_tag_ids.keys()),
      }
    ]
  }
  # send the request
  r = requests.post("https://gateway.icloud.com/acsnservice/fetch",
    auth=auth_data,
    headers=generate_anisette_headers(),
    json=data)
  res = json.loads(r.content.decode())
  if DEBUG: app.logger.info(res)
  if r.status_code != 200:
    app.logger.info(f'ERROR: response code from server is {r.status_code}')
    return jsonify({"error": res})
  else:
    response_arr = []
    # decode list of results
    for report in res['results']:
      priv = int.from_bytes(base64.b64decode(table_priv_keys[report['id']]), 'big')
      data = base64.b64decode(report['payload'])
      timestamp = int.from_bytes(data[0:4], 'big') + 978307200
      if timestamp < startdate:
        continue # skip this report if it's outside of search range
      # adapted from https://github.com/hatomist/openhaystack-python, thanks @hatomist!
      try:
        eph_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), data[5:62])
      except:
        continue
      shared_key = ec.derive_private_key(priv, ec.SECP224R1(), default_backend()).exchange(ec.ECDH(), eph_key)
      symmetric_key = sha256(shared_key + b'\x00\x00\x00\x01' + data[5:62])
      decryption_key = symmetric_key[:16]
      iv = symmetric_key[16:]
      enc_data = data[62:72]
      tag = data[72:]
      # decrypt the data
      decrypted = decrypt(enc_data, algorithms.AES(decryption_key), modes.GCM(iv, tag))
      tag = decode_tag(decrypted)
      # write the response
      response_arr.append({
        'timestamp': timestamp,
        'isodatetime': datetime.datetime.fromtimestamp(timestamp).isoformat(),
        'tag_id': table_tag_ids[report['id']],
        'lat': tag['lat'],
        'lon': tag['lon'],
      })
    return jsonify({"results": response_arr})

@app.route('/generate_key', methods=['POST'])
def generate_key():
  tag_id = format(random.getrandbits(64), '016x')
  priv = random.getrandbits(224)
  adv = ec.derive_private_key(priv, ec.SECP224R1(), default_backend()).public_key().public_numbers().x
  # convert to byte array
  priv_bytes = int.to_bytes(priv, 28, 'big')
  adv_bytes = int.to_bytes(adv, 28, 'big')
  # convert to base64
  priv_b64 = base64.b64encode(priv_bytes).decode("ascii")
  adv_b64 = base64.b64encode(adv_bytes).decode("ascii")
  s256_b64 = base64.b64encode(sha256(adv_bytes)).decode("ascii")
  ctype_byte_arr = ', '.join('0x{:02x}'.format(x) for x in adv_bytes)
  # return the result as JSON
  return jsonify({
    'tag_id': tag_id,
    'priv_key': priv_b64,
    'adv_key': adv_b64,
    'adv_hash': s256_b64,
    'ctype_byte_arr': ctype_byte_arr,
  })

@app.route('/')
def root():
  return render_template('index.html')

if __name__ == "__main__":
  app.run(debug=DEBUG, host='0.0.0.0', port=3033, reload=True)