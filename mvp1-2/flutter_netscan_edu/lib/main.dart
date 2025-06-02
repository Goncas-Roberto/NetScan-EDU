import 'dart:async';
import 'dart:isolate';
import 'package:flutter/material.dart';
import 'package:dart_ping/dart_ping.dart';

void main() {
  runApp(const NetScanEduApp());
}

class NetScanEduApp extends StatelessWidget {
  const NetScanEduApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NetScan Edu',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const ScanScreen(),
    );
  }
}

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  List<NetworkDevice> devices = [];
  bool isScanning = false;
  String logs = "";
  int scannedBlocks = 0;

  Future<void> scanEntireNetwork() async {
    setState(() {
      isScanning = true;
      devices.clear();
      logs = "Iniciando escaneamento de 192.168.0.0/16...\n";
    });

    for (int subnet = 0; subnet < 256; subnet++) {
      await _scanBlock(subnet); // 192.168.subnet.y
      _addLog("Bloco 192.168.$subnet.0/24 finalizado.");
    }

    setState(() {
      isScanning = false;
      logs += "\nEscaneamento completo!";
    });
  }

  Future<void> _scanBlock(int subnet) async {
    final receivePort = ReceivePort();
    final completer = Completer();
    int responded = 0;

    receivePort.listen((message) {
      if (message is Map<String, dynamic>) {
        if (message['status'] == 'online') {
          _addDevice(message['ip'], message['hostname']);
          _addLog("Dispositivo: ${message['ip']}");
        }
      }
      responded++;
      if (responded >= 254) {
        receivePort.close();
        completer.complete();
      }
    });

    for (int i = 1; i <= 254; i++) {
      final ip = '192.168.$subnet.$i';
      Isolate.spawn(pingIsolate, {'ip': ip, 'sendPort': receivePort.sendPort});
    }

    await completer.future;
  }

  static Future<void> pingIsolate(Map<String, dynamic> data) async {
    final String ip = data['ip'];
    final SendPort sendPort = data['sendPort'];

    try {
      final ping = Ping(ip, count: 1, timeout: 1);
      await for (final PingData event in ping.stream) {
        if (event.response != null) {
          sendPort.send({'ip': ip, 'hostname': 'Desconhecido', 'status': 'online'});
          return;
        }
      }
    } catch (_) {}
    sendPort.send({'ip': ip, 'status': 'offline'});
  }

  void _addDevice(String ip, String hostname) {
    setState(() {
      devices.add(NetworkDevice(ip: ip, hostname: hostname, status: 'Online'));
    });
  }

  void _addLog(String message) {
    setState(() {
      logs += "$message\n";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('NetScan Edu')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: isScanning ? null : scanEntireNetwork,
              child: Text(isScanning ? 'Escaneando...' : 'Iniciar Scanner Total'),
            ),
          ),
          Expanded(
            flex: 2,
            child: ListView.builder(
              itemCount: devices.length,
              itemBuilder: (context, index) {
                final device = devices[index];
                return ListTile(
                  title: Text(device.ip),
                  subtitle: Text(device.hostname),
                  trailing: Chip(
                    label: Text(device.status),
                    backgroundColor: Colors.green[100],
                  ),
                );
              },
            ),
          ),
          const Divider(),
          const Padding(
            padding: EdgeInsets.all(8.0),
            child: Text('Logs:'),
          ),
          Expanded(
            flex: 1,
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(8.0),
              child: Text(logs),
            ),
          ),
        ],
      ),
    );
  }
}

class NetworkDevice {
  final String ip;
  final String hostname;
  final String status;

  NetworkDevice({
    required this.ip,
    required this.hostname,
    required this.status,
  });
}
