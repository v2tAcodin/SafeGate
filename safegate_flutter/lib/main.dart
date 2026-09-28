import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'ui/navigation/main_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SafeGateApp());
}

class SafeGateApp extends StatelessWidget {
  const SafeGateApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SafeGate - AI PPE Inspection',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const MainScreen(),
    );
  }
}
