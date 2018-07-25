import json
from urllib.request import urlopen


class Castxmr(object):
    def __init__(self, host, port, password, client):
        self.host = host
        self.port = port
        self.password = password
        self.client = client

    def getData(self):
        rig_json_data = []
        # Connect and handle exceptions
        try:
            rig_data = urlopen(f'http://{self.host}:{self.port}', timeout=10)
            # Load the rig_data in the json format into rig_json_data
            rig_json_data = json.loads(rig_data.read().decode("utf-8"))
        except Exception as x:
            print("Error: Could not connect to rig. Please check the configuration file.")

        return rig_json_data

    def getStats(self):
        data = []
        rig_json_data = []
        rig_json_data = self.getData()

        if rig_json_data:
            try:
                # Insert gpu measurement
                rig_hashrate = 0
                gpu_data = []
                for device in rig_json_data["devices"]:
                    gpu = [
                        {
                            "temperature": float(device["gpu_temperature"]),
                            "fan": float(device["gpu_fan_rpm"]),
                            "main_hashrate": float(device["hash_rate"] / 1000)
                        }
                    ]
                    gpu_data.append(gpu)

                # Insert miner measurement
                miner_data = [
                    {
                        "main_hashrate": float(rig_json_data["total_hash_rate"] / 1000),
                        "main_accepted_shares": int(rig_json_data['shares']['num_accepted']),
                        "main_rejected_shares": int(rig_json_data['shares']['num_rejected']),
                        "main_invalid_shares": int(rig_json_data['shares']['num_invalid']),
                        "main_pool_switches": int(rig_json_data['pool']['reconnects']),
                        "current_mining_pool": str(rig_json_data['pool']['server']),
                    }
                ]

                data = [{"gpu": gpu_data, "miner": miner_data}]
            except Exception as x:
                print("Failed to decode miner data " + str(x))
                self.client.captureException()

        return data
