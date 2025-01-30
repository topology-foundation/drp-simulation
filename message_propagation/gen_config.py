#!/usr/bin/env python3
import os
import re
import argparse
from gen_topology import generate_topology


parser = argparse.ArgumentParser(prog="gen_config", description="Generate shadow.yaml")
parser.add_argument(
    "-n",
    "--nodes",
    help="Number of nodes in the network",
    type=int,
    default=8,
)
parser.add_argument(
    "-b",
    "--bootstraps",
    help="Number of bootstrap nodes in the network (<= 8)",
    type=int,
    default=1,
)
parser.add_argument(
    "-f",
    "--file",
    help="Output .yaml file",
    type=str,
    default="shadow.yaml",
)
parser.add_argument(
    "--same-region",
    help="Put all nodes in the same region",
    action="store_true",
)
parser.add_argument(
    "--all-reliable",
    help="Make all nodes reliable",
    action="store_true",
)
parser.add_argument(
    "--bootstrap-end-time",
    help="Bootstrap end time {amount}s/min/h",
    type=str,
    default="10s",
)
parser.add_argument(
    "--heartbeat",
    help="Heartbeat interval {amount}s/min/h",
    type=str,
    default="10s",
)
parser.add_argument(
    "--duration",
    help="Duration of the simulation {amount}s/min/h",
    type=str,
    default="1min",
)
args = parser.parse_args()

# validate the time args
assert re.match(
    r"^\d+(s|min|h)$", args.bootstrap_end_time
), "Bootstrap end time must follow format"
assert re.match(
    r"^\d+(s|min|h)$", args.heartbeat
), "Heartbeat interval must follow format"
assert re.match(r"^\d+(s|min|h)$", args.duration), "Duration must follow format"

DIRNAME = os.path.dirname(os.path.abspath(__file__))

ip_addrs = generate_topology(
    args.bootstraps, args.nodes, args.same_region, args.all_reliable
)

assert os.path.exists("network_topology.gml")

with open(args.file, "w", encoding="utf8") as f:
    f.write(
        f"""general:
  bootstrap_end_time: {args.bootstrap_end_time}
  heartbeat_interval: {args.heartbeat}
  stop_time: {args.duration}
  progress: true
  model_unblocked_syscall_latency: true
network:
  use_shortest_path: false
  graph:
    type: gml
    file:
      path: network_topology.gml

hosts:
"""
    )

    bootstrap_addresses = []
    for i in range(args.bootstraps):
        ip_addr = ip_addrs[i]
        bootstrap_addresses.append(ip_addr)
        f.write(
            f"""  bootstrap{i+1}:
    ip_addr: {ip_addr}
    network_node_id: {i}
    processes:
    - path: /usr/bin/node
      args: {DIRNAME}/generic_node.js -s bootstrap{i+1} --ips {ip_addr}
      environment:
        DEBUG: "*"
      expected_final_state: running
"""
        )

    for i in range(args.nodes):
        ip_addr = ip_addrs[args.bootstraps + i]
        f.write(
            f"""  node{i+1}:
    ip_addr: {ip_addr}
    network_node_id: {args.bootstraps + i}
    processes:
    - path: /usr/bin/node
      args: {DIRNAME}/generic_node.js -s node{i+1} --ips {",".join(bootstrap_addresses)}
      environment:
        DEBUG: "*"
      start_time: 5s
      expected_final_state: running
"""
        )
