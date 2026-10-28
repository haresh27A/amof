// AMOF Flutter App — Main Entry Point
// Replaces Streamlit frontend with native Flutter UI
// Targets: Web (browser) + Android APK
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'theme/app_theme.dart';
import 'screens/chat_screen.dart';
import 'screens/compare_screen.dart';
import 'screens/sources_screen.dart';
import 'screens/benchmark_screen.dart';
import 'services/api_service.dart';

void main() {
  runApp(const AmofApp());
}

class AmofApp extends StatelessWidget {
  const AmofApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AMOF — Adaptive Multi-Objective RAG',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const MainShell(),
    );
  }
}

// ── Main shell with bottom navigation ──────────────────────────────────────
class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _index = 0;
  bool _backendOnline = false;
  bool _checking = true;

  @override
  void initState() {
    super.initState();
    _checkBackend();
  }

  Future<void> _checkBackend() async {
    try {
      await ApiService.getHealth();
      if (mounted) setState(() { _backendOnline = true; _checking = false; });
    } catch (_) {
      if (mounted) setState(() { _backendOnline = false; _checking = false; });
    }
  }

  static const _screens = [
    ChatScreen(),
    CompareScreen(),
    SourcesScreen(),
    BenchmarkScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      appBar: _buildAppBar(),
      body: IndexedStack(index: _index, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        backgroundColor: AppTheme.bgCard,
        indicatorColor: AppTheme.accent.withValues(alpha: 0.12),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.chat_bubble_outline),
            selectedIcon: Icon(Icons.chat_bubble, color: AppTheme.accentLight),
            label: 'Chat',
          ),
          NavigationDestination(
            icon: Icon(Icons.compare_arrows_outlined),
            selectedIcon: Icon(Icons.compare_arrows, color: AppTheme.accentLight),
            label: 'Compare',
          ),
          NavigationDestination(
            icon: Icon(Icons.folder_outlined),
            selectedIcon: Icon(Icons.folder, color: AppTheme.accentLight),
            label: 'Sources',
          ),
          NavigationDestination(
            icon: Icon(Icons.bar_chart_outlined),
            selectedIcon: Icon(Icons.bar_chart, color: AppTheme.accentLight),
            label: 'Benchmark',
          ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      titleSpacing: 16,
      title: Row(
        children: [
          // AMOF logo
          Container(
            width: 32, height: 32,
            decoration: BoxDecoration(gradient: AppTheme.accentGrad, borderRadius: BorderRadius.circular(8)),
            child: const Center(child: Text('A', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 18))),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ShaderMask(
                shaderCallback: (b) => const LinearGradient(colors: [Color(0xFF4F46E5), Color(0xFF9333EA)]).createShader(b),
                child: Text('AMOF', style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w800, color: Colors.white)),
              ),
              Text('RAG Intelligence', style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted)),
            ],
          ),
        ],
      ),
      actions: [
        // Backend status indicator
        Padding(
          padding: const EdgeInsets.only(right: 12),
          child: _checking
            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.accent))
            : GestureDetector(
                onTap: () {
                  setState(() => _checking = true);
                  _checkBackend();
                },
                child: Row(
                  children: [
                    Container(
                      width: 8, height: 8,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _backendOnline ? AppTheme.green : AppTheme.red,
                        boxShadow: [BoxShadow(color: (_backendOnline ? AppTheme.green : AppTheme.red).withValues(alpha: 0.6), blurRadius: 6)],
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      _backendOnline ? 'Backend Online' : 'Backend Offline',
                      style: GoogleFonts.inter(fontSize: 12, color: _backendOnline ? AppTheme.green : AppTheme.red),
                    ),
                  ],
                ),
              ),
        ),
        // Settings button
        IconButton(
          icon: const Icon(Icons.settings_outlined, size: 20),
          onPressed: () => _showSettings(context),
          tooltip: 'Settings',
        ),
      ],
    );
  }

  void _showSettings(BuildContext context) {
    final ctrl = TextEditingController(text: ApiService.baseUrl);
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppTheme.bgCard,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('⚙️ Settings', style: GoogleFonts.inter(color: AppTheme.textPrimary, fontWeight: FontWeight.w700)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Backend URL', style: GoogleFonts.inter(fontSize: 13, color: AppTheme.textMuted)),
            const SizedBox(height: 8),
            TextField(
              controller: ctrl,
              style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14),
              decoration: const InputDecoration(hintText: 'http://localhost:8000'),
            ),
            const SizedBox(height: 12),
            Text(
              '💡 For Android APK: use your PC\'s IP\n   e.g. http://192.168.x.x:8000\n\nFor Flutter Web: http://localhost:8000',
              style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted),
            ),
          ],
        ),
        actions: [
          TextButton(
            child: Text('Cancel', style: GoogleFonts.inter(color: AppTheme.textMuted)),
            onPressed: () => Navigator.pop(context),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppTheme.accent),
            child: Text('Save & Reconnect', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
            onPressed: () {
              ApiService.baseUrl = ctrl.text.trim();
              Navigator.pop(context);
              setState(() => _checking = true);
              _checkBackend();
            },
          ),
        ],
      ),
    );
  }
}
