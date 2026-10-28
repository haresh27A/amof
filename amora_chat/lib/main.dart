// main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'theme/app_theme.dart';
import 'providers/chat_provider.dart';
import 'screens/chat_screen.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => ChatProvider(),
      child: const AmoraChatApp(),
    ),
  );
}

class AmoraChatApp extends StatelessWidget {
  const AmoraChatApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'AMORA × LLM Chat',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light,
        home: const ChatScreen(),
      );
}
