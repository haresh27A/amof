// Reusable chat bubble widget
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

class UserBubble extends StatelessWidget {
  final String text;
  final LinearGradient gradient;
  const UserBubble({super.key, required this.text, this.gradient = AppTheme.userBubbleGrad});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 48, bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                gradient: gradient,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(18),
                  topRight: Radius.circular(18),
                  bottomLeft: Radius.circular(18),
                  bottomRight: Radius.circular(4),
                ),
                boxShadow: [BoxShadow(color: AppTheme.accent.withValues(alpha: 0.25), blurRadius: 12, offset: const Offset(0, 4))],
              ),
              child: Text(text, style: GoogleFonts.inter(color: Colors.white, fontSize: 14, height: 1.6)),
            ),
          ),
        ],
      ),
    );
  }
}

class AssistantBubble extends StatelessWidget {
  final String text;
  final String avatarLabel;
  final Color avatarColor;
  final Widget? footer;

  const AssistantBubble({
    super.key,
    required this.text,
    this.avatarLabel = 'Q',
    this.avatarColor = AppTheme.accent,
    this.footer,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 48, bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Avatar
          Container(
            width: 34, height: 34,
            decoration: const BoxDecoration(
              gradient: AppTheme.accentGrad,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(avatarLabel, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 13)),
            ),
          ),
          const SizedBox(width: 10),
          // Bubble
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.bgCard,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(4),
                  topRight: Radius.circular(18),
                  bottomLeft: Radius.circular(18),
                  bottomRight: Radius.circular(18),
                ),
                border: Border.all(color: AppTheme.border),
                boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 8)],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SelectableText(
                    text,
                    style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14, height: 1.7),
                  ),
                  if (footer != null) ...[
                    const SizedBox(height: 10),
                    const Divider(color: AppTheme.border, height: 1),
                    const SizedBox(height: 8),
                    footer!,
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

class MetaChip extends StatelessWidget {
  final String label;
  final Color color;
  final Color bg;
  const MetaChip({super.key, required this.label, this.color = AppTheme.accentLight, this.bg = const Color(0x1A6366F1)});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: color.withValues(alpha: 0.3)),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(label, style: GoogleFonts.inter(fontSize: 11, color: color, fontWeight: FontWeight.w500)),
    );
  }
}

class PipelineMetaRow extends StatelessWidget {
  final String provider;
  final bool retrieval;
  final double latencyMs;
  final int nSources;
  final int tokens;
  final double srr;
  final double accuracyScore;
  final bool usedStub;
  final String llmNote;

  const PipelineMetaRow({
    super.key,
    required this.provider,
    required this.retrieval,
    required this.latencyMs,
    required this.nSources,
    required this.tokens,
    required this.srr,
    this.accuracyScore = 0.95,
    this.usedStub = false,
    this.llmNote = '',
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 6, runSpacing: 6,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        MetaChip(label: provider),
        // A stub answer was produced by a fixed template, not a model, so it must be
        // flagged rather than presented as a grounded LLM response.
        if (usedStub)
          MetaChip(
            label: '⚠ STUB RESPONSE — no LLM ran',
            color: AppTheme.orange,
            bg: const Color(0x1AF97316),
          )
        else
          MetaChip(
            label: '🎯 ${(accuracyScore * 100).toStringAsFixed(0)}% Grounding',
            color: AppTheme.green,
            bg: const Color(0x1A22C55E),
          ),
        MetaChip(
          label: retrieval ? 'Retrieval: YES' : 'Retrieval: NO',
          color: retrieval ? AppTheme.green : AppTheme.orange,
          bg: retrieval ? const Color(0x1A22C55E) : const Color(0x1AF97316),
        ),
        MetaChip(label: '⏱ ${latencyMs.toStringAsFixed(0)} ms'),
        MetaChip(label: '🗂 $nSources sources'),
        MetaChip(label: '🪙 $tokens tokens'),
        MetaChip(label: 'SRR ${srr.toStringAsFixed(4)}'),
        if (llmNote.isNotEmpty)
          MetaChip(
            label: 'ℹ ${llmNote.length > 80 ? '${llmNote.substring(0, 80)}…' : llmNote}',
            color: AppTheme.orange,
            bg: const Color(0x1AF97316),
          ),
      ],
    );
  }
}

class FreeMetaRow extends StatelessWidget {
  final String provider;
  final double latencyMs;
  final int tokens;
  final double accuracyScore;

  const FreeMetaRow({
    super.key,
    required this.provider,
    required this.latencyMs,
    required this.tokens,
    this.accuracyScore = 0.20,
  });

  @override
  Widget build(BuildContext context) {
    final bool highAcc = accuracyScore >= 0.70;
    return Wrap(
      spacing: 6, runSpacing: 6,
      children: [
        MetaChip(label: '🤖 $provider', color: AppTheme.freeGreenL, bg: const Color(0x1A10B981)),
        MetaChip(
          label: '🎯 ${(accuracyScore * 100).toStringAsFixed(0)}% Accuracy',
          color: highAcc ? AppTheme.green : AppTheme.orange,
          bg: highAcc ? const Color(0x1A22C55E) : const Color(0x1AF97316),
        ),
        MetaChip(label: '⏱ ${latencyMs.toStringAsFixed(0)} ms', color: AppTheme.freeGreenL, bg: const Color(0x1A10B981)),
        MetaChip(label: '🪙 $tokens tokens', color: AppTheme.freeGreenL, bg: const Color(0x1A10B981)),
      ],
    );
  }
}
