// AMOF Dual-Panel LLM Comparison Screen
// Simultaneously compares:
//   1. LLM with AMORA RAG vs LLM without AMORA (Direct)
//   2. Qwen + AMORA vs other LLMs (Groq, Gemini, Mistral, HuggingFace, Cohere) without Qwen
//   3. Different LLMs both connected to AMORA RAG
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class CompareScreen extends StatefulWidget {
  const CompareScreen({super.key});

  @override
  State<CompareScreen> createState() => _CompareScreenState();
}

class _CompareResult {
  final String query;
  final String providerA;
  final bool amoraA;
  final String answerA;
  final double latencyA;
  final int tokensA;
  final double accuracyA;
  final QueryResponse? pipelineA;
  final String? errorA;

  final String providerB;
  final bool amoraB;
  final String answerB;
  final double latencyB;
  final int tokensB;
  final double accuracyB;
  final QueryResponse? pipelineB;
  final String? errorB;

  _CompareResult({
    required this.query,
    required this.providerA,
    required this.amoraA,
    required this.answerA,
    required this.latencyA,
    required this.tokensA,
    required this.accuracyA,
    this.pipelineA,
    this.errorA,
    required this.providerB,
    required this.amoraB,
    required this.answerB,
    required this.latencyB,
    required this.tokensB,
    required this.accuracyB,
    this.pipelineB,
    this.errorB,
  });
}

class _CompareScreenState extends State<CompareScreen> {
  final TextEditingController _queryCtrl = TextEditingController();
  final ScrollController _scrollCtrl = ScrollController();

  // Panel A Config
  String _providerA = 'qwen';
  bool _amoraA = true;
  String _modeA = 'weighted';
  int _topKA = 5;

  // Panel B Config
  String _providerB = 'groq';
  bool _amoraB = false;
  String _modeB = 'weighted';
  int _topKB = 5;

  bool _loading = false;
  final List<_CompareResult> _history = [];

  static const _providers = [
    ('qwen', 'Qwen 2.5 (Local/Ollama)', Icons.terminal),
    ('groq', 'Groq (Llama 3.1 - Free)', Icons.bolt),
    ('gemini', 'Google Gemini 1.5', Icons.auto_awesome),
    ('mistral', 'Mistral 7B', Icons.waves),
    ('huggingface', 'HuggingFace', Icons.hub),
    ('cohere', 'Cohere Command-R', Icons.forest),
  ];

  static const _samples = [
    'What is the current inventory of Quantum X Laptop?',
    'What does the return policy say about unopened merchandise?',
    'Which product has the highest sales revenue?',
    'Compare the product spec with the company manual.',
  ];

  void _applyPreset(String pA, bool amA, String pB, bool amB) {
    setState(() {
      _providerA = pA;
      _amoraA = amA;
      _providerB = pB;
      _amoraB = amB;
    });
  }

  Future<void> _compare(String query) async {
    final q = query.trim();
    if (q.isEmpty || _loading) return;

    setState(() => _loading = true);

    final bool bothLocal = (_providerA == 'qwen' || _providerA == 'ollama') &&
                           (_providerB == 'qwen' || _providerB == 'ollama');

    late final ({String answer, double latency, int tokens, double accuracy, QueryResponse? pipeline, String? error}) resA;
    late final ({String answer, double latency, int tokens, double accuracy, QueryResponse? pipeline, String? error}) resB;

    if (bothLocal) {
      // Run sequentially to prevent overloading local CPU/RAM with two 36B models simultaneously
      resA = await _runSingle(q, _providerA, _amoraA, _modeA, _topKA);
      resB = await _runSingle(q, _providerB, _amoraB, _modeB, _topKB);
    } else {
      // Run in parallel for high speed
      final futureA = _runSingle(q, _providerA, _amoraA, _modeA, _topKA);
      final futureB = _runSingle(q, _providerB, _amoraB, _modeB, _topKB);
      final results = await Future.wait([futureA, futureB]);
      resA = results[0];
      resB = results[1];
    }

    setState(() {
      _history.insert(
        0,
        _CompareResult(
          query: q,
          providerA: _providerA,
          amoraA: _amoraA,
          answerA: resA.answer,
          latencyA: resA.latency,
          tokensA: resA.tokens,
          accuracyA: resA.accuracy,
          pipelineA: resA.pipeline,
          errorA: resA.error,
          providerB: _providerB,
          amoraB: _amoraB,
          answerB: resB.answer,
          latencyB: resB.latency,
          tokensB: resB.tokens,
          accuracyB: resB.accuracy,
          pipelineB: resB.pipeline,
          errorB: resB.error,
        ),
      );
      _loading = false;
    });

    // Scroll to top
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          0,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<({String answer, double latency, int tokens, double accuracy, QueryResponse? pipeline, String? error})>
      _runSingle(String q, String provider, bool withAmora, String mode, int topK) async {
    final stopwatch = Stopwatch()..start();
    try {
      if (withAmora) {
        final res = await ApiService.query(
          query: q,
          provider: provider,
          mode: mode,
          topK: topK,
          forcedRetrieval: true,
        );
        stopwatch.stop();
        final ans = res.finalAnswer.trim().isNotEmpty
            ? res.finalAnswer
            : (res.evidenceContext.trim().isNotEmpty
                ? 'Synthesized from retrieved sources:\n\n${res.evidenceContext}'
                : 'Model completed execution.');
        return (
          answer: ans,
          latency: res.latencyMs > 0 ? res.latencyMs : stopwatch.elapsedMilliseconds.toDouble(),
          tokens: res.tokens,
          accuracy: res.accuracyScore,
          pipeline: res,
          error: null,
        );
      } else {
        final res = await ApiService.freeChat(
          question: q,
          provider: provider,
        );
        stopwatch.stop();
        final ans = res.answer.trim().isNotEmpty
            ? res.answer
            : 'Model completed execution.';
        return (
          answer: ans,
          latency: res.latencyMs > 0 ? res.latencyMs : stopwatch.elapsedMilliseconds.toDouble(),
          tokens: res.totalTokens,
          accuracy: res.accuracyScore,
          pipeline: null,
          error: null,
        );
      }
    } catch (e) {
      stopwatch.stop();
      final errStr = e.toString();
      String friendlyMsg = errStr;
      if (errStr.contains('TimeoutException')) {
        friendlyMsg = 'Timed out: The model took longer than the timeout limit. For local models on CPU (such as Qwen 36B), inference can take 1-2 minutes. Tip: Try cloud models (Groq / Gemini) for instant ~500ms answers, or pull a lighter model like qwen2.5:7b.';
      }
      return (
        answer: 'Failed to generate answer from $provider.',
        latency: stopwatch.elapsedMilliseconds.toDouble(),
        tokens: 0,
        accuracy: 0.0,
        pipeline: null,
        error: friendlyMsg,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Column(
        children: [
          _buildTopConfigBanner(),
          Expanded(
            child: ListView(
              controller: _scrollCtrl,
              padding: const EdgeInsets.all(16),
              children: [
                _buildPresetsRow(),
                const SizedBox(height: 12),
                _buildQueryInputCard(),
                const SizedBox(height: 16),
                if (_loading) _buildLoadingCard(),
                if (_history.isEmpty && !_loading) _buildEmptyState(),
                ..._history.map((item) => _buildComparisonCard(item)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Top Config Banner with side-by-side panel selectors ────────────────────
  Widget _buildTopConfigBanner() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 14, 20, 14),
      decoration: const BoxDecoration(
        color: AppTheme.bgCard2,
        border: Border(bottom: BorderSide(color: AppTheme.border)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  gradient: AppTheme.accentGrad,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.compare_arrows_rounded, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Simultaneous LLM Comparison',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  Text(
                    'Benchmark answers, latency, and tokens with or without AMORA RAG',
                    style: GoogleFonts.inter(fontSize: 11, color: AppTheme.textMuted),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 14),
          // Two Panel Configurations
          LayoutBuilder(
            builder: (ctx, constraints) {
              final isWide = constraints.maxWidth > 700;
              final panelA = _buildPanelSelector(
                title: 'Panel A (Left)',
                badgeColor: AppTheme.accent,
                provider: _providerA,
                withAmora: _amoraA,
                mode: _modeA,
                topK: _topKA,
                onProviderChanged: (v) => setState(() => _providerA = v),
                onAmoraChanged: (v) => setState(() => _amoraA = v),
                onModeChanged: (v) => setState(() => _modeA = v),
                onTopKChanged: (v) => setState(() => _topKA = v),
              );
              final panelB = _buildPanelSelector(
                title: 'Panel B (Right)',
                badgeColor: AppTheme.orange,
                provider: _providerB,
                withAmora: _amoraB,
                mode: _modeB,
                topK: _topKB,
                onProviderChanged: (v) => setState(() => _providerB = v),
                onAmoraChanged: (v) => setState(() => _amoraB = v),
                onModeChanged: (v) => setState(() => _modeB = v),
                onTopKChanged: (v) => setState(() => _topKB = v),
              );

              if (isWide) {
                return Row(
                  children: [
                    Expanded(child: panelA),
                    const SizedBox(width: 12),
                    Expanded(child: panelB),
                  ],
                );
              } else {
                return Column(
                  children: [
                    panelA,
                    const SizedBox(height: 10),
                    panelB,
                  ],
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildPanelSelector({
    required String title,
    required Color badgeColor,
    required String provider,
    required bool withAmora,
    required String mode,
    required int topK,
    required ValueChanged<String> onProviderChanged,
    required ValueChanged<bool> onAmoraChanged,
    required ValueChanged<String> onModeChanged,
    required ValueChanged<int> onTopKChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: badgeColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(color: badgeColor, shape: BoxShape.circle),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    title,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ],
              ),
              // AMORA Toggle Switch
              InkWell(
                borderRadius: BorderRadius.circular(6),
                onTap: () => onAmoraChanged(!withAmora),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: withAmora
                        ? AppTheme.accent.withValues(alpha: 0.2)
                        : AppTheme.bg,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(
                      color: withAmora ? AppTheme.accent : AppTheme.border,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        withAmora ? Icons.verified : Icons.do_not_disturb_alt,
                        size: 13,
                        color: withAmora ? AppTheme.accentLight : AppTheme.textMuted,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        withAmora ? 'AMORA: ON' : 'AMORA: OFF',
                        style: GoogleFonts.inter(
                          fontSize: 10,
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
          const SizedBox(height: 8),
          // Dropdown LLM Selector
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 0),
            decoration: BoxDecoration(
              color: AppTheme.bg,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: AppTheme.border),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                isExpanded: true,
                value: provider,
                dropdownColor: AppTheme.bgCard,
                icon: const Icon(Icons.arrow_drop_down, color: AppTheme.accentLight, size: 20),
                style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textPrimary, fontWeight: FontWeight.w600),
                onChanged: (v) => onProviderChanged(v!),
                items: _providers.map((p) => DropdownMenuItem(
                  value: p.$1,
                  child: Row(
                    children: [
                      Icon(p.$3, size: 14, color: AppTheme.accentLight),
                      const SizedBox(width: 8),
                      Text(p.$2),
                    ],
                  ),
                )).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Presets Row ────────────────────────────────────────────────────────────
  Widget _buildPresetsRow() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          Text(
            'Presets:',
            style: GoogleFonts.inter(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: AppTheme.textMuted,
            ),
          ),
          const SizedBox(width: 8),
          _presetChip(
            label: 'AMORA vs Direct (Groq)',
            onTap: () => _applyPreset('groq', true, 'groq', false),
          ),
          const SizedBox(width: 6),
          _presetChip(
            label: 'Qwen + AMORA vs Groq Direct',
            highlight: true,
            onTap: () => _applyPreset('qwen', true, 'groq', false),
          ),
          const SizedBox(width: 6),
          _presetChip(
            label: 'Qwen + AMORA vs Gemini Direct',
            onTap: () => _applyPreset('qwen', true, 'gemini', false),
          ),
          const SizedBox(width: 6),
          _presetChip(
            label: 'Groq+AMORA vs Gemini+AMORA',
            onTap: () => _applyPreset('groq', true, 'gemini', true),
          ),
        ],
      ),
    );
  }

  Widget _presetChip({required String label, required VoidCallback onTap, bool highlight = false}) {
    return ActionChip(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
      label: Text(label, style: GoogleFonts.inter(fontSize: 11, color: highlight ? Colors.white : AppTheme.textSecond)),
      backgroundColor: highlight ? AppTheme.accent.withValues(alpha: 0.3) : AppTheme.bgCard,
      side: BorderSide(color: highlight ? AppTheme.accent : AppTheme.border),
      onPressed: onTap,
    );
  }

  // ── Query Input Card ───────────────────────────────────────────────────────
  Widget _buildQueryInputCard() {
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
          // Sample Chips
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: _samples.map((s) => ActionChip(
              label: Text(
                s.length > 40 ? '${s.substring(0, 40)}…' : s,
                style: GoogleFonts.inter(fontSize: 11, color: AppTheme.textSecond),
              ),
              backgroundColor: AppTheme.bg,
              side: const BorderSide(color: AppTheme.border),
              onPressed: () {
                _queryCtrl.text = s;
                _compare(s);
              },
            )).toList(),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _queryCtrl,
                  enabled: !_loading,
                  onSubmitted: _compare,
                  style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 13),
                  decoration: const InputDecoration(
                    hintText: 'Enter question to send simultaneously to both panels…',
                    prefixIcon: Icon(Icons.search, size: 18, color: AppTheme.accentLight),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              FilledButton.icon(
                onPressed: _loading ? null : () => _compare(_queryCtrl.text),
                style: FilledButton.styleFrom(
                  backgroundColor: AppTheme.accent,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: const Icon(Icons.flash_on_rounded, size: 18),
                label: Text(
                  'Compare Both',
                  style: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 13),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ── Loading Card ───────────────────────────────────────────────────────────
  Widget _buildLoadingCard() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.accent.withValues(alpha: 0.5)),
      ),
      child: Column(
        children: [
          const CircularProgressIndicator(color: AppTheme.accent, strokeWidth: 2.5),
          const SizedBox(height: 14),
          Text(
            'Querying Panel A & Panel B simultaneously…',
            style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: AppTheme.textPrimary),
          ),
          const SizedBox(height: 6),
          Text(
            'Evaluating retrieval, latency, and token footprint in real-time',
            style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted),
          ),
        ],
      ),
    );
  }

  // ── Empty State ────────────────────────────────────────────────────────────
  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
      alignment: Alignment.center,
      child: Column(
        children: [
          Icon(Icons.compare_arrows_rounded, size: 48, color: AppTheme.textMuted.withValues(alpha: 0.4)),
          const SizedBox(height: 12),
          Text(
            'No Comparisons Yet',
            style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600, color: AppTheme.textSecond),
          ),
          const SizedBox(height: 6),
          Text(
            'Choose your two models above and click "Compare Both" to view side-by-side synthesis!',
            style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  // ── Comparison Result Card ─────────────────────────────────────────────────
  Widget _buildComparisonCard(_CompareResult item) {
    final bool aFaster = item.latencyA > 0 && (item.latencyA < item.latencyB || item.latencyB == 0);
    final double diffMs = (item.latencyA - item.latencyB).abs();
    final bool aMoreAccurate = item.accuracyA > item.accuracyB;
    final bool accDiffSignificant = (item.accuracyA - item.accuracyB).abs() >= 0.05;

    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Query + Winner summary
          Container(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
            decoration: const BoxDecoration(
              color: AppTheme.bgCard2,
              borderRadius: BorderRadius.vertical(top: Radius.circular(14)),
              border: Border(bottom: BorderSide(color: AppTheme.border)),
            ),
            child: Row(
              children: [
                const Icon(Icons.help_outline, size: 18, color: AppTheme.accentLight),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    item.query,
                    style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.textPrimary),
                  ),
                ),
                // Accuracy Badge
                if (accDiffSignificant) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.green.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppTheme.green),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.verified, size: 13, color: AppTheme.green),
                        const SizedBox(width: 4),
                        Text(
                          aMoreAccurate
                              ? 'Panel A: ${(item.accuracyA * 100).toStringAsFixed(0)}% Accuracy'
                              : 'Panel B: ${(item.accuracyB * 100).toStringAsFixed(0)}% Accuracy',
                          style: GoogleFonts.inter(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: AppTheme.green,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                ],
                // Speed Badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                  decoration: BoxDecoration(
                    color: aFaster
                        ? AppTheme.accent.withValues(alpha: 0.15)
                        : AppTheme.orange.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: aFaster ? AppTheme.accent : AppTheme.orange),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.speed, size: 13, color: Colors.white70),
                      const SizedBox(width: 4),
                      Text(
                        aFaster
                            ? 'Panel A faster (-${diffMs.toStringAsFixed(0)}ms)'
                            : 'Panel B faster (-${diffMs.toStringAsFixed(0)}ms)',
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: aFaster ? AppTheme.accentLight : AppTheme.orange,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Explanatory trade-off insight banner when comparing RAG vs Non-RAG
          if (item.amoraA != item.amoraB)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: AppTheme.accent.withValues(alpha: 0.08),
                border: const Border(bottom: BorderSide(color: AppTheme.border)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, size: 15, color: AppTheme.accentLight),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item.amoraA
                          ? 'AMORA RAG dynamically routed top enterprise sources for Panel A (reducing tokens & latency via Pareto ranking), delivering authoritative accuracy (${(item.accuracyA * 100).toStringAsFixed(0)}%) vs unrouted baseline (${(item.accuracyB * 100).toStringAsFixed(0)}%).'
                          : 'AMORA RAG dynamically routed top enterprise sources for Panel B (reducing tokens & latency via Pareto ranking), delivering authoritative accuracy (${(item.accuracyB * 100).toStringAsFixed(0)}%) vs unrouted baseline (${(item.accuracyA * 100).toStringAsFixed(0)}%).',
                      style: GoogleFonts.inter(fontSize: 11.5, color: AppTheme.textSecond, height: 1.4),
                    ),
                  ),
                ],
              ),
            ),
          // Side-by-side Response Panels
          LayoutBuilder(
            builder: (ctx, constraints) {
              final isWide = constraints.maxWidth > 750;
              final panelAWidget = _buildResponsePanel(
                panelName: 'Panel A',
                provider: item.providerA,
                withAmora: item.amoraA,
                answer: item.answerA,
                latency: item.latencyA,
                tokens: item.tokensA,
                accuracy: item.accuracyA,
                pipeline: item.pipelineA,
                error: item.errorA,
                isWinner: aFaster,
                accentColor: AppTheme.accent,
              );

              final panelBWidget = _buildResponsePanel(
                panelName: 'Panel B',
                provider: item.providerB,
                withAmora: item.amoraB,
                answer: item.answerB,
                latency: item.latencyB,
                tokens: item.tokensB,
                accuracy: item.accuracyB,
                pipeline: item.pipelineB,
                error: item.errorB,
                isWinner: !aFaster,
                accentColor: AppTheme.orange,
              );

              if (isWide) {
                return IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Expanded(child: panelAWidget),
                      const VerticalDivider(width: 1, color: AppTheme.border),
                      Expanded(child: panelBWidget),
                    ],
                  ),
                );
              } else {
                return Column(
                  children: [
                    panelAWidget,
                    const Divider(height: 1, color: AppTheme.border),
                    panelBWidget,
                  ],
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildResponsePanel({
    required String panelName,
    required String provider,
    required bool withAmora,
    required String answer,
    required double latency,
    required int tokens,
    required double accuracy,
    required QueryResponse? pipeline,
    required String? error,
    required bool isWinner,
    required Color accentColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header info
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: accentColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: accentColor),
                    ),
                    child: Text(
                      panelName,
                      style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w700, color: accentColor),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    provider.toUpperCase(),
                    style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.textPrimary),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: withAmora ? AppTheme.accent.withValues(alpha: 0.2) : AppTheme.bg,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: withAmora ? AppTheme.accent : AppTheme.border),
                ),
                child: Text(
                  withAmora ? '⚡ AMORA RAG' : '⚪ DIRECT (NO RAG)',
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: withAmora ? AppTheme.accentLight : AppTheme.textMuted,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          // Metric chips
          Wrap(
            spacing: 6,
            runSpacing: 4,
            children: [
              _metricChip(
                '🎯 ${(accuracy * 100).toStringAsFixed(0)}% Accuracy',
                accuracy >= 0.70 ? AppTheme.green : AppTheme.orange,
              ),
              _metricChip('⏱ ${latency.toStringAsFixed(0)} ms', isWinner ? AppTheme.green : AppTheme.textMuted),
              _metricChip('🪙 $tokens tokens', AppTheme.textMuted),
              if (withAmora && pipeline != null)
                _metricChip('🗂 ${pipeline.selectedSources.length} sources', AppTheme.accentLight)
              else
                _metricChip('🗂 0 sources (direct)', AppTheme.textMuted),
            ],
          ),
          const SizedBox(height: 12),
          // Answer
          if (error != null)
            Text(
              '⚠️ $error',
              style: GoogleFonts.inter(fontSize: 12, color: AppTheme.red, height: 1.5),
            )
          else
            SelectableText(
              answer,
              style: GoogleFonts.inter(fontSize: 13, color: AppTheme.textPrimary, height: 1.6),
            ),
          // Collapsible sources if AMORA RAG was active
          if (withAmora && pipeline != null && pipeline.selectedSources.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Divider(color: AppTheme.border, height: 1),
            const SizedBox(height: 8),
            _buildRetrievedSourcesAccordion(pipeline),
          ],
          const SizedBox(height: 10),
          // Copy button
          Align(
            alignment: Alignment.centerRight,
            child: IconButton(
              icon: const Icon(Icons.copy_rounded, size: 16, color: AppTheme.textMuted),
              tooltip: 'Copy Answer',
              onPressed: () {
                Clipboard.setData(ClipboardData(text: answer));
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Answer copied to clipboard!'), duration: Duration(seconds: 1)),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _metricChip(String text, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: AppTheme.bg,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: AppTheme.border),
      ),
      child: Text(text, style: GoogleFonts.inter(fontSize: 11, color: col, fontWeight: FontWeight.w600)),
    );
  }

  Widget _buildRetrievedSourcesAccordion(QueryResponse pipeline) {
    return Theme(
      data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        tilePadding: EdgeInsets.zero,
        dense: true,
        title: Text(
          '🔍 ${pipeline.selectedSources.length} Evidence Sources Ranked by AMORA',
          style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.accentLight),
        ),
        children: pipeline.selectedSources.map((s) {
          return Container(
            margin: const EdgeInsets.only(bottom: 6),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.bg,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: AppTheme.border),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(s.name, style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textPrimary)),
                      Text('Tool: ${s.tool}  •  Relevance: ${(s.relevance * 100).toStringAsFixed(0)}%',
                          style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted)),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppTheme.accent.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    '${(s.score * 100).toStringAsFixed(1)}%',
                    style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.w700, color: AppTheme.accentLight),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}
