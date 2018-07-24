import json
import sys
import time

import requests
from raven import Client

from miners.bminer import BMiner
from miners.claymore import ClaymoreMiner

# Sentry
client = Client('https://0813bc02480642a99a2338ef50250072:41bf8af4deea4c3b9a7799582e194546@sentry.io/1248845')

version = '0.1'
api_url = 'https://api.rigmonitor.io/api/external'


try:
    config_raw = open('config.json')
    config = json.load(config_raw)
except:
    print(
        'Could not load config file. Please download your config.json file from RigMonitor.io and copy it in this program directory.')
    input("Press enter to exit")
    sys.exit(1)

if not config['api_key']:
    print(
        'Missing API key. Please download your config.json file from RigMonitor.io and copy it in this program directory.')
    input("Press enter to exit")
    sys.exit(1)

client.user_context({
    'api_key': config['api_key'],
    'rigs': config['rigs'],
    'version': version
})


print(f'Welcome to RigMonitor.io version {version}')
print('Please send any feedback or bug report to contact@ostrich.media')
while 1:
    for rig in config["rigs"]:
        print(f'Connecting to rig #{rig["id"]} {rig["type"]}...')
        data = []
        # Claymore
        if rig['type'] == 'CLAYMORE':
            data = ClaymoreMiner(rig['host'], rig['port'], rig['password'], client).getStats()
        # BMiner
        if rig['type'] == 'BMINER':
            data = BMiner(rig['host'], rig['port'], rig['password'], client).getStats()

        if not data:
            print('Miner Type not supported or no response from getStats().')
        else:
            # add identification to data
            identification = [{
                'api_key': config['api_key'],
                'rig_id': rig['id'],
                'miner': rig['type'],
                'version': version
            }]
            data[0]['identification'] = identification

            # Debug
            if config['debug']:
                print(json.dumps(data))
            else:
                print(f'Data successfully fetched from {rig["type"]}')

            # Send data to API
            try:
                r = requests.post(f'{api_url}/ingest', json=data)
            except Exception as e:
                client.captureException()
                print('Failed to send data to RigMonitor... Retrying.' + str(e))

            if r.status_code != 200:
                if r.status_code == 400:
                    print(r.json()['message'])
                else:
                    print(f'Failed to send data to RigMonitor (status_code {r.status_code})... Retrying.')
            else:
                print(r.json()['message'])

    print('Waiting')
    time.sleep(60 / len(config['rigs']))
