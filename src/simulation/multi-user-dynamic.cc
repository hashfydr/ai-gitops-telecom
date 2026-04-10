#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"

using namespace ns3;

int main (int argc, char *argv[])
{
    NodeContainer hub; hub.Create (1);
    NodeContainer users; users.Create (16);

    MobilityHelper mobility;
    mobility.SetPositionAllocator ("ns3::GridPositionAllocator",
                                  "MinX", DoubleValue (0.0), "MinY", DoubleValue (0.0),
                                  "DeltaX", DoubleValue (5.0), "DeltaY", DoubleValue (5.0),
                                  "GridWidth", UintegerValue (4), "LayoutType", StringValue ("RowFirst"));
    mobility.SetMobilityModel ("ns3::ConstantVelocityMobilityModel");
    mobility.Install (users);
    
    // Milestone 2: Severe mobility fault for User 3
    users.Get(3)->GetObject<ConstantVelocityMobilityModel>()->SetVelocity(Vector(150.0, 0, 0));

    PointToPointHelper p2p;
    p2p.SetDeviceAttribute ("DataRate", StringValue ("5Mbps")); // Constrain bandwidth
    p2p.SetChannelAttribute ("Delay", StringValue ("5ms"));

    InternetStackHelper stack;
    stack.Install (hub); stack.Install (users);

    Ipv4AddressHelper address;
    for (uint32_t i = 0; i < users.GetN (); ++i) {
        NetDeviceContainer link = p2p.Install (users.Get (i), hub.Get (0));
        std::ostringstream subnet;
        subnet << "10.1." << i + 1 << ".0";
        address.SetBase (subnet.str().c_str(), "255.255.255.0");
        Ipv4InterfaceContainer interfaces = address.Assign (link);

        UdpEchoClientHelper client (interfaces.GetAddress (1), 9);
        client.SetAttribute ("MaxPackets", UintegerValue (5000));
        client.SetAttribute ("Interval", TimeValue (Seconds (0.002))); // Aggressive traffic
        client.Install (users.Get (i)).Start (Seconds (1.0));
    }

    UdpEchoServerHelper echoServer (9);
    echoServer.Install (hub.Get (0)).Start (Seconds (0.5));

    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll ();
    Simulator::Stop (Seconds (10.0));
    Simulator::Run ();
    monitor->SerializeToXmlFile ("results/dynamic_report.xml", true, true);
    Simulator::Destroy ();
    return 0;
}
