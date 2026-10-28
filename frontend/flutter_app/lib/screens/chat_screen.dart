// AMOF Unified Chat Screen — Choose Any LLM + AMORA RAG ON/OFF
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/chat_bubble.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _ctrl = TextEditingController();
  final ScrollController _scroll = ScrollController();
  final List<ChatMessage> _messages = [];

  bool _loading = false;
  String _provider = 'llama3';
  bool _withAmora = true;
  String _mode = 'weighted';
  int _topK = 5;
  bool _costSensitive = false;
  bool _conflictSensitive = false;
  bool _forceRetrieval = false;
  int _totalTokens = 0;

  static const _providers = [
    ('llama3', 'Llama 3 (Local GPU)', 'RTX 4060 Accelerated · ~1.8s', Icons.flash_on),
    ('qwen', 'Qwen (Local Ollama)', 'Ollama Reasoning Engine', Icons.terminal),
    ('groq', 'Groq (Llama 3.1)', '14.4k req/day free API', Icons.bolt),
    ('gemini', 'Google Gemini', '1.5k req/day free API', Icons.auto_awesome),
    ('mistral', 'Mistral 7B', 'Free tier API', Icons.waves),
    ('huggingface', 'HuggingFace', 'Free open models', Icons.hub),
    ('cohere', 'Cohere Command-R', '1k req/month free', Icons.forest),
  ];

  static const _samples = [
    'What is the current inventory of Quantum X Laptop?',
    'What does the return policy say about unopened merchandise?',
    'Which product has the highest sales revenue?',
    'Compare the product spec with the company manual.',
  ];

  void _scrollBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _send(String text) async {
    if (text.trim().isEmpty || _loading) return;
    _ctrl.clear();
    setState(() {
      _messages.add(ChatMessage(
        role: 'user',
        content: text,
        provider: _provider,
        withAmora: _withAmora,
      ));
      _loading = true;
    });
    _scrollBottom();

    try {
      if (_withAmora) {
        // Run full AMORA RAG pipeline over SSE so answer tokens render as they
        // arrive. A local reasoning model can take minutes; a placeholder message
        // is inserted first so the user sees progress instead of a bare spinner.
        final placeholderIndex = _messages.length;
        setState(() {
          _messages.add(ChatMessage(
            role: 'assistant',
            content: '_Routing sources and waiting for the local model…_',
            provider: _provider,
            withAmora: true,
          ));
        });
        _scrollBottom();

        var buffer = '';
        final res = await ApiService.queryStream(
          query: text,
          provider: _provider,
          mode: _mode,
          topK: _topK,
          costSensitive: _costSensitive,
          conflictSensitive: _conflictSensitive,
          forcedRetrieval: _forceRetrieval ? true : null,
          onRetrieval: (_) {},
          onDelta: (chunk) {
            buffer += chunk;
            setState(() {
              if (placeholderIndex < _messages.length) {
                _messages[placeholderIndex] = ChatMessage(
                  role: 'assistant',
                  content: buffer,
                  provider: _provider,
                  withAmora: true,
                );
              }
            });
            _scrollBottom();
          },
        );
        final ans = res.finalAnswer.trim().isNotEmpty
            ? res.finalAnswer
            : (res.evidenceContext.trim().isNotEmpty
                ? 'Synthesized from retrieved sources:\n\n${res.evidenceContext}'
                : 'Model completed execution.');
        setState(() {
          _totalTokens += res.tokens;
          if (placeholderIndex < _messages.length) {
            _messages[placeholderIndex] = ChatMessage(
              role: 'assistant',
              content: ans,
              pipeline: res,
              provider: res.providerUsed.isEmpty ? _provider : res.providerUsed,
              withAmora: true,
            );
          } else {
            _messages.add(ChatMessage(
              role: 'assistant',
              content: ans,
              pipeline: res,
              provider: _provider,
              withAmora: true,
            ));
          }
        });
      } else {
        // Direct LLM call without AMORA RAG
        final res = await ApiService.freeChat(
          question: text,
          provider: _provider,
        );
        final ans = res.answer.trim().isNotEmpty
            ? res.answer
            : 'Model completed execution.';
        setState(() {
          _totalTokens += res.totalTokens;
          _messages.add(ChatMessage(
            role: 'assistant',
            content: ans,
            freeMeta: res,
            provider: _provider,
            withAmora: false,
          ));
        });
      }
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          role: 'assistant',
          content: '⚠️ Error: $e\n\nEnsure backend is running: python -m uvicorn backend.main:app --reload',
          provider: _provider,
          withAmora: _withAmora,
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
      body: Row(
        children: [
          // ── Sidebar Controls ──────────────────────────────────
          _Sidebar(
            provider: _provider,
            withAmora: _withAmora,
            mode: _mode,
            topK: _topK,
            costSensitive: _costSensitive,
            conflictSensitive: _conflictSensitive,
            forceRetrieval: _forceRetrieval,
            totalTokens: _totalTokens,
            msgCount: _messages.where((m) => m.role == 'user').length,
            providers: _providers,
            onProviderChanged: (p) => setState(() => _provider = p),
            onAmoraChanged: (v) => setState(() => _withAmora = v),
            onModeChanged: (v) => setState(() => _mode = v),
            onTopKChanged: (v) => setState(() => _topK = v),
            onCostChanged: (v) => setState(() => _costSensitive = v),
            onConflictChanged: (v) => setState(() => _conflictSensitive = v),
            onForceChanged: (v) => setState(() => _forceRetrieval = v),
            onClear: () => setState(() { _messages.clear(); _totalTokens = 0; }),
          ),
          // ── Main Chat Area ────────────────────────────────────
          Expanded(
            child: Column(
              children: [
                _Header(
                  provider: _provider,
                  withAmora: _withAmora,
                  providers: _providers,
                  onProviderChanged: (p) => setState(() => _provider = p),
                  onAmoraChanged: (v) => setState(() => _withAmora = v),
                ),
                // Sample pills
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: _samples.map((s) => ActionChip(
                      label: Text(
                        s.length > 42 ? '${s.substring(0, 42)}…' : s,
                        style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textSecond),
                      ),
                      backgroundColor: AppTheme.bgCard,
                      side: const BorderSide(color: AppTheme.border),
                      onPressed: () => _send(s),
                    )).toList(),
                  ),
                ),
                const Divider(height: 16),
                // Messages
                Expanded(
                  child: ListView.builder(
                    controller: _scroll,
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                    itemCount: _messages.length + (_loading ? 1 : 0),
                    itemBuilder: (ctx, i) {
                      if (i == _messages.length) return _TypingIndicator(provider: _provider);
                      final msg = _messages[i];
                      if (msg.role == 'user') return UserBubble(text: msg.content);
                      return _AssistantMsg(msg: msg);
                    },
                  ),
                ),
                // Input
                _InputBar(
                  ctrl: _ctrl,
                  loading: _loading,
                  provider: _provider,
                  withAmora: _withAmora,
                  onSend: _send,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ── Top Header Bar ──────────────────────────────────────────────────────────
class _Header extends StatelessWidget {
  final String provider;
  final bool withAmora;
  final List<(String, String, String, IconData)> providers;
  final ValueChanged<String> onProviderChanged;
  final ValueChanged<bool> onAmoraChanged;

  const _Header({
    required this.provider,
    required this.withAmora,
    required this.providers,
    required this.onProviderChanged,
    required this.onAmoraChanged,
  });

  String get _providerLabel =>
      providers.firstWhere((p) => p.$1 == provider, orElse: () => (provider, provider, '', Icons.smart_toy)).$2;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 12, 18, 12),
      decoration: const BoxDecoration(
        color: AppTheme.bgCard2,
        border: Border(bottom: BorderSide(color: AppTheme.border)),
      ),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              gradient: withAmora ? AppTheme.accentGrad : null,
              color: withAmora ? null : AppTheme.bgCard,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: withAmora ? Colors.transparent : AppTheme.border,
              ),
            ),
            child: Icon(
              withAmora ? Icons.auto_awesome : Icons.bolt,
              color: withAmora ? Colors.white : AppTheme.orange,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      _providerLabel,
                      style: GoogleFonts.inter(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: withAmora
                            ? AppTheme.accent.withValues(alpha: 0.2)
                            : AppTheme.orange.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: withAmora ? AppTheme.accent : AppTheme.orange,
                          width: 0.8,
                        ),
                      ),
                      child: Text(
                        withAmora ? '⚡ AMORA RAG ON' : '⚪ DIRECT (NO RAG)',
                        style: GoogleFonts.inter(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          color: withAmora ? AppTheme.accentLight : AppTheme.orange,
                        ),
                      ),
                    ),
                  ],
                ),
                Text(
                  withAmora
                      ? 'Multi-Objective Evidence Routing & Context Grounding'
                      : 'Direct model output without retrieval augmentation',
                  style: GoogleFonts.inter(fontSize: 11, color: AppTheme.textMuted),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          // Compact Provider Selector for fast switching
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
            decoration: BoxDecoration(
              color: AppTheme.bgCard,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppTheme.border),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: provider,
                icon: const Icon(Icons.arrow_drop_down, color: AppTheme.accentLight, size: 20),
                dropdownColor: AppTheme.bgCard,
                style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textPrimary, fontWeight: FontWeight.w600),
                onChanged: (v) => onProviderChanged(v!),
                items: providers.map((p) => DropdownMenuItem(
                  value: p.$1,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(p.$4, size: 14, color: AppTheme.accentLight),
                      const SizedBox(width: 6),
                      Text(p.$2),
                    ],
                  ),
                )).toList(),
              ),
            ),
          ),
          const SizedBox(width: 8),
          // Quick AMORA Toggle button
          InkWell(
            borderRadius: BorderRadius.circular(8),
            onTap: () => onAmoraChanged(!withAmora),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: withAmora
                    ? AppTheme.accent.withValues(alpha: 0.2)
                    : AppTheme.bgCard,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: withAmora ? AppTheme.accent : AppTheme.border,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    withAmora ? Icons.verified : Icons.do_not_disturb_on_outlined,
                    size: 14,
                    color: withAmora ? AppTheme.accentLight : AppTheme.textMuted,
                  ),
                  const SizedBox(width: 5),
                  Text(
                    'AMORA',
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: withAmora ? AppTheme.accentLight : AppTheme.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Sidebar Controls ────────────────────────────────────────────────────────
class _Sidebar extends StatelessWidget {
  final String provider;
  final bool withAmora;
  final String mode;
  final int topK;
  final bool costSensitive, conflictSensitive, forceRetrieval;
  final int totalTokens, msgCount;
  final List<(String, String, String, IconData)> providers;
  final ValueChanged<String> onProviderChanged;
  final ValueChanged<bool> onAmoraChanged;
  final ValueChanged<String> onModeChanged;
  final ValueChanged<int> onTopKChanged;
  final ValueChanged<bool> onCostChanged, onConflictChanged, onForceChanged;
  final VoidCallback onClear;

  const _Sidebar({
    required this.provider,
    required this.withAmora,
    required this.mode,
    required this.topK,
    required this.costSensitive,
    required this.conflictSensitive,
    required this.forceRetrieval,
    required this.totalTokens,
    required this.msgCount,
    required this.providers,
    required this.onProviderChanged,
    required this.onAmoraChanged,
    required this.onModeChanged,
    required this.onTopKChanged,
    required this.onCostChanged,
    required this.onConflictChanged,
    required this.onForceChanged,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width < 750;
    if (isMobile) return const SizedBox.shrink();

    return Container(
      width: 250,
      decoration: const BoxDecoration(
        color: AppTheme.bgCard2,
        border: Border(right: BorderSide(color: AppTheme.border)),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 8),
            _sectionLabel('1. Choose LLM Engine'),
            ...providers.map((p) {
              final isSel = provider == p.$1;
              return Container(
                margin: const EdgeInsets.only(bottom: 6),
                decoration: BoxDecoration(
                  color: isSel ? AppTheme.accent.withValues(alpha: 0.15) : AppTheme.bgCard,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isSel ? AppTheme.accent : AppTheme.border,
                    width: isSel ? 1.5 : 1.0,
                  ),
                ),
                child: ListTile(
                  dense: true,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 0),
                  leading: Icon(p.$4, size: 18, color: isSel ? AppTheme.accentLight : AppTheme.textMuted),
                  title: Text(
                    p.$2,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: isSel ? FontWeight.w700 : FontWeight.w500,
                      color: isSel ? Colors.white : AppTheme.textPrimary,
                    ),
                  ),
                  subtitle: Text(
                    p.$3,
                    style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted),
                  ),
                  onTap: () => onProviderChanged(p.$1),
                ),
              );
            }),
            const Divider(color: AppTheme.border, height: 24),
            _sectionLabel('2. AMORA Pipeline'),
            SwitchListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              value: withAmora,
              title: Text(
                'Connect AMORA RAG',
                style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textPrimary),
              ),
              subtitle: Text(
                withAmora ? 'Multi-source evidence routing' : 'Direct ungrounded generation',
                style: GoogleFonts.inter(fontSize: 11, color: AppTheme.textMuted),
              ),
              thumbColor: WidgetStateProperty.resolveWith(
                (s) => s.contains(WidgetState.selected) ? AppTheme.accent : AppTheme.textMuted,
              ),
              onChanged: onAmoraChanged,
            ),
            if (withAmora) ...[
              const SizedBox(height: 8),
              _label('Ranking Mode'),
              RadioGroup<String>(
                groupValue: mode,
                onChanged: (v) => onModeChanged(v!),
                child: Column(
                  children: [('weighted', 'Weighted (w·s)'), ('pareto', 'Pareto Frontier')].map((e) => ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    leading: Radio<String>(
                      value: e.$1,
                      fillColor: WidgetStateProperty.resolveWith(
                        (states) => states.contains(WidgetState.selected) ? AppTheme.accent : AppTheme.textMuted,
                      ),
                    ),
                    title: Text(e.$2, style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textPrimary)),
                  )).toList(),
                ),
              ),
              const SizedBox(height: 6),
              _label('Top-K Sources: $topK'),
              Slider(
                value: topK.toDouble(),
                min: 1,
                max: 10,
                divisions: 9,
                activeColor: AppTheme.accent,
                inactiveColor: AppTheme.border,
                onChanged: (v) => onTopKChanged(v.round()),
              ),
              _toggle('Cost-Sensitive', costSensitive, onCostChanged),
              _toggle('Conflict-Sensitive', conflictSensitive, onConflictChanged),
              _toggle('Force Retrieval', forceRetrieval, onForceChanged),
            ],
            const Divider(color: AppTheme.border, height: 24),
            _sectionLabel('Session Stats'),
            _statRow('Active Model', provider.toUpperCase()),
            _statRow('RAG Mode', withAmora ? 'AMORA Active' : 'Direct LLM'),
            _statRow('Queries', '$msgCount'),
            _statRow('Total Tokens', '$totalTokens'),
            const SizedBox(height: 14),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                icon: const Icon(Icons.delete_outline, size: 16),
                label: const Text('Clear Chat'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppTheme.textSecond,
                  side: const BorderSide(color: AppTheme.border),
                ),
                onPressed: onClear,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _sectionLabel(String t) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Text(
      t,
      style: GoogleFonts.inter(
        fontSize: 11,
        color: AppTheme.textMuted,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.5,
      ),
    ),
  );

  Widget _label(String t) => Text(t, style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textSecond));

  Widget _toggle(String label, bool val, ValueChanged<bool> onChanged) => SwitchListTile(
    dense: true,
    contentPadding: EdgeInsets.zero,
    value: val,
    title: Text(label, style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textPrimary)),
    thumbColor: WidgetStateProperty.resolveWith(
      (s) => s.contains(WidgetState.selected) ? AppTheme.accent : AppTheme.textMuted,
    ),
    onChanged: onChanged,
  );

  Widget _statRow(String label, String val) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 2),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: GoogleFonts.inter(fontSize: 11, color: AppTheme.textMuted)),
        Text(
          val,
          style: GoogleFonts.inter(fontSize: 12, color: AppTheme.accentLight, fontWeight: FontWeight.w600),
        ),
      ],
    ),
  );
}

// ── Assistant message with expandable pipeline details ─────────────────────
class _AssistantMsg extends StatefulWidget {
  final ChatMessage msg;
  const _AssistantMsg({required this.msg});
  @override
  State<_AssistantMsg> createState() => _AssistantMsgState();
}

class _AssistantMsgState extends State<_AssistantMsg> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final p = widget.msg.pipeline;
    final f = widget.msg.freeMeta;
    final isAmora = widget.msg.withAmora;
    final providerName = widget.msg.provider?.toUpperCase() ?? 'AI';

    Widget? footerWidget;
    if (isAmora && p != null) {
      footerWidget = PipelineMetaRow(
        provider: 'AMORA + $providerName',
        retrieval: p.retrievalRequired,
        latencyMs: p.latencyMs,
        nSources: p.selectedSources.length,
        tokens: p.tokens,
        srr: p.sourceReductionRatio,
        accuracyScore: p.accuracyScore,
        usedStub: p.usedStubResponse,
        llmNote: p.llmNote,
      );
    } else if (f != null) {
      footerWidget = FreeMetaRow(
        provider: '$providerName Direct (No RAG)',
        latencyMs: f.latencyMs,
        tokens: f.totalTokens,
        accuracyScore: f.accuracyScore,
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        AssistantBubble(
          text: widget.msg.content,
          avatarLabel: providerName.isNotEmpty ? providerName[0] : 'A',
          footer: footerWidget,
        ),
        if (p != null && p.selectedSources.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(left: 44, bottom: 8),
            child: GestureDetector(
              onTap: () => setState(() => _expanded = !_expanded),
              child: Row(
                children: [
                  Icon(_expanded ? Icons.expand_less : Icons.expand_more, size: 16, color: AppTheme.accent),
                  const SizedBox(width: 4),
                  Text(
                    '📊 AMORA Evidence Sources (${p.selectedSources.length})',
                    style: GoogleFonts.inter(fontSize: 12, color: AppTheme.accent, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),
          ),
        if (p != null && _expanded)
          Padding(
            padding: const EdgeInsets.only(left: 44, right: 12, bottom: 12),
            child: _PipelineDetail(pipeline: p),
          ),
      ],
    );
  }
}

class _PipelineDetail extends StatelessWidget {
  final QueryResponse pipeline;
  const _PipelineDetail({required this.pipeline});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _statCard('Accuracy', '${(pipeline.accuracyScore * 100).toStringAsFixed(0)}%'),
              const SizedBox(width: 6),
              _statCard('K-Score', pipeline.kActivationScore.toStringAsFixed(3)),
              const SizedBox(width: 6),
              _statCard('Efficiency', pipeline.amoraEfficiencyScore.toStringAsFixed(2)),
              const SizedBox(width: 6),
              _statCard('Evidence', '${pipeline.retrievedEvidenceCount}'),
              const SizedBox(width: 6),
              _statCard('Catalog', '${pipeline.totalCatalogSources}→${pipeline.selectedSources.length}'),
            ],
          ),
          if (pipeline.usedStubResponse) ...[
            const SizedBox(height: 10),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0x1AF97316),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0x33F97316)),
              ),
              child: Text(
                'This answer was NOT generated by a language model. '
                '${pipeline.providerUsed}\n'
                '${pipeline.llmNote.isEmpty ? '' : '${pipeline.llmNote}\n'}'
                'The grounding score is reported as 0% because there is no model '
                'output to ground. Check GET /llm/status.',
                style: GoogleFonts.inter(fontSize: 11, color: AppTheme.orange, height: 1.4),
              ),
            ),
          ],
          if (pipeline.selectedSources.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              'AMORA Ranked Sources',
              style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            ...pipeline.selectedSources.map((s) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Expanded(
                    child: Text(s.name, style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textPrimary)),
                  ),
                  Text(
                    'Rel: ${(s.relevance * 100).toStringAsFixed(0)}%  •  Score: ${(s.score * 100).toStringAsFixed(1)}%',
                    style: GoogleFonts.inter(fontSize: 11, color: AppTheme.accentLight),
                  ),
                ],
              ),
            )),
          ],
        ],
      ),
    );
  }

  Widget _statCard(String label, String val) => Expanded(
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.bg,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        children: [
          Text(val, style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.accentLight)),
          Text(label, style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted)),
        ],
      ),
    ),
  );
}

// ── Typing indicator ────────────────────────────────────────────────────────
class _TypingIndicator extends StatefulWidget {
  final String provider;
  const _TypingIndicator({required this.provider});
  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator> with SingleTickerProviderStateMixin {
  late AnimationController _anim;
  @override
  void initState() {
    super.initState();
    _anim = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..repeat();
  }
  @override
  void dispose() {
    _anim.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final label = widget.provider.isNotEmpty ? widget.provider[0].toUpperCase() : 'A';
    return Padding(
      padding: const EdgeInsets.only(right: 48, bottom: 12),
      child: Row(
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: const BoxDecoration(gradient: AppTheme.accentGrad, shape: BoxShape.circle),
            child: Center(
              child: Text(label, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700)),
            ),
          ),
          const SizedBox(width: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(
              color: AppTheme.bgCard,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppTheme.border),
            ),
            child: AnimatedBuilder(
              animation: _anim,
              builder: (_, __) => Row(
                children: List.generate(3, (i) {
                  final t = (_anim.value - i * 0.2).clamp(0.0, 1.0);
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 3),
                    child: Transform.translate(
                      offset: Offset(0, -4 * (t < 0.5 ? t * 2 : (1 - t) * 2)),
                      child: Container(
                        width: 7,
                        height: 7,
                        decoration: const BoxDecoration(color: AppTheme.accentLight, shape: BoxShape.circle),
                      ),
                    ),
                  );
                }),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Input Bar ───────────────────────────────────────────────────────────────
class _InputBar extends StatelessWidget {
  final TextEditingController ctrl;
  final bool loading;
  final String provider;
  final bool withAmora;
  final ValueChanged<String> onSend;

  const _InputBar({
    required this.ctrl,
    required this.loading,
    required this.provider,
    required this.withAmora,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    final hint = withAmora
        ? 'Ask $provider via AMORA RAG pipeline…'
        : 'Ask $provider directly (no RAG)…';

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 16),
      decoration: const BoxDecoration(border: Border(top: BorderSide(color: AppTheme.border))),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: ctrl,
              enabled: !loading,
              onSubmitted: onSend,
              maxLines: null,
              style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14),
              decoration: InputDecoration(
                hintText: hint,
                prefixIcon: Icon(
                  withAmora ? Icons.verified : Icons.chat_bubble_outline,
                  size: 18,
                  color: withAmora ? AppTheme.accentLight : AppTheme.textMuted,
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            child: loading
                ? const SizedBox(
                    width: 44,
                    height: 44,
                    child: Padding(
                      padding: EdgeInsets.all(10),
                      child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.accent),
                    ),
                  )
                : IconButton(
                    onPressed: () => onSend(ctrl.text),
                    icon: const Icon(Icons.send_rounded),
                    style: IconButton.styleFrom(
                      backgroundColor: withAmora ? AppTheme.accent : AppTheme.orange,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
