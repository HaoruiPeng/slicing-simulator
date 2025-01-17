import os
import numpy as np
from multiprocessing import Pool
import json
import time

PROCESSES = 4

with open('default_config.json') as config_file:
    config = json.load(config_file)

with open('nodes/node_config.json') as node_config:
    node = json.load(node_config)

total_pilots = config.get("no_pilots")
slot_time = config.get("frame_length")

mmtc_period = node.get("deadline_par").get(node.get("mmtc").get("deadline"))
mmtc_pilot = 1

period = {"long": 10,
          "short": 1}
pilots = {"high": 3,
          "low": 1}

reliability = "high"
deadline = "long"

urllc_period = period[deadline]
urllc_pilot = pilots[reliability]

SEED = round(time.time() / 100)


def rho2urllc(rho):
    urllc = rho * total_pilots * urllc_period / (urllc_pilot * slot_time)
    return int(round(urllc))


def rho2mmtc(rho):
    mmtc = rho * total_pilots * mmtc_period / (mmtc_pilot * slot_time)
    return int(round(mmtc))


simulations = []

urllc_load = 0.5
no_urllc = rho2urllc(urllc_load)
mmtc_loads = np.linspace(0.1, 1.5, 15)
no_mmtc_list = [rho2mmtc(rho) for rho in mmtc_loads]

scheduler = "RR_F"
for no_mmtc in no_mmtc_list:
    SEED += np.random.randint(100)
    simulations.append("python3 main.py \
                        --scheduler {} --reliability {} --deadline {} \
                        --urllc_node {} --mmtc_node {} \
                        --seed {}".format(
        scheduler, reliability, deadline, no_urllc, no_mmtc, SEED))

scheduler = "RR_RR"
for no_mmtc in no_mmtc_list:
    SEED += np.random.randint(100)
    simulations.append("python3 main.py \
                            --scheduler {} --reliability {} --deadline {} \
                            --urllc_node {} --mmtc_node {} \
                            --seed {}".format(
        scheduler, reliability, deadline, no_urllc, no_mmtc, SEED))

pool = Pool(processes=PROCESSES)
for k, simulation in enumerate(simulations):
    pool.apply_async(os.system, (simulation,))

pool.close()
pool.join()
print("All simulations completed")
