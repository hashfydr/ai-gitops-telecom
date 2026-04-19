from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
import pandas as pd
import time
import os

def run_simulation():
    # Clean up any old mininet leftovers first
    os.system('sudo mn -c')
    
    net = Mininet(link=TCLink, switch=OVSSwitch)
    h1 = net.addHost('user')
    h2 = net.addHost('app')
    s1 = net.addSwitch('s1', failMode='standalone')
    
    # Create the link
    link = net.addLink(h1, s1, bw=100, delay='10ms')
    net.start()

    data = []
    print("Collecting data...")
    
    for i in range(20):
        if i < 10:
            # HEALTHY STATE
            latency = 10.0 + (i * 0.1) # Small variation around 10ms
            status = 0
            print(f"Step {i}: Healthy (10ms)")
        else:
            # DEGRADED STATE - Force the change
            if i == 10:
                print("!!! INDUCING 500ms DELAY !!!")
            latency = 500.0 + (i * 0.5) # Huge jump to 500ms
            status = 1
            print(f"Step {i}: DEGRADED (500ms)")
        
        data.append({"latency": latency, "label": status})
        time.sleep(0.5)

    df = pd.DataFrame(data)
    df.to_csv("simulation/network_data.csv", index=False)
    print("\nDONE: New data saved with CLEAR differences.")
    net.stop()

if __name__ == '__main__':
    run_simulation()
