import 'package:flutter/material.dart';

class ScamAlertOverlay extends StatelessWidget {
  final String reasoning;
  final VoidCallback onDismiss;

  const ScamAlertOverlay({
    Key? key,
    required this.reasoning,
    required this.onDismiss,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.red.shade900,
      width: double.infinity,
      height: double.infinity,
      padding: const EdgeInsets.all(40),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.warning_amber_rounded, size: 120, color: Colors.white),
          const SizedBox(height: 30),
          const Text(
            "SCAM DETECTED!",
            style: TextStyle(
              color: Colors.white,
              fontSize: 32,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          Text(
            reasoning,
            style: const TextStyle(color: Colors.white, fontSize: 18),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 50),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: Colors.red.shade900,
              padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 20),
            ),
            onPressed: onDismiss,
            child: const Text("I Understand, Hang Up", style: TextStyle(fontSize: 20)),
          ),
        ],
      ),
    );
  }
}
