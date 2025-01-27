# DRP simulation

## Prerequisites

- Linux environment
- [Dependencies](https://shadow.github.io/docs/guide/install_dependencies.html)
- [The Shadow Simulator](https://github.com/shadow/shadow)

## Message Propagation

To benchmark message propagation, navigate to [message_propagation/](/message_propagation). First, generate `shadow.yaml` using `gen_config.py`.

```bash
usage: gen_config [-h] [-n NODES] [-b BOOTSTRAPS] [-f FILE]

Generate shadow.yaml

optional arguments:
  -h, --help            show this help message and exit
  -n NODES, --nodes NODES
                        Number of nodes in the network
  -b BOOTSTRAPS, --bootstraps BOOTSTRAPS
                        Number of bootstrap nodes in the network (<= 8)
  -f FILE, --file FILE  Output .yaml file
```

Then, run the simulation.

```bash
rm -rf shadow.data && shadow shadow.yaml > shadow.log
```

Finally, parse the log files.

```bash
./parse.py
```
