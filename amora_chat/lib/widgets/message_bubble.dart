// widgets/message_bubble.dart
import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../theme/app_theme.dart';
import 'pipeline_drawer.dart';

class MessageBubble extends StatelessWidget {
  final ChatMessage message;
  final bool compact;

  const MessageBubble({super.key, required this.message, this.compact = false});

  @override
  Widget build(BuildContext context) {
    return message.role == MessageRole.user
        ? _UserBubble(message: message)
        : _AssistantBubble(message: message, compact: compact);
  }
}

// ── User bubble ───────────────────────────────────────────────────────────────
class _UserBubble extends StatelessWidget {
  final ChatMessage message;
  const _UserBubble({required this.message});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.end,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Flexible(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF4F46E5), Color(0xFF7C3AED)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(18),
                    topRight: Radius.circular(18),
                    bottomLeft: Radius.circular(18),
                    bottomRight: Radius.circular(4),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.accent.withOpacity(0.3),
                      blurRadius: 12, offset: const Offset(0, 4),
                    )
                  ],
                ),
                child: Text(
                  message.content,
                  style: const TextStyle(color: Color(0xFFF5F3FF), fontSize: 14, height: 1.6),
                ),
              ),
            ),
            const SizedBox(width: 8),
            const CircleAvatar(
              radius: 16,
              backgroundColor: AppTheme.bg3,
              child: Icon(Icons.person, size: 16, color: AppTheme.textMuted),
            ),
          ],
        ),
      );
}

// ── Assistant bubble ──────────────────────────────────────────────────────────
class _AssistantBubble extends StatelessWidget {
  final ChatMessage message;
  final bool compact;
  const _AssistantBubble({required this.message, required this.compact});

  Color get _modeColor => message.mode == ChatMode.withAmora
      ? AppTheme.accent2
      : AppTheme.orange;

  String get _modeLabel => message.mode == ChatMode.withAmora
      ? '🤖 LLM with AMOF (${message.model ?? ''})'
      : '⚡ LLM without AMOF (${message.model ?? ''})';

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Avatar
            Container(
              width: 34, height: 34,
              decoration: BoxDecoration(
                gradient: AppTheme.gradient,
                shape: BoxShape.circle,
                boxShadow: [BoxShadow(color: AppTheme.accent.withOpacity(0.4), blurRadius: 10)],
              ),
              child: Center(
                child: Text(
                  (message.model ?? 'A').substring(0, 1).toUpperCase(),
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Flexible(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Mode tag
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: _modeColor.withOpacity(0.12),
                          border: Border.all(color: _modeColor.withOpacity(0.35)),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(_modeLabel,
                            style: TextStyle(color: _modeColor, fontSize: 11, fontWeight: FontWeight.w600)),
                      ),
                      if (message.isStreaming) ...[
                        const SizedBox(width: 8),
                        _TypingDots(),
                      ]
                    ],
                  ),
                  const SizedBox(height: 6),
                  // Content bubble
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppTheme.bg2,
                      border: Border.all(color: AppTheme.border),
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(4),
                        topRight: Radius.circular(18),
                        bottomLeft: Radius.circular(18),
                        bottomRight: Radius.circular(18),
                      ),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 8, offset: const Offset(0, 2))
                      ],
                    ),
                    child: message.content.isEmpty
                        ? _TypingDots()
                        : _SimpleMarkdown(text: message.content),
                  ),
                  // Metrics chips (both with and without AMOF)
                  if (!message.isStreaming) ...[
                    const SizedBox(height: 6),
                    _MetricsChips(message: message),
                  ],
                ],
              ),
            ),
          ],
        ),
      );
}

// ── Metrics chips ────────────────────────────────────────────────────────────
class _MetricsChips extends StatelessWidget {
  final ChatMessage message;
  const _MetricsChips({required this.message});

  @override
  Widget build(BuildContext context) {
    final p = message.pipeline;
    final latency = message.latencyMs > 0 ? message.latencyMs : (p?.latencyMs ?? 0);
    final tokens = message.tokens > 0 ? message.tokens : (p?.tokens ?? 0);

    if (message.mode == ChatMode.withAmora && p != null) {
      return Wrap(
        spacing: 6, runSpacing: 4,
        children: [
          _chip('⏱ ${latency.toStringAsFixed(0)}ms'),
          _chip('🗂 ${p.selectedSources.length} sources', color: AppTheme.green),
          _chip('🪙 $tokens tok'),
          _chip('SRR ${p.sourceReductionRatio.toStringAsFixed(3)}'),
          _chip('Eff ${p.amoraEfficiencyScore.toStringAsFixed(2)}'),
          if (p.conflictDetected) _chip('⚠️ Conflict', color: AppTheme.orange),
          InkWell(
            onTap: () => PipelineDrawer.show(context, p),
            child: _chip('📊 Details', color: AppTheme.accent2, clickable: true),
          ),
        ],
      );
    }

    // Direct LLM without AMOF mode
    return Wrap(
      spacing: 6, runSpacing: 4,
      children: [
        _chip('⏱ ${latency.toStringAsFixed(0)}ms', color: AppTheme.orange),
        _chip('🪙 $tokens tok', color: AppTheme.purple),
        _chip('🚫 0 external sources', color: AppTheme.textMuted),
        _chip('🧠 Parametric only', color: AppTheme.accent2),
      ],
    );
  }

  Widget _chip(String label, {Color? color, bool clickable = false}) {
    final c = color ?? AppTheme.purple;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
      decoration: BoxDecoration(
        color: c.withOpacity(0.1),
        border: Border.all(color: c.withOpacity(0.3)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(label, style: TextStyle(color: c, fontSize: 11, fontWeight: FontWeight.w500)),
    );
  }
}

// ── Typing indicator ──────────────────────────────────────────────────────────
class _TypingDots extends StatefulWidget {
  @override
  State<_TypingDots> createState() => _TypingDotsState();
}

class _TypingDotsState extends State<_TypingDots> with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 900))..repeat();
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _ctrl,
        builder: (_, __) => Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(3, (i) {
            final t = (_ctrl.value - i * 0.15).clamp(0.0, 1.0);
            final opacity = (t < 0.5 ? t * 2 : (1 - t) * 2).clamp(0.2, 1.0);
            return Container(
              margin: const EdgeInsets.symmetric(horizontal: 2),
              width: 6, height: 6,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.textMuted.withOpacity(opacity),
              ),
            );
          }),
        ),
      );
}

// ── Simple Markdown renderer (no external dependency) ─────────────────────────
class _SimpleMarkdown extends StatelessWidget {
  final String text;
  const _SimpleMarkdown({required this.text});

  @override
  Widget build(BuildContext context) {
    final lines = text.split('\n');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: lines.map((line) => _renderLine(line)).toList(),
    );
  }

  Widget _renderLine(String line) {
    // Code block hint
    if (line.startsWith('```')) {
      return Container(
        margin: const EdgeInsets.symmetric(vertical: 2),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: AppTheme.bg3, borderRadius: BorderRadius.circular(6),
          border: Border.all(color: AppTheme.border),
        ),
        child: Text(line.replaceAll('`', ''),
            style: const TextStyle(fontFamily: 'monospace', color: AppTheme.purple, fontSize: 12)),
      );
    }
    // Heading
    if (line.startsWith('### ')) return _heading(line.substring(4), 13, AppTheme.purple);
    if (line.startsWith('## '))  return _heading(line.substring(3), 15, AppTheme.textPrimary);
    if (line.startsWith('# '))   return _heading(line.substring(2), 17, AppTheme.textPrimary);
    // Bullet
    if (line.startsWith('- ') || line.startsWith('* ')) {
      return Padding(
        padding: const EdgeInsets.only(left: 12, top: 1),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('• ', style: TextStyle(color: AppTheme.accent2, fontSize: 14)),
          Expanded(child: _inlineText(line.substring(2))),
        ]),
      );
    }
    // Numbered list
    final numMatch = RegExp(r'^\d+\. (.+)$').firstMatch(line);
    if (numMatch != null) {
      return Padding(
        padding: const EdgeInsets.only(left: 12, top: 1),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${numMatch.group(0)!.split('.')[0]}. ', style: const TextStyle(color: AppTheme.accent2, fontSize: 13)),
          Expanded(child: _inlineText(numMatch.group(1)!)),
        ]),
      );
    }
    // Empty line
    if (line.trim().isEmpty) return const SizedBox(height: 6);
    // Normal line
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 1),
      child: _inlineText(line),
    );
  }

  Widget _heading(String text, double size, Color color) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Text(text, style: TextStyle(color: color, fontSize: size, fontWeight: FontWeight.w700)),
      );

  Widget _inlineText(String line) {
    // Process **bold**, *italic*, `code`, [Source: X]
    final spans = <InlineSpan>[];
    final re = RegExp(r'\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[Source: (.+?)\]');
    int last = 0;
    for (final m in re.allMatches(line)) {
      if (m.start > last) {
        spans.add(TextSpan(text: line.substring(last, m.start)));
      }
      if (m.group(1) != null) {
        spans.add(TextSpan(text: m.group(1), style: const TextStyle(fontWeight: FontWeight.w700, color: AppTheme.textPrimary)));
      } else if (m.group(2) != null) {
        spans.add(TextSpan(text: m.group(2), style: const TextStyle(fontStyle: FontStyle.italic, color: AppTheme.textMuted)));
      } else if (m.group(3) != null) {
        spans.add(WidgetSpan(child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 2),
          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
          decoration: BoxDecoration(color: AppTheme.bg3, borderRadius: BorderRadius.circular(4)),
          child: Text(m.group(3)!, style: const TextStyle(fontFamily: 'monospace', color: AppTheme.purple, fontSize: 11)),
        )));
      } else if (m.group(4) != null) {
        spans.add(WidgetSpan(child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 2, vertical: 1),
          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
          decoration: BoxDecoration(
            color: AppTheme.accent2.withOpacity(0.12),
            border: Border.all(color: AppTheme.accent2.withOpacity(0.3)),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text('[Source: ${m.group(4)}]', style: const TextStyle(color: AppTheme.purple, fontSize: 11)),
        )));
      }
      last = m.end;
    }
    if (last < line.length) spans.add(TextSpan(text: line.substring(last)));
    return SelectableText.rich(
      TextSpan(children: spans, style: const TextStyle(color: AppTheme.textPrimary, fontSize: 13.5, height: 1.7)),
    );
  }
}

