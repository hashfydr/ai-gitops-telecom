#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"

using namespace ns3;

int main (int argc, char *argv[])
{
    NodeContainer hub; hub.Create (1);
    NodeContainer users; users.Create (16); // Increased to 16 users

    PointToPointHelper p2p;
    p2p.SetDeviceAttribute ("DataRate", StringValue ("100Mbps"));
    p2p.SetChannelAttribute ("Delay", StringValue ("2ms"));

    InternetStackHelper stack;
    stack.Install (hub); stack.Install (users);

    Ipv4AddressHelper address;
    Ipv4InterfaceContainer interfaces;

    for (uint32_t i = 0; i < users.GetN (); ++i) {
        NetDeviceContainer link = p2p.Install (users.Get (i), hub.Get (0));
        std::ostringstream subnet;
        subnet << "10.1." << i + 1 << ".0";
        address.SetBase (subnet.str ().c_str (), "255.255.255.0");
        interfaces.Add (address.Assign (link));

        // Start Traffic
        UdpEchoClientHelper client (interfaces.GetAddress (2 * i + 1), 9);
        client.SetAttribute ("MaxPackets", UintegerValue (1000));
        client.SetAttribute ("Interval", TimeValue (Seconds (0.01)));
        ApplicationContainer clientApp = client.Install (users.Get (i));
        clientApp.Start (Seconds (1.0));

        // Inject faults on specific nodes: 4, 8, 12 (to create class variety)
        if (i % 4 == 0 && i > 0) {
            Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
            em->SetAttribute ("ErrorRate", DoubleValue (0.15)); // 15% loss
            link.Get(0)->SetAttribute ("ReceiveErrorModel", PointerValue (em));
        }
    }

    UdpEchoServerHelper echoServer (9);
    echoServer.Install (hub.Get (0)).Start (Seconds (0.5));

    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll ();
    Simulator::Stop (Seconds (15.0));
    Simulator::Run ();
    monitor->SerializeToXmlFile ("results/multi_user_report.xml", true, true);
    Simulator::Destroy ();
    return 0;
}
