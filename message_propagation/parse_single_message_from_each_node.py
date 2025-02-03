#!/usr/bin/env python3
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from defaults import REGIONS

patterns = {
    "received_message": re.compile(
        r"Received message from (?P<peer_id>[A-Za-z0-9]+): Message from \1, at (?P<timestamp>\d+)"
    ),
    "send_message": re.compile(
        r"Sending message from (?P<peer_id>[A-Za-z0-9]+) at (?P<timestamp>\d+)"
    ),
}

DIRNAME = os.path.dirname(os.path.abspath(__file__))

shadow_data_dir = "shadow.data"
assert os.path.exists(
    os.path.join(DIRNAME, shadow_data_dir)
), f"{shadow_data_dir} directory not found"

LOG_DIR = os.path.join(DIRNAME, f"{shadow_data_dir}/hosts")

messages_received = {}
messages_sent = {}

def process_log_file(file_path):
    """Process a single log file"""
    node_name = os.path.basename(os.path.dirname(file_path))  # Extract node name
    print(f"Processing {node_name}...")
    with open(file_path, "r", encoding="utf8") as file:
        for line in file:
            for key, pattern in patterns.items():
                match = pattern.match(line)
                if match:
                    if key in ("received_message", "send_message"):
                        message = {
                            "peer_id": match.group("peer_id"),
                            "timestamp": int(match.group("timestamp")),
                        }
                        if key == "received_message":
                            messages_received.setdefault(node_name, []).append(message)
                        else:
                            messages_sent.setdefault(node_name, []).append(message)


def process_logs(directory):
    """Process all log files in the given directory"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "node.1000.stdout":  # Only process stdout files
                file_path = os.path.join(root, file)
                process_log_file(file_path)


process_logs(LOG_DIR)

# Convert lists into DataFrame for easier analysis
sent_df = pd.DataFrame(
    [
        {"node": REGIONS[int(node[node.find("node") + 4:]) - 1], **msg}
        for node, messages in messages_sent.items()
        for msg in messages
    ]
)
received_df = pd.DataFrame(
    [
        {"node": node, **msg}
        for node, messages in messages_received.items()
        for msg in messages
    ]
)

print("\n\nSent DataFrame:")
print(sent_df)
print("\n\nReceived DataFrame:")
print(received_df)

# Convert timestamps and message numbers to integer types
sent_df["timestamp"] = sent_df["timestamp"].astype(int)
received_df["timestamp"] = received_df["timestamp"].astype(int)

num_of_nodes = len(sent_df["peer_id"].unique())

# get the received times for each message
received_times = received_df.groupby("peer_id")["timestamp"].apply(lambda x: sorted(list(x))).reset_index()

result_to_all = {}
result_to_all_but_one = {}

assert len(received_times) == num_of_nodes
for i in range(num_of_nodes):
    assert len(received_times["timestamp"]) == num_of_nodes
    send_timestamp = sent_df[sent_df["peer_id"] == received_times["peer_id"][i]]["timestamp"].values
    send_name = sent_df[sent_df["peer_id"] == received_times["peer_id"][i]]["node"].values[0]

    time_to_all_but_one = sum(received_times["timestamp"][i][:-1] - send_timestamp)
    time_to_all = sum(received_times["timestamp"][i] - send_timestamp)
    print(f"Time to all but one for {send_name}: {time_to_all_but_one}")
    print(f"Time to all for {send_name}: {time_to_all}")
    result_to_all[send_name] = time_to_all / num_of_nodes
    result_to_all_but_one[send_name] = time_to_all_but_one / (num_of_nodes - 1)


result_to_all = dict(sorted(result_to_all.items(), key=lambda item: item[1]))
result_to_all_but_one = dict(sorted(result_to_all_but_one.items(), key=lambda item: item[1]))

fig, ax = plt.subplots(figsize=(10, 6))

width = 0.4  # Adjust width for better visibility
x = np.arange(len(result_to_all_but_one))

ax.bar(x - width/2, result_to_all_but_one.values(), width=width, color="tab:blue", label="Avg. time to all but one", alpha=0.7)
ax.bar(x + width/2, result_to_all.values(), width=width, color="tab:red", label="Avg. time to all", alpha=0.5)


ax.set_xticks(x)
ax.set_xticklabels(result_to_all_but_one.keys(), rotation=45)

# Labels and title
ax.set_xlabel("Node sending a message")
ax.set_ylabel("Time to reach (ms)")
ax.set_title("Message Propagation Time")

# Legend
ax.legend(loc="upper left")

plt.tight_layout()
fig.savefig(os.path.join(DIRNAME, "plots/message_propagation.png"), dpi=300)
plt.close(fig)
