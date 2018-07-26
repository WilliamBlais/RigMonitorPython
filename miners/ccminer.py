# Credits: https://github.com/JamesSmith2/EthMonitoringLinux/blob/master/miners/ccminer_alexis.py
import socket


class Ccminer(object):
    def __init__(self, host, port, password, client):
        self.host = host
        self.port = port
        self.password = password
        self.client = client

    def getCommand(self, command):
        try:
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)

            # Connect the socket to the port where the server is listening
            server_address = (self.host, self.port)
            self.sock.connect(server_address)

            # Send data
            self.sock.sendall(command.encode())

            # receive data
            data = self.sock.recv(12000)

            # Close socket
            self.sock.close()

            return data

        except socket.error as msg:
            print("Socket error: {0}".format(msg))

    def getStats(self):
        data = []
        miner_data = []
        gpu_data_to_api = []

        try:
            summary_data = self.getCommand("summary|")
            if summary_data is not None:
                summary_response = summary_data.decode().split(";")

                pool_data = self.getCommand("pool|")
                pool_response = pool_data.decode().split(";")

                if len(summary_response) > 0:
                    # Insert miner measurement
                    miner_data = [
                        {
                            "running_time": summary_response[14].split('=')[1],
                            "current_mining_pool": pool_response[0].split("=")[1],
                            "main_hashrate": summary_response[5].split("=")[1],
                            "main_accepted_shares": summary_response[7].split('=')[1],
                            "main_rejected_shares": summary_response[8].split('=')[1],
                            "version": float(summary_response[1].split("=")[1])
                        }
                    ]

                """ GPU RESPONSE """
                gpu_data = self.getCommand("threads|")
                gpu_response = gpu_data.decode().split("|")

                if 1 == 1:
                    for gpu in gpu_response:
                        gpu_data = gpu.split(";")

                        if len(gpu_data) == 19:
                            hashrate = 0
                            wattage = 0

                            if miner_data[0]['version'] > 2.0:
                                hashrate = float(gpu_data[11].split('=')[1]) * 1000
                                wattage = (int(gpu_data[4].split('=')[1]) / 1000)
                            else:
                                hashrate = float(gpu_data[8].split('=')[1]) * 1000
                                wattage = (int(gpu_data[4].split('=')[1]) / 1000)

                            gpu_to_api = [
                                {
                                    "temperature": gpu_data[3].split('=')[1],
                                    "fan": gpu_data[5].split('=')[1],
                                    "power": wattage,
                                    "main_hashrate": hashrate,
                                }
                            ]
                        gpu_data_to_api.append(gpu_to_api)
                data = [{"gpu": gpu_data_to_api, "miner": miner_data}]
        except Exception as x:
            self.client.captureException()
            print("Failed to decode miner data " + str(x))
        return data
