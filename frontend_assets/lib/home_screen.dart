import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:permission_handler/permission_handler.dart';
import 'api_service.dart';
import 'scam_alert.dart';
import 'steward_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  final ApiService _api = ApiService();
  late stt.SpeechToText _speech;
  bool _isListening = false;
  String _voiceText = "";
  
  bool _isScanning = false;
  late AnimationController _controller;
  
  // Status message
  String _statusMessage = "Tap the Shield & Say\n'Check my bills' or 'Analyze call'";

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
    _initSpeech();
  }

  void _initSpeech() async {
    await Permission.microphone.request();
    bool available = await _speech.initialize(
      onStatus: (val) => print('onStatus: $val'),
      onError: (val) => print('onError: $val'),
    );
    if (!available) {
      setState(() => _statusMessage = "Voice not available");
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _listen() async {
    if (!_isListening) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() {
          _isListening = true;
          _voiceText = "";
          _statusMessage = "Listening...";
          _controller.repeat(reverse: true); // Start pulsing
        });
        
        _speech.listen(
          onResult: (val) {
            setState(() {
              _voiceText = val.recognizedWords;
              if (val.hasConfidenceRating && val.confidence > 0) {
                 // Update live transcription
              }
            });
            
            if (val.finalResult) {
              _processCommand(_voiceText);
            }
          },
        );
      }
    } else {
      setState(() {
        _isListening = false;
        _speech.stop();
        _controller.stop();
        _controller.reset();
      });
    }
  }

  void _processCommand(String command) async {
    setState(() {
      _isListening = false;
      _speech.stop();
      _isScanning = true;
      _statusMessage = "Processing: \"$command\"...";
    });

    String lowerCmd = command.toLowerCase();

    // Trigger Logic based on voice command
    if (lowerCmd.contains("bill") || lowerCmd.contains("check")) {
      
      final result = await _api.checkBills();
      
      setState(() {
        _isScanning = false;
        _controller.stop();
        _controller.reset();
        
        if (result['action_required'] == true) {
           _statusMessage = "Alert: High Bill Found.\nSteward Notified.";
           _showSnackBar(result['reasoning']);
        } else {
           _statusMessage = "Bills Checked.\nAll Safe, Grandpa!";
        }
      });

    } else if (lowerCmd.contains("call") || lowerCmd.contains("analyze") || lowerCmd.contains("scam")) {
      
      // For demo, we might not have a real live call stream, 
      // so we will simulate analysis of a "current" call.
      // In a real app, this would stream audio bytes.
      String demoTranscript = "Hello I am from IRS give me gift card now or jail.";
      if (lowerCmd.contains("save") || lowerCmd.contains("safe")) {
         demoTranscript = "Hi Grandpa, just calling to say hi.";
      }

      final result = await _api.analyzeCall(demoTranscript);
      
      setState(() {
        _isScanning = false;
        _controller.stop();
        _controller.reset();
        _statusMessage = "Analysis Complete.";
      });

      if (result['classification'] == 'Confirmed Scam') {
        _showScamAlert(result['reasoning']);
      } else {
         _statusMessage = "Call is Safe.";
         _showSnackBar("Call looks safe.");
      }
      
      if (result['classification'] == 'Confirmed Scam') {
        _showScamAlert(result['reasoning']);
      } else {
         _statusMessage = "Call is Safe.";
         _showSnackBar("Call looks safe.");
      }
      
    } else if (lowerCmd.contains("scan") || lowerCmd.contains("document")) {
      // Mock Document Scan for Demo
      // In real Flutter, allow Camera/File Picker
      await Future.delayed(const Duration(seconds: 2)); // Simulate upload
      
      setState(() {
        _isScanning = false;
        _controller.stop();
        _controller.reset();
        _statusMessage = "Document Analysis Complete.";
      });
      
      // Basic Mock Logic for now (since we can't easily upload from Simulator via this voice command)
       _showSnackBar("Scanned Safe Utility Bill.");
       
    } else {
      setState(() {
        _isScanning = false;
        _controller.stop();
        _controller.reset();
        _statusMessage = "Did not understand.\nTry 'Check Bills'";
      });
    }
  }

  void _showScamAlert(String reasoning) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => ScamAlertOverlay(
        reasoning: reasoning,
        onDismiss: () => Navigator.pop(context),
      ),
    );
  }

  void _showSnackBar(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueGrey.shade50,
      appBar: AppBar(
        title: const Text("Project Aegis"),
        actions: [
          IconButton(
            icon: const Icon(Icons.admin_panel_settings),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const StewardDashboard()),
            ),
          )
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Spacer(),
            
            // PULSING SHIELD (Tap to Listen)
            GestureDetector(
              onTap: _listen,
              child: AnimatedBuilder(
                animation: _controller,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _isListening || _isScanning ? 1.0 + (_controller.value * 0.15) : 1.0,
                    child: Container(
                      width: 200,
                      height: 200,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.white,
                        boxShadow: [
                           BoxShadow(
                             color: (_isListening || _isScanning) ? Colors.blueAccent.withOpacity(0.6) : Colors.grey.withOpacity(0.2),
                             blurRadius: (_isListening || _isScanning) ? 50 * _controller.value + 10 : 10,
                             spreadRadius: (_isListening || _isScanning) ? 10 * _controller.value : 2,
                           )
                        ],
                      ),
                      child: Icon(
                        _isListening ? Icons.mic : Icons.shield,
                        size: 100,
                        color: _isListening ? Colors.redAccent : Colors.blueAccent,
                      ),
                    ),
                  );
                },
              ),
            ),
            
            const SizedBox(height: 40),
            
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 30.0),
              child: Text(
                _voiceText.isEmpty ? _statusMessage : _voiceText,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: Colors.black87),
                textAlign: TextAlign.center,
              ),
            ),
            
            const Spacer(),
            
            // Debug / Fallback Buttons
            const Text("Manual Controls:", style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: () => _processCommand("check bills"),
                  child: const Text("Check Bills"),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: _isScanning ? null : () => _triggerScan("analyze this call"),
                  icon: const Icon(Icons.phone_in_talk),
                  label: const Text("Analyze Call"),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.orange.shade100, foregroundColor: Colors.brown),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: _isScanning ? null : () => _triggerScan("scan document"),
                  icon: const Icon(Icons.document_scanner),
                  label: const Text("Scan Document"),
                   style: ElevatedButton.styleFrom(backgroundColor: Colors.green.shade100, foregroundColor: Colors.green.shade900),
                ),
              ],
            ),
            const SizedBox(height: 50),
          ],
        ),
      ),
    );
  }
}
