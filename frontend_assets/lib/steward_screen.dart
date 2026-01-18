import 'package:flutter/material.dart';
import 'api_service.dart';

class StewardDashboard extends StatefulWidget {
  const StewardDashboard({Key? key}) : super(key: key);

  @override
  State<StewardDashboard> createState() => _StewardDashboardState();
}

class _StewardDashboardState extends State<StewardDashboard> {
  final ApiService _api = ApiService();
  List<dynamic> _approvals = [];

  @override
  void initState() {
    super.initState();
    _loadApprovals();
  }

  Future<void> _loadApprovals() async {
    final items = await _api.getPendingApprovals();
    setState(() {
      _approvals = items;
    });
  }

  Future<void> _handleDecision(int id, String decision) async {
    await _api.reviewBill(id, decision);
    _loadApprovals(); // Refresh
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Steward Dashboard - HITL Oversight")),
      body: _approvals.isEmpty
          ? const Center(child: Text("No pending approvals."))
          : ListView.builder(
              itemCount: _approvals.length,
              itemBuilder: (context, index) {
                final item = _approvals[index];
                return Card(
                  margin: const EdgeInsets.all(10),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text("Service: ${item['service_name']}",
                            style: Theme.of(context).textTheme.titleLarge),
                        Text("Amount: \$${item['amount']}",
                            style: const TextStyle(
                                fontSize: 20, fontWeight: FontWeight.bold, color: Colors.red)),
                        const SizedBox(height: 10),
                        Text("AI Reasoning: ${item['reasoning']}"),
                        const SizedBox(height: 20),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            ElevatedButton.icon(
                              icon: const Icon(Icons.close),
                              label: const Text("Reject"),
                              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                              onPressed: () => _handleDecision(item['id'], "REJECT"),
                            ),
                            const SizedBox(width: 10),
                            ElevatedButton.icon(
                              icon: const Icon(Icons.check),
                              label: const Text("Approve"),
                              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                              onPressed: () => _handleDecision(item['id'], "APPROVE"),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
