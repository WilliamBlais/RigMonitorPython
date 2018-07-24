import json
import sys
from urllib.request import urlopen


class BMiner(object):
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password

    def getData(self):
        rig_json_data = []
        # Connect and handle exceptions
        try:
            rig_data = urlopen(f'http://{self.host}:{self.port}/api/status', timeout=10)
            # Load the rig_data in the json format into rig_json_data
            rig_json_data = json.loads(rig_data.read().decode("utf-8"))
        except Exception as x:
            print("Error: Could not connect to rig. Please check the configuration file.")
            input("Press enter to exit")
            sys.exit(1)

        return rig_json_data

    def getStats(self):
        data = []
        rig_json_data = self.getData()
        try:
            # Insert gpu measurement
            rig_hashrate = 0;
            gpu_data = []
            for miner in rig_json_data["miners"]:
                gpu = [
                    {
                        "temperature": float(rig_json_data["miners"][miner]['device']["temperature"]),
                        "fan": float(rig_json_data["miners"][miner]['device']['fan_speed']),
                        "power": int(rig_json_data["miners"][miner]['device']['power']),
                        "main_hashrate": float(rig_json_data["miners"][miner]['solver']['solution_rate'])
                    }
                ]
                gpu_data.append(gpu)
                rig_hashrate = rig_hashrate + rig_json_data["miners"][miner]['solver']['solution_rate']

            # Insert miner measurement
            miner_data = [
                {
                    "main_hashrate": float(rig_hashrate),
                    "main_accepted_shares": int(rig_json_data['stratum']['accepted_shares']),
                    "main_rejected_shares": int(rig_json_data['stratum']['rejected_shares']),
                    "current_mining_pool": str(rig_json_data['algorithm']),
                }
            ]

            data = [{"gpu": gpu_data, "miner": miner_data}]
        except Exception as x:
            print("Failed to decode miner data " + str(x))
            input("Press enter to exit")
            sys.exit(1)

        return data
