import json
import socket
import sys


class ClaymoreMiner(object):
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password

    def getData(self):
        try:
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)

            # Connect the socket to the port where the server is listening
            self.sock.connect((self.host, self.port))

            if self.password.strip():
                command = '{"id":0,"jsonrpc":"2.0","method":"miner_getstat2","psw":' + str(self.password) + '}\n'
            else:
                command = '{"id":0,"jsonrpc":"2.0","method":"miner_getstat2"}\n'

                # Send data
            self.sock.sendall(command.encode())

            # receive data
            data = self.sock.recv(12000)

            # Close socket
            self.sock.close()

            return data

        except socket.error as msg:
            print("Socket error: {0}".format(msg))
            input("Press enter to exit")
            sys.exit(1)

    def getStats(self):
        try:
            data = []
            raw_data = self.getData()
            rig_json_data = json.loads(raw_data)

            # running time, in minutes
            running_time = int(rig_json_data['result'][1]);

            # total ETH hashrate in MH/s, number of ETH shares, number of ETH rejected shares.
            rig_json_data_2_splitted = rig_json_data['result'][2].split(";");

            main_hashrate = float(rig_json_data_2_splitted[0]) / 1000.0;
            main_shares = int(rig_json_data_2_splitted[1]);
            main_rejected_shares = int(rig_json_data_2_splitted[2]);

            # detailed ETH hashrate for all GPUs.
            main_hashrate_gpus = rig_json_data['result'][3].split(";");
            for index, hashrate in enumerate(main_hashrate_gpus):
                if hashrate != "off":
                    main_hashrate_gpus[index] = float(hashrate) / 1000.0;
                else:
                    main_hashrate_gpus[index] = 0.0;  # float

            # total DCR hashrate in MH/s, number of DCR shares, number of DCR rejected shares.
            rig_json_data_4_splitted = rig_json_data['result'][4].split(";");

            dual_hashrate = float(rig_json_data_4_splitted[0]) / 1000.0;
            dual_shares = int(rig_json_data_4_splitted[1]);
            dual_rejected_shares = int(rig_json_data_4_splitted[2]);

            # detailed DCR hashrate for all GPUs.
            dual_hashrate_gpus = rig_json_data['result'][5].split(";");
            for index, hashrate in enumerate(dual_hashrate_gpus):
                if hashrate != "off":
                    dual_hashrate_gpus[index] = float(hashrate) / 1000.0;
                else:
                    dual_hashrate_gpus[index] = 0.0;  # float

            # Temperature and Fan speed(%) pairs for all GPUs.
            temperature_gpus = []
            fan_gpus = []
            temperature_fan_gpus = rig_json_data['result'][6].split(";");
            for index, value in enumerate(temperature_fan_gpus):
                if index % 2 == 0:
                    temperature_gpus.append(float(value));
                else:
                    fan_gpus.append(float(value));

            # current mining pool. For dual mode, there will be two pools here.
            current_mining_pool = str(rig_json_data['result'][7]);

            # number of ETH invalid shares, number of ETH pool switches, number of DCR invalid shares, number of DCR pool switches.
            rig_json_data_8_splitted = rig_json_data['result'][8].split(";");
            main_invalid_shares = int(rig_json_data_8_splitted[0]);
            main_pool_switches = int(rig_json_data_8_splitted[1]);
            dual_invalid_shares = int(rig_json_data_8_splitted[2]);
            dual_pool_switches = int(rig_json_data_8_splitted[3]);

            # ETH accepted shares for every GPU.
            main_accepted_shares_gpus = rig_json_data['result'][9].split(";");
            for index, value in enumerate(main_accepted_shares_gpus):
                main_accepted_shares_gpus[index] = int(value);

            # ETH rejected shares for every GPU.
            main_rejected_shares_gpus = rig_json_data['result'][10].split(";");
            for index, value in enumerate(main_rejected_shares_gpus):
                main_rejected_shares_gpus[index] = int(value);

            # ETH invalid shares for every GPU.
            main_invalid_shares_gpus = rig_json_data['result'][11].split(";");
            for index, value in enumerate(main_invalid_shares_gpus):
                main_invalid_shares_gpus[index] = int(value);

            # DCR accepted shares for every GPU.
            dual_accepted_shares_gpus = rig_json_data['result'][12].split(";");
            for index, value in enumerate(dual_accepted_shares_gpus):
                dual_accepted_shares_gpus[index] = int(value);

            # DCR rejected shares for every GPU.
            dual_rejected_shares_gpus = rig_json_data['result'][13].split(";");
            for index, value in enumerate(dual_rejected_shares_gpus):
                dual_rejected_shares_gpus[index] = int(value);

            # DCR invalid shares for every GPU.
            dual_invalid_shares_gpus = rig_json_data['result'][14].split(";");
            for index, value in enumerate(dual_invalid_shares_gpus):
                dual_invalid_shares_gpus[index] = int(value);

            # Determine the gpu_count
            gpu_count = len(main_hashrate_gpus)

            # Insert gpu measurement
            i = 00
            gpu_data = []
            while (i < gpu_count):
                gpu = [
                    {
                        "temperature": temperature_gpus[i],
                        "fan": fan_gpus[i],
                        "main_hashrate": main_hashrate_gpus[i],
                        "main_accepted_shares": main_accepted_shares_gpus[i],
                        "main_rejected_shares": main_rejected_shares_gpus[i],
                        "main_invalid_shares": main_invalid_shares_gpus[i],
                        "dual_hashrate": dual_hashrate_gpus[i],
                        "dual_accepted_shares": dual_accepted_shares_gpus[i],
                        "dual_rejected_shares": dual_rejected_shares_gpus[i],
                        "dual_invalid_shares": dual_invalid_shares_gpus[i]
                    }
                ]
                gpu_data.append(gpu)
                i = i + 1

            # Insert miner measurement
            miner_data = [
                {
                    "running_time": running_time,
                    "current_mining_pool": current_mining_pool,
                    "main_hashrate": main_hashrate,
                    "main_accepted_shares": main_shares,
                    "main_rejected_shares": main_rejected_shares,
                    "main_invalid_shares": main_invalid_shares,
                    "main_pool_switches": main_pool_switches,
                    "dual_hashrate": dual_hashrate,
                    "dual_accepted_shares": dual_shares,
                    "dual_rejected_shares": dual_rejected_shares,
                    "dual_invalid_shares": dual_invalid_shares,
                    "dual_pool_switches": dual_pool_switches
                }
            ]

            data = [{"gpu": gpu_data, "miner": miner_data}]
        except Exception as x:
            print("Failed to decode miner data " + str(x))
            input("Press enter to exit")
            sys.exit(1)
        return data
