#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/applications-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include "ns3/internet-module.h"
#include "ns3/flow-monitor-module.h"

using namespace ns3;

int main (int argc, char *argv[])
{
    NodeContainer wifiStaNodes;
    wifiStaNodes.Create (16);
    NodeContainer wifiApNode;
    wifiApNode.Create (1);

    YansWifiChannelHelper channel = YansWifiChannelHelper::Default ();
    YansWifiPhyHelper phy;
    phy.SetChannel (channel.Create ());

    WifiHelper wifi;
    WifiMacHelper mac;
    Ssid ssid = Ssid ("ns-3-ssid");

    mac.SetType ("ns3::StaWifiMac", "Ssid", SsidValue (ssid));
    NetDeviceContainer staDevices = wifi.Install (phy, mac, wifiStaNodes);

    mac.SetType ("ns3::ApWifiMac", "Ssid", SsidValue (ssid));
    NetDeviceContainer apDevices = wifi.Install (phy, mac, wifiApNode);

    // VIBE UPGRADE: Mobility
    MobilityHelper mobility;
    mobility.SetPositionAllocator ("ns3::GridPositionAllocator",
                                  "MinX", DoubleValue (0.0), "MinY", DoubleValue (0.0));
    
    // AP is at (0,0). STAs move at random speeds
    mobility.SetMobilityModel ("ns3::ConstantVelocityMobilityModel");
    mobility.Install (wifiStaNodes);
    mobility.Install (wifiApNode);

    for (uint32_t i = 0; i < wifiStaNodes.GetN(); ++i) {
        Ptr<ConstantVelocityMobilityModel> cvmm = wifiStaNodes.Get(i)->GetObject<ConstantVelocityMobilityModel>();
        if (i % 4 == 0) {
            cvmm->SetVelocity (Vector (20.0, 0.0, 0.0)); // Moving away fast (The Fault/High Risk)
        } else {
            cvmm->SetVelocity (Vector (2.0, 0.0, 0.0));  // Slow movement (Healthy)
        }
    }

    InternetStackHelper stack;
    stack.Install (wifiApNode);
    stack.Install (wifiStaNodes);

    Ipv4AddressHelper address;
    address.SetBase ("10.1.1.0", "255.255.255.0");
    address.Assign (staDevices);
    address.Assign (apDevices);

    UdpEchoServerHelper echoServer (9);
    echoServer.Install (wifiApNode.Get (0)).Start (Seconds (1.0));

    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll ();

    Simulator::Stop (Seconds (10.0));
    Simulator::Run ();
    monitor->SerializeToXmlFile ("results/mobility_report.xml", true, true);
    Simulator::Destroy ();
    return 0;
}
