import 'package:flutter/material.dart';
import 'home_screen.dart';

void main() {
  runApp(const AegisApp());
}

class AegisApp extends StatelessWidget {
  const AegisApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Project Aegis',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        scaffoldBackgroundColor: Colors.white,
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
