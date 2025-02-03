# Message Propagation

First, generate `shadow.yaml` using `gen_config.py`.

```bash
cd message_propagation
pip install -r requirements.txt
./gen_config.py
```

All options of `gen_config.py` are shown below.

```bash
usage: gen_config [-h] [-s SEED] [-n NODES] [-b BOOTSTRAPS] [-f FILE] [--same-region]
                  [--all-reliable] [--bootstrap-end-time BOOTSTRAP_END_TIME]
                  [--heartbeat HEARTBEAT] [--duration DURATION]
                  [--other-region OTHER_REGION] [--single-message]

Generate shadow.yaml

optional arguments:
  -h, --help            show this help message and exit
  -s SEED, --seed SEED  Seed for the simulation
  -n NODES, --nodes NODES
                        Number of nodes in the network
  -b BOOTSTRAPS, --bootstraps BOOTSTRAPS
                        Number of bootstrap nodes in the network (<= 8)
  -f FILE, --file FILE  Output .yaml file
  --same-region         Put all nodes in the same region
  --all-reliable        Make all nodes reliable
  --bootstrap-end-time BOOTSTRAP_END_TIME
                        Bootstrap end time {amount}s/min/h
  --heartbeat HEARTBEAT
                        Heartbeat interval {amount}s/min/h
  --duration DURATION   Duration of the simulation {amount}s/min/h
  --other-region OTHER_REGION
                        Number of nodes in a different region if --same-region is set
  --single-message      Send a single message from each node in the interval of 10s
```

Default number of nodes is 8 (1 for each region), and 1 bootstrap node located in Europe.

Then, run the simulation.

```bash
rm -rf shadow.data && shadow shadow.yaml > shadow.log
```

Finally, parse the log files. Currently, only parsing the logs created with `--single-message` is supported.

```bash
./parse_single_message_from_each_node.py
```

The plot will be saved in `plots/message_propagation.png`.
