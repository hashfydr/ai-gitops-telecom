#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"

using namespace ns3;

// Fault: Simulating a Latency Spike (Congestion)
void InjectLatencyFault (Ptr<PointToPointChannel> channel, Time newDelay)
{
    Config::Set ("/ChannelList/0/$ns3::PointToPointChannel/Delay", TimeValue (newDelay));
}

int main (int argc, char *argv[])
{
    NodeContainer nodes;
    nodes.Create (2);

    PointToPointHelper pointToPoint;
    pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("100Mbps"));
    pointToPoint.SetChannelAttribute ("Delay", StringValue ("5ms"));

    NetDeviceContainer devices = pointToPoint.Install (nodes);
    Ptr<PointToPointChannel> channel = StaticCast<PointToPointChannel> (devices.Get(0)->GetChannel());

    InternetStackHelper stack;
    stack.Install (nodes);

    Ipv4AddressHelper address;
    address.SetBase ("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaces = address.Assign (devices);

    UdpEchoServerHelper echoServer (9);
    ApplicationContainer serverApps = echoServer.Install (nodes.Get (1));
    serverApps.Start (Seconds (1.0));
    serverApps.Stop (Seconds (40.0));

    UdpEchoClientHelper echoClient (interfaces.GetAddress (1), 9);
    echoClient.SetAttribute ("MaxPackets", UintegerValue (4000));
    echoClient.SetAttribute ("Interval", TimeValue (Seconds (0.01)));
    echoClient.SetAttribute ("PacketSize", UintegerValue (1024));

    ApplicationContainer clientApps = echoClient.Install (nodes.Get (0));
    clientApps.Start (Seconds (2.0));
    clientApps.Stop (Seconds (40.0));

    // AT 20 SECONDS: The 5ms delay spikes to 200ms (Congestion Fault)
    Simulator::Schedule (Seconds (20.0), &InjectLatencyFault, channel, MilliSeconds (200));

    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll ();

    Simulator::Stop (Seconds (40.0));
    Simulator::Run ();
    monitor->SerializeToXmlFile ("results/deployment_report.xml", true, true);
    Simulator::Destroy ();
    return 0;
}
