// Free AI Chat Screen — Groq / Gemini / HuggingFace / Mistral / Cohere
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/chat_bubble.dart';

class FreeAiChatScreen extends StatefulWidget {
  const FreeAiChatScreen({super.key});
  @override
  State<FreeAiChatScreen> createState() => _FreeAiChatScreenState();
}

class _FreeAiChatScreenState extends State<FreeAiChatScreen> {
  final TextEditingController _ctrl = TextEditingController();
  final ScrollController _scroll = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _loading = false;
  String _provider = 'groq';
  int _totalTokens = 0;
  Map<String, dynamic> _providerStatus = {};

  static const Map<String, Map<String, String>> _providerInfo = {
    'groq':        {'icon': '⚡', 'label': 'Groq',        'model': 'Llama 3.1',    'limit': '14,400/day'},
    'gemini':      {'icon': '🌟', 'label': 'Gemini',      'model': '1.5 Flash',    'limit': '1,500/day'},
    'huggingface': {'icon': '🤗', 'label': 'HuggingFace', 'model': 'Mistral 7B',   'limit': 'Rate limited'},
    'mistral':     {'icon': '🌀', 'label': 'Mistral AI',  'model': 'mistral-small','limit': 'Free tier'},
    'cohere':      {'icon': '🔷', 'label': 'Cohere',      'model': 'command-r',    'limit': '1,000/month'},
  };

  static const _samples = [
    'Explain quantum computing in simple terms',
    'What is machine learning?',
    'How does the internet work?',
    'Write a Python function to sort a list',
  ];

  @override
  void initState() {
    super.initState();
    _loadProviderStatus();
  }

  Future<void> _loadProviderStatus() async {
    try {
      final data = await ApiService.getProviders();
      if (mounted) setState(() { _providerStatus = data; });
    } catch (_) {
      // provider status load failed, continue without it
    }
  }

  void _scrollBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scroll.hasClients) _scroll.animateTo(_scroll.position.maxScrollExtent, duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
    });
  }

  Future<void> _send(String text) async {
    if (text.trim().isEmpty || _loading) return;
    _ctrl.clear();
    setState(() {
      _messages.add(ChatMessage(role: 'user', content: text));
      _loading = true;
    });
    _scrollBottom();

    try {
      final res = await ApiService.freeChat(question: text, provider: _provider);
      setState(() {
        _totalTokens += res.totalTokens;
        _messages.add(ChatMessage(role: 'assistant', content: res.answer, freeMeta: res));
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          role: 'assistant',
          content: '⚠️ Error: $e\n\nMake sure:\n1. FastAPI backend is running\n2. API key is set in .env (e.g. GROQ_API_KEY)\n\nGet a free key at console.groq.com',
        ));
      });
    } finally {
      setState(() => _loading = false);
      _scrollBottom();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Column(
        children: [
          // ── Header ─────────────────────────────────────────
          _buildHeader(),
          // ── Provider cards ─────────────────────────────────
          _buildProviderCards(),
          const Divider(height: 1),
          // ── Provider selector + samples ────────────────────
          _buildControls(),
          const Divider(height: 1),
          // ── Messages ───────────────────────────────────────
          Expanded(
            child: _messages.isEmpty ? _buildEmptyState() : ListView.builder(
              controller: _scroll,
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              itemCount: _messages.length + (_loading ? 1 : 0),
              itemBuilder: (ctx, i) {
                if (i == _messages.length) return _FreeTypingIndicator(provider: _provider, info: _providerInfo[_provider]!);
                final msg = _messages[i];
                if (msg.role == 'user') return UserBubble(text: msg.content, gradient: AppTheme.freeBubbleGrad);
                return _FreeAssistantBubble(msg: msg);
              },
            ),
          ),
          // ── Stats bar ──────────────────────────────────────
          _buildStatsBar(),
          // ── Input ──────────────────────────────────────────
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppTheme.freeGreen.withValues(alpha: 0.12), AppTheme.freeBlue.withValues(alpha: 0.12)],
          begin: Alignment.topLeft, end: Alignment.bottomRight,
        ),
        border: const Border(bottom: BorderSide(color: AppTheme.border)),
      ),
      child: Row(
        children: [
          Container(
            width: 48, height: 48,
            decoration: BoxDecoration(gradient: AppTheme.freeGrad, borderRadius: BorderRadius.circular(14),
              boxShadow: [BoxShadow(color: AppTheme.freeGreen.withValues(alpha: 0.35), blurRadius: 20)]),
            child: const Center(child: Text('🤖', style: TextStyle(fontSize: 24))),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ShaderMask(
                  shaderCallback: (b) => const LinearGradient(colors: [Color(0xFF059669), Color(0xFF2563EB)]).createShader(b),
                  child: Text('Free AI Chat', style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: Colors.white)),
                ),
                Text('Powered by free cloud LLMs — answers here, no redirect, no APK',
                    style: GoogleFonts.inter(fontSize: 11, color: AppTheme.textMuted)),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
            decoration: BoxDecoration(
              color: AppTheme.freeGreen.withValues(alpha: 0.15),
              border: Border.all(color: AppTheme.freeGreen.withValues(alpha: 0.35)),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text('✅ Free Tier', style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.freeGreenL)),
          ),
        ],
      ),
    );
  }

  Widget _buildProviderCards() {
    final providers = _providerStatus['providers'] as Map<String, dynamic>? ?? {};
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('🔌 Available Providers — set API keys in .env',
              style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted, fontWeight: FontWeight.w500)),
          const SizedBox(height: 8),
          SizedBox(
            height: 72,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: _providerInfo.entries.map((e) {
                final key = e.key;
                final info = e.value;
                final status = providers[key] as Map<String, dynamic>? ?? {};
                final configured = status['configured'] as bool? ?? false;
                final isActive = key == _provider;
                return GestureDetector(
                  onTap: () => setState(() => _provider = key),
                  child: Container(
                    width: 150,
                    margin: const EdgeInsets.only(right: 8),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: isActive ? AppTheme.freeGreen.withValues(alpha: 0.08) : AppTheme.bgCard,
                      border: Border.all(color: isActive ? AppTheme.freeGreen.withValues(alpha: 0.5) : AppTheme.border),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Text(info['icon']!, style: const TextStyle(fontSize: 22)),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(info['label']!, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textPrimary)),
                              Text('${info['model']} · ${info['limit']}', style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted)),
                              const SizedBox(height: 3),
                              Row(
                                children: [
                                  Container(
                                    width: 7, height: 7,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: configured ? AppTheme.green : AppTheme.red,
                                      boxShadow: [BoxShadow(color: (configured ? AppTheme.green : AppTheme.red).withValues(alpha: 0.5), blurRadius: 4)],
                                    ),
                                  ),
                                  const SizedBox(width: 4),
                                  Text(configured ? '✓ Ready' : 'Key needed',
                                      style: GoogleFonts.inter(fontSize: 10, color: configured ? AppTheme.green : AppTheme.textMuted)),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildControls() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Quick questions:', style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted, fontWeight: FontWeight.w500)),
          const SizedBox(height: 6),
          Wrap(
            spacing: 8, runSpacing: 6,
            children: _samples.map((s) => ActionChip(
              label: Text(s.length > 38 ? '${s.substring(0, 38)}…' : s,
                  style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textSecond)),
              backgroundColor: AppTheme.bgCard,
              side: const BorderSide(color: AppTheme.border),
              onPressed: () => _send(s),
            )).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    final info = _providerInfo[_provider]!;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(info['icon']!, style: const TextStyle(fontSize: 56)),
          const SizedBox(height: 16),
          Text('Chat with ${info['label']}', style: GoogleFonts.inter(fontSize: 20, fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
          const SizedBox(height: 8),
          Text('${info['model']} · ${info['limit']}', style: GoogleFonts.inter(fontSize: 13, color: AppTheme.textMuted)),
          const SizedBox(height: 20),
          Text('Type a question below — answer appears here on AMOF',
              style: GoogleFonts.inter(fontSize: 13, color: AppTheme.textMuted)),
        ],
      ),
    );
  }

  Widget _buildStatsBar() {
    final info = _providerInfo[_provider]!;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: const BoxDecoration(
        color: AppTheme.bgCard2,
        border: Border(top: BorderSide(color: AppTheme.border)),
      ),
      child: Row(
        children: [
          _statItem('Questions', '${_messages.where((m) => m.role == 'user').length}'),
          const SizedBox(width: 20),
          _statItem('Tokens', '$_totalTokens'),
          const SizedBox(width: 20),
          _statItem('Provider', '${info['icon']} ${info['label']}'),
          const Spacer(),
          TextButton.icon(
            icon: const Icon(Icons.delete_outline, size: 14),
            label: const Text('Clear'),
            style: TextButton.styleFrom(foregroundColor: AppTheme.textMuted, textStyle: GoogleFonts.inter(fontSize: 12)),
            onPressed: () => setState(() { _messages.clear(); _totalTokens = 0; }),
          ),
        ],
      ),
    );
  }

  Widget _statItem(String label, String val) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(val, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.freeGreenL)),
      Text(label, style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted)),
    ],
  );

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 16),
      decoration: const BoxDecoration(border: Border(top: BorderSide(color: AppTheme.border))),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _ctrl, enabled: !_loading, onSubmitted: _send, maxLines: null,
              style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14),
              decoration: InputDecoration(
                hintText: 'Ask anything — answered by ${_providerInfo[_provider]!['label']} here on AMOF…',
              ),
            ),
          ),
          const SizedBox(width: 10),
          _loading
            ? const SizedBox(width: 44, height: 44, child: Padding(padding: EdgeInsets.all(10), child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.freeGreen)))
            : IconButton(
                onPressed: () => _send(_ctrl.text),
                icon: const Icon(Icons.send_rounded),
                style: IconButton.styleFrom(
                  backgroundColor: AppTheme.freeGreen,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
        ],
      ),
    );
  }
}

// ── Free chat assistant bubble ──────────────────────────────────────────────
class _FreeAssistantBubble extends StatelessWidget {
  final ChatMessage msg;
  const _FreeAssistantBubble({required this.msg});

  @override
  Widget build(BuildContext context) {
    final m = msg.freeMeta;
    return Padding(
      padding: const EdgeInsets.only(right: 48, bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34, height: 34,
            decoration: const BoxDecoration(gradient: AppTheme.freeGrad, shape: BoxShape.circle),
            child: Center(child: Text('AI', style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 11))),
          ),
          const SizedBox(width: 10),
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.bgCard,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(4), topRight: Radius.circular(18),
                  bottomLeft: Radius.circular(18), bottomRight: Radius.circular(18),
                ),
                border: Border.all(color: AppTheme.border),
                boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 8)],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SelectableText(msg.content, style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14, height: 1.7)),
                  if (m != null) ...[
                    const SizedBox(height: 8),
                    const Divider(color: AppTheme.border, height: 1),
                    const SizedBox(height: 8),
                    FreeMetaRow(provider: m.providerUsed, latencyMs: m.latencyMs, tokens: m.totalTokens),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Free typing indicator ───────────────────────────────────────────────────
class _FreeTypingIndicator extends StatefulWidget {
  final String provider;
  final Map<String, String> info;
  const _FreeTypingIndicator({required this.provider, required this.info});
  @override
  State<_FreeTypingIndicator> createState() => _FreeTypingIndicatorState();
}
class _FreeTypingIndicatorState extends State<_FreeTypingIndicator> with SingleTickerProviderStateMixin {
  late AnimationController _anim;
  @override void initState() { super.initState(); _anim = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..repeat(); }
  @override void dispose() { _anim.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 48, bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34, height: 34,
            decoration: const BoxDecoration(gradient: AppTheme.freeGrad, shape: BoxShape.circle),
            child: Center(child: Text(widget.info['icon']!, style: const TextStyle(fontSize: 16))),
          ),
          const SizedBox(width: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(color: AppTheme.bgCard, borderRadius: BorderRadius.circular(18), border: Border.all(color: AppTheme.border)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${widget.info['label']} is thinking…', style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted)),
                const SizedBox(height: 8),
                AnimatedBuilder(
                  animation: _anim,
                  builder: (_, __) => Row(
                    children: List.generate(3, (i) {
                      final t = (_anim.value - i * 0.2).clamp(0.0, 1.0);
                      return Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 3),
                        child: Transform.translate(
                          offset: Offset(0, -4 * (t < 0.5 ? t * 2 : (1 - t) * 2)),
                          child: Container(width: 7, height: 7, decoration: const BoxDecoration(color: AppTheme.freeGreenL, shape: BoxShape.circle)),
                        ),
                      );
                    }),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
