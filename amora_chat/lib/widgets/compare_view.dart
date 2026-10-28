// widgets/compare_view.dart
import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../theme/app_theme.dart';
import 'message_bubble.dart';

/// Renders one CompareMessage as two side-by-side columns (AMORA vs Direct)
class CompareView extends StatelessWidget {
  final CompareMessage cmp;
  const CompareView({super.key, required this.cmp});

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // User query row
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(mainAxisAlignment: MainAxisAlignment.end, children: [
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF4F46E5), Color(0xFF7C3AED)],
                    ),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(18), topRight: Radius.circular(18),
                      bottomLeft: Radius.circular(18), bottomRight: Radius.circular(4),
                    ),
                    boxShadow: [BoxShadow(color: AppTheme.accent.withOpacity(0.3), blurRadius: 12)],
                  ),
                  child: Text(cmp.query,
                      style: const TextStyle(color: Color(0xFFF5F3FF), fontSize: 14, height: 1.5)),
                ),
              ),
              const SizedBox(width: 8),
              const CircleAvatar(radius: 16, backgroundColor: AppTheme.bg3,
                  child: Icon(Icons.person, size: 16, color: AppTheme.textMuted)),
            ]),
          ),
          // Two response columns
          IntrinsicHeight(
            child: Row(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              // AMOF column
              Expanded(child: _ResponseColumn(
                label: '🤖 LLM with AMOF',
                color: AppTheme.accent2,
                message: cmp.amoraMessage,
              )),
              const SizedBox(width: 10),
              // Direct column
              Expanded(child: _ResponseColumn(
                label: '⚡ LLM without AMOF',
                color: AppTheme.orange,
                message: cmp.directMessage,
              )),
            ]),
          ),
          // Delta card
          if (_bothDone(cmp)) _DeltaCard(cmp: cmp),
          const SizedBox(height: 12),
          const Divider(color: AppTheme.border, height: 1),
          const SizedBox(height: 4),
        ],
      );

  bool _bothDone(CompareMessage c) =>
      c.amoraMessage != null && !c.amoraMessage!.isStreaming &&
      c.directMessage != null && !c.directMessage!.isStreaming;
}

class _ResponseColumn extends StatelessWidget {
  final String label;
  final Color color;
  final ChatMessage? message;
  const _ResponseColumn({required this.label, required this.color, this.message});

  @override
  Widget build(BuildContext context) => Container(
        decoration: BoxDecoration(
          color: AppTheme.bg2, borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.25)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          // Column header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
              border: Border(bottom: BorderSide(color: color.withOpacity(0.25))),
            ),
            child: Row(children: [
              Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: color)),
              const Spacer(),
              if (message?.isStreaming == true)
                SizedBox(
                  width: 14, height: 14,
                  child: CircularProgressIndicator(strokeWidth: 2, color: color),
                ),
            ]),
          ),
          // Content
          Padding(
            padding: const EdgeInsets.all(14),
            child: message == null
                ? _buildWaiting(color)
                : MessageBubble(message: message!, compact: true),
          ),
        ]),
      );

  Widget _buildWaiting(Color c) => Row(children: [
        SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: c)),
        const SizedBox(width: 8),
        Text('Processing…', style: TextStyle(color: c, fontSize: 12)),
      ]);
}

// ── Delta comparison card ─────────────────────────────────────────────────────
class _DeltaCard extends StatelessWidget {
  final CompareMessage cmp;
  const _DeltaCard({required this.cmp});

  @override
  Widget build(BuildContext context) {
    final amoraPipeline = cmp.amoraMessage?.pipeline;
    final amoraLatency  = (cmp.amoraMessage?.latencyMs ?? 0) > 0 ? cmp.amoraMessage!.latencyMs : (amoraPipeline?.latencyMs ?? 0);
    final amoraSources  = amoraPipeline?.selectedSources.length ?? 0;
    final amoraTokens   = (cmp.amoraMessage?.tokens ?? 0) > 0 ? cmp.amoraMessage!.tokens : (amoraPipeline?.tokens ?? 0);
    final amoraSRR      = amoraPipeline?.sourceReductionRatio ?? 0;

    final directLatency = cmp.directMessage?.latencyMs ?? 0;
    final directTokens  = cmp.directMessage?.tokens ?? 0;

    // Word count comparison
    final amoraWords  = (cmp.amoraMessage?.content.split(RegExp(r'\s+')).length ?? 0);
    final directWords = (cmp.directMessage?.content.split(RegExp(r'\s+')).length ?? 0);
    final wordDelta   = amoraWords - directWords;

    return Container(
      margin: const EdgeInsets.only(top: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppTheme.accent2.withOpacity(0.06), AppTheme.green.withOpacity(0.06)],
        ),
        border: Border.all(color: AppTheme.border),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('📊 Side-by-Side Comparison Metrics (LLM with AMOF  vs  LLM without AMOF)',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
        const SizedBox(height: 10),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(children: [
            _DeltaChip('AMOF Latency', '${amoraLatency.toStringAsFixed(0)}ms', AppTheme.accent2),
            const SizedBox(width: 8),
            _DeltaChip('Direct Latency', '${directLatency.toStringAsFixed(0)}ms', AppTheme.orange),
            const SizedBox(width: 8),
            _DeltaChip('AMOF Tokens', '$amoraTokens tok', AppTheme.purple),
            const SizedBox(width: 8),
            _DeltaChip('Direct Tokens', '$directTokens tok', AppTheme.orange),
            const SizedBox(width: 8),
            _DeltaChip('AMOF Sources', '$amoraSources src', AppTheme.green),
            const SizedBox(width: 8),
            _DeltaChip('Direct Sources', '0 src', AppTheme.textMuted),
            const SizedBox(width: 8),
            _DeltaChip('SRR Score', amoraSRR.toStringAsFixed(3), AppTheme.green),
            const SizedBox(width: 8),
            _DeltaChip(
              wordDelta >= 0 ? 'AMOF +$wordDelta words' : 'Direct +${-wordDelta} words',
              wordDelta >= 0 ? 'More detailed' : 'More concise',
              wordDelta >= 0 ? AppTheme.green : AppTheme.textMuted,
            ),
          ]),
        ),
      ]),
    );
  }
}

class _DeltaChip extends StatelessWidget {
  final String label, value;
  final Color color;
  const _DeltaChip(this.label, this.value, this.color);
  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1), border: Border.all(color: color.withOpacity(0.3)),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Column(children: [
          Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: color)),
          const SizedBox(height: 2),
          Text(label, style: const TextStyle(fontSize: 10, color: AppTheme.textMuted)),
        ]),
      );
}
