// screens/chat_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/sidebar.dart';
import '../widgets/message_bubble.dart';
import '../widgets/compare_view.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _inputCtrl   = TextEditingController();
  final _scrollCtrl  = ScrollController();
  final _focusNode   = FocusNode();
  bool _sidebarOpen  = true;

  final _sampleQueries = [
    'What is the current inventory stock quantity of Quantum X Laptop in Warehouse A?',
    'What does the company return policy say about unopened merchandise and refund timeframe?',
    'Which product generated the highest total sales revenue from customer orders?',
    'What warranty coverage is provided for Aura Pro Wireless Headphones?',
    'How many units of Ergonomic Lumbar Office Chair are currently in stock?',
  ];

  @override
  void dispose() {
    _inputCtrl.dispose();
    _scrollCtrl.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _sendQuery() {
    final query = _inputCtrl.text.trim();
    if (query.isEmpty) return;
    _inputCtrl.clear();
    context.read<ChatProvider>().sendQuery(query);
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ChatProvider>();

    // Auto-scroll when new content appears
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());

    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Row(
        children: [
          // ── Sidebar ─────────────────────────────────────────────
          AnimatedContainer(
            duration: const Duration(milliseconds: 250),
            width: _sidebarOpen ? 260 : 0,
            child: _sidebarOpen ? const AppSidebar() : const SizedBox.shrink(),
          ),

          // ── Main panel ──────────────────────────────────────────
          Expanded(
            child: Column(
              children: [
                _buildTopBar(provider),
                _buildQuickPills(provider),
                Expanded(child: _buildChatArea(provider)),
                _buildInputBar(provider),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Top bar ───────────────────────────────────────────────────────────────
  Widget _buildTopBar(ChatProvider p) => Container(
        height: 56,
        decoration: const BoxDecoration(
          color: AppTheme.bg2,
          border: Border(bottom: BorderSide(color: AppTheme.border)),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(children: [
          IconButton(
            icon: Icon(_sidebarOpen ? Icons.menu_open : Icons.menu,
                color: AppTheme.textMuted),
            onPressed: () => setState(() => _sidebarOpen = !_sidebarOpen),
            tooltip: 'Toggle sidebar',
          ),
          const SizedBox(width: 4),
          // Title with gradient
          ShaderMask(
            shaderCallback: (b) => AppTheme.gradient.createShader(b),
            child: Text(
              'AMOF  ×  ${p.selectedModel.isEmpty ? 'Chat' : p.selectedModel}',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white),
            ),
          ),
          const SizedBox(width: 10),
          // Mode indicator chip
          _modeChip(p.appMode),
          const Spacer(),
          // Status indicators
          _StatusIndicator(label: 'Backend', online: p.backendOnline),
          const SizedBox(width: 8),
          _StatusIndicator(label: 'Ollama', online: p.ollamaOnline),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.refresh, size: 18, color: AppTheme.textMuted),
            onPressed: p.refreshConnections,
            tooltip: 'Refresh connections',
          ),
        ]),
      );

  Widget _modeChip(AppMode mode) {
    final (label, color) = switch (mode) {
      AppMode.withAmora => ('🤖 LLM with AMOF', AppTheme.accent2),
      AppMode.directLlm => ('⚡ LLM without AMOF', AppTheme.orange),
      AppMode.compare   => ('⚖️ Compare Mode', AppTheme.green),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        border: Border.all(color: color.withOpacity(0.35)),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(label, style: TextStyle(fontSize: 12, color: color, fontWeight: FontWeight.w600)),
    );
  }

  // ── Quick pills ───────────────────────────────────────────────────────────
  Widget _buildQuickPills(ChatProvider p) => Container(
        decoration: const BoxDecoration(
          color: AppTheme.bg2,
          border: Border(bottom: BorderSide(color: AppTheme.border)),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              const Text('Example Questions: ', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.purple)),
              const SizedBox(width: 8),
              ..._sampleQueries.map((q) => Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ActionChip(
                      label: Text(q.length > 44 ? '${q.substring(0, 42)}…' : q,
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                      backgroundColor: AppTheme.bg3,
                      side: const BorderSide(color: AppTheme.border),
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                      onPressed: p.isGenerating ? null : () {
                        _inputCtrl.text = q;
                        _sendQuery();
                      },
                    ),
                  )),
            ],
          ),
        ),
      );

  // ── Chat area ─────────────────────────────────────────────────────────────
  Widget _buildChatArea(ChatProvider p) {
    final isCompare = p.appMode == AppMode.compare;
    final isEmpty   = isCompare ? p.compareMessages.isEmpty : p.messages.isEmpty;

    if (isEmpty) return _buildSplash(p);

    return ListView.builder(
      controller: _scrollCtrl,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      itemCount: isCompare ? p.compareMessages.length : p.messages.length,
      itemBuilder: (ctx, i) {
        if (isCompare) {
          return CompareView(cmp: p.compareMessages[i]);
        } else {
          return MessageBubble(message: p.messages[i]);
        }
      },
    );
  }

  Widget _buildSplash(ChatProvider p) => Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          // Animated logo
          Container(
            width: 72, height: 72,
            decoration: BoxDecoration(
              gradient: AppTheme.gradient,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [BoxShadow(color: AppTheme.accent.withOpacity(0.4), blurRadius: 24, spreadRadius: 2)],
            ),
            child: const Center(child: Text('A', style: TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold))),
          ),
          const SizedBox(height: 24),
          ShaderMask(
            shaderCallback: (b) => AppTheme.gradient.createShader(b),
            child: const Text('AMOF × LLM Chat',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700, color: Colors.white)),
          ),
          const SizedBox(height: 10),
          Text(
            p.appMode == AppMode.compare
                ? 'Compare Mode: See LLM with AMOF vs LLM without AMOF side by side'
                : p.appMode == AppMode.withAmora
                    ? 'Queries are enhanced by AMOF multi-objective source routing and external evidence grounding'
                    : 'Direct LLM Mode: Pure model parametric knowledge — no AMOF routing',
            style: const TextStyle(color: AppTheme.textMuted, fontSize: 14),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6),
          Text(
            p.selectedModel.isEmpty ? 'Select a model from the sidebar to start' : 'Model: ${p.selectedModel}',
            style: const TextStyle(color: AppTheme.textDim, fontSize: 12),
          ),
        ]),
      );

  // ── Input bar ─────────────────────────────────────────────────────────────
  Widget _buildInputBar(ChatProvider p) => Container(
        decoration: const BoxDecoration(
          color: AppTheme.bg2,
          border: Border(top: BorderSide(color: AppTheme.border)),
        ),
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: AppTheme.bg3,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.border),
                ),
                child: Focus(
                  onFocusChange: (f) => setState(() {}),
                  child: TextField(
                    controller: _inputCtrl,
                    focusNode: _focusNode,
                    minLines: 1, maxLines: 5,
                    enabled: !p.isGenerating,
                    style: const TextStyle(color: AppTheme.textPrimary, fontSize: 14),
                    decoration: const InputDecoration(
                      hintText: 'Ask anything… AMORA routes it intelligently',
                      hintStyle: TextStyle(color: AppTheme.textDim, fontSize: 14),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    onSubmitted: (_) => p.isGenerating ? null : _sendQuery(),
                    textInputAction: TextInputAction.send,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            // Send button
            GestureDetector(
              onTap: p.isGenerating ? null : _sendQuery,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 48, height: 48,
                decoration: BoxDecoration(
                  gradient: p.isGenerating
                      ? const LinearGradient(colors: [AppTheme.bg3, AppTheme.bg3])
                      : AppTheme.gradient,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: p.isGenerating
                      ? []
                      : [BoxShadow(color: AppTheme.accent.withOpacity(0.4), blurRadius: 14)],
                ),
                child: p.isGenerating
                    ? const Center(child: SizedBox(width: 20, height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.textMuted)))
                    : const Icon(Icons.send_rounded, color: Colors.white, size: 20),
              ),
            ),
          ]),
          const SizedBox(height: 6),
          Text(
            'Enter to send  ·  Shift+Enter for new line  ·  ${p.appMode == AppMode.compare ? "Runs AMORA + Direct simultaneously" : p.appMode == AppMode.withAmora ? "AMORA routes to best sources" : "Goes directly to ${p.selectedModel}"}',
            style: const TextStyle(fontSize: 11, color: AppTheme.textDim),
          ),
        ]),
      );
}

// ── Status indicator ──────────────────────────────────────────────────────────
class _StatusIndicator extends StatelessWidget {
  final String label;
  final bool online;
  const _StatusIndicator({required this.label, required this.online});

  @override
  Widget build(BuildContext context) => Row(children: [
        Container(
          width: 7, height: 7,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: online ? AppTheme.green : AppTheme.red,
            boxShadow: [BoxShadow(color: (online ? AppTheme.green : AppTheme.red).withOpacity(0.5), blurRadius: 5)],
          ),
        ),
        const SizedBox(width: 5),
        Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
      ]);
}
