import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'api_service.dart';
import 'scam_alert.dart';
import 'steward_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  final ApiService _api = ApiService();
  late stt.SpeechToText _speech;
  late FlutterTts _flutterTts;

  bool _isListening = false;
  String _lastWords = "";

  bool _isProcessing = false;
  late AnimationController _controller;

  String _statusMessage = "Tap 'Active Protection' to start Sentinel";

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
    _flutterTts = FlutterTts();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    );
    _initPermissions();
  }

  void _initPermissions() async {
    await Permission.microphone.request();
    await Permission.speech.request();
  }

  @override
  void dispose() {
    _controller.dispose();
    _speech.stop();
    _flutterTts.stop();
    super.dispose();
  }

  void _toggleProtection() async {
    if (_isListening) {
      _stopListening();
    } else {
      _startListening();
    }
  }

  void _startListening() async {
    bool available = await _speech.initialize(
      onStatus: (status) => print('onStatus: $status'),
      onError: (errorNotification) => print('onError: $errorNotification'),
    );

    if (available) {
      setState(() {
        _isListening = true;
        _statusMessage = "Listening for threats...";
        _controller.repeat(reverse: true);
      });

      _speech.listen(
        onResult: (val) {
          setState(() {
            _lastWords = val.recognizedWords;
          });

          if (val.finalResult && _lastWords.isNotEmpty) {
            _analyzeText(_lastWords);
          }
        },
        listenFor: const Duration(seconds: 30),
        pauseFor: const Duration(seconds: 5),
        listenOptions: stt.SpeechListenOptions(partialResults: true),
      );
    } else {
      setState(() => _statusMessage = "Speech recognition unavailable");
    }
  }

  void _stopListening() {
    _speech.stop();
    _controller.stop();
    _controller.reset();
    setState(() {
      _isListening = false;
      _statusMessage = "Protection Deactivated";
    });
  }

  void _analyzeText(String text) async {
    if (_isProcessing) return;
    setState(() => _isProcessing = true);

    // Send to Backend
    final result = await _api.analyzeVoice(text);

    // Speak Response
    String message = result['message'] ?? "Analyzed.";
    await _flutterTts.speak(message);

    // Handle Threat
    if (result['status'] == 'DANGER') {
      _stopListening(); // Stop ensuring we don't loop
      _showScamAlert(message);
    } else {
      setState(() {
        _statusMessage = "Safe: $message";
      });
    }

    setState(() => _isProcessing = false);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueGrey.shade50,
      appBar: AppBar(
        title: const Text("Project Aegis: Sentinel"),
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

            // PULSING BUTTON
            GestureDetector(
              onTap: _toggleProtection,
              child: AnimatedBuilder(
                animation: _controller,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _isListening ? 1.0 + (_controller.value * 0.1) : 1.0,
                    child: Container(
                      width: 250,
                      height: 250,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isListening
                            ? Colors.blueAccent
                            : Colors.grey.shade300,
                        boxShadow: [
                          BoxShadow(
                            color: _isListening
                                ? Colors.blue.withValues(alpha: 0.5)
                                : Colors.transparent,
                            blurRadius:
                                _isListening ? 50 * _controller.value + 20 : 0,
                            spreadRadius:
                                _isListening ? 10 * _controller.value : 0,
                          )
                        ],
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            _isListening
                                ? Icons.security
                                : Icons.security_outlined,
                            size: 100,
                            color: Colors.white,
                          ),
                          const SizedBox(height: 10),
                          Text(
                            _isListening ? "ACTIVE" : "INACTIVE",
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 24,
                            ),
                          )
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 50),

            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Text(
                _statusMessage,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w500,
                  color: _isListening ? Colors.blue.shade900 : Colors.grey,
                ),
              ),
            ),

            const SizedBox(height: 20),
            if (_isListening)
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  "Detected: \"$_lastWords\"",
                  style: const TextStyle(fontStyle: FontStyle.italic),
                  textAlign: TextAlign.center,
                ),
              ),

            const Spacer(),

            // Manual Test Buttons
            Wrap(
              spacing: 10,
              children: [
                ElevatedButton(
                  onPressed: () => _analyzeText(
                      "I need you to pay the IRS with a gift card now"),
                  child: const Text("Sim. SCAM"),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green.shade100),
                  onPressed: () =>
                      _analyzeText("Hi grandma, how are you doing today?"),
                  child: const Text("Sim. SAFE"),
                ),
              ],
            ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }
}
