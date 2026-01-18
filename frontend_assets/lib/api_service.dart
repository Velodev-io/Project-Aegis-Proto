import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // REPLACE WITH YOUR MAC'S IP IF TESTING ON PHYSICAL DEVICE
  // For iOS Simulator, 'http://127.0.0.1:8000' usually works.
  // For Android Emulator, use 'http://10.0.2.2:8000'.
  static const String baseUrl = 'http://127.0.0.1:8000';

  Future<Map<String, dynamic>> analyzeCall(String transcript) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/sentinel/analyze'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'text': transcript}),
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      print("Error analyzing call: $e");
    }
    return {'classification': 'Error', 'reasoning': 'Could not reach Sentinel.'};
  }

  Future<Map<String, dynamic>> checkBills() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/advocate/check_bills'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'service_name': 'utility_portal'}),
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      print("Error checking bills: $e");
    }
    return {'status': 'Error', 'reasoning': 'Could not reach Advocate.'};
  }

  Future<List<dynamic>> getPendingApprovals() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/steward/pending'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      print("Error fetching approvals: $e");
    }
    return [];
  }

  Future<void> reviewBill(int id, String decision) async {
    try {
      await http.post(
        Uri.parse('$baseUrl/steward/review'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'item_id': id, 'decision': decision}),
      );
    } catch (e) {
      print("Error reviewing bill: $e");
    }
  }
}
