import xml.etree.ElementTree as ET
import csv
import numpy as np

def parse_dynamic_flow(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    stats = []
    for flow in root.findall('.//FlowStats/Flow'):
        tx = int(flow.get('txPackets'))
        rx = int(flow.get('rxPackets'))
        delay = int(float(flow.get('delaySum').replace('ns', '')))
        jitter = int(float(flow.get('jitterSum').replace('ns', '')))
        if tx > 0:
            stats.append({'id': int(flow.get('flowId')), 'lost': tx-rx, 'delay': delay, 'jitter': jitter})

    # Milestone 2: Explicitly label the top 10% worst delays as "Fault"
    delays = sorted([s['delay'] for s in stats])
    boundary = delays[int(len(delays) * 0.90)]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['flow_id', 'lost_packets', 'delay_sum_ns', 'jitter_ns', 'label'])
        writer.writeheader()
        for s in stats:
            label = 1 if s['delay'] >= boundary else 0
            writer.writerow({'flow_id': s['id'], 'lost_packets': s['lost'], 'delay_sum_ns': s['delay'], 'jitter_ns': s['jitter'], 'label': label})

if __name__ == "__main__":
    parse_dynamic_flow('results/dynamic_report.xml', 'results/training_data.csv')
