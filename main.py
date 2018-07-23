import configparser
import json
import sys
import time

import requests

from miners.bminer import BMiner
from miners.claymore import ClaymoreMiner

version = '0.1'
api_url = 'http://127.0.0.1:8000/api/external'

# Load Config
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

api_key = config.get('GENERAL', 'API_KEY')
if not api_key.strip():
    print('Please insert the config file within the same folder of this program.')
    sys.exit(1)

type = config.get('MINER', 'TYPE')
host = config.get('MINER', 'HOST')
port = int(config.get('MINER', 'PORT'))
password = config.get('MINER', 'PASSWORD')

print(f'Welcome to RigMonitor version {version}')
print('Please send any feedback or bug report to contact@ostrich.media')

while 1:
    print(f'Connecting to {type}...')

    # Claymore
    if type == 'CLAYMORE':
        data = ClaymoreMiner(host, port, password).getStats()
    # BMiner
    if type == 'BMINER':
        data = BMiner(host, port, password).getStats()

    if data is None:
        print('Miner Type not supported or no response from getStats().')
        sys.exit(1)

    # add identification to data
    identification = [{
        'api_key': api_key,
        'rig_id': config.get('GENERAL', 'RIG_ID'),
        'miner': type,
        'version': version
    }]
    data[0]['identification'] = identification

    # Debug
    if config.getboolean('GENERAL', 'DEBUG'):
        print(json.dumps(data))
    else:
        print(f'Data successfully fetched from {type}')

    # Send data to API
    try:
        r = requests.post(f'{api_url}/ingest', json=data)
    except Exception as e:
        print('Failed to send data to RigMonitor... Retrying.' + str(e))

    if r.status_code != 200:
        if r.status_code == 400:
            print(r.json()['message'])
        else:
            print(f'Failed to send data to RigMonitor (status_code {r.status_code})... Retrying.')
    else:
        print(r.json()['message'])

    print('Waiting 1 minute')
    time.sleep(60)
