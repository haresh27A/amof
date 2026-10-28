// widgets/sidebar.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../theme/app_theme.dart';

class AppSidebar extends StatelessWidget {
  const AppSidebar({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.watch<ChatProvider>();
    return Container(
      width: 260,
      decoration: const BoxDecoration(
        color: AppTheme.bg2,
        border: Border(right: BorderSide(color: AppTheme.border)),
      ),
      child: Column(
        children: [
          _Brand(),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _ModelSelector(provider: p),
                  const _Divider(),
                  _ModeSelector(provider: p),
                  const _Divider(),
                  _AmoraControls(provider: p),
                  const _Divider(),
                  _Constraints(provider: p),
                  const _Divider(),
                  _SessionStats(provider: p),
                ],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: _ClearButton(provider: p),
          ),
        ],
      ),
    );
  }
}

// ── Brand ─────────────────────────────────────────────────────────────────────
class _Brand extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 16),
        decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: AppTheme.border))),
        child: Row(children: [
          Container(
            width: 38, height: 38,
            decoration: BoxDecoration(
              gradient: AppTheme.gradient,
              borderRadius: BorderRadius.circular(10),
              boxShadow: [BoxShadow(color: AppTheme.accent.withOpacity(0.4), blurRadius: 14)],
            ),
            child: const Center(child: Text('A', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18))),
          ),
          const SizedBox(width: 10),
          const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('AMOF', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16, color: AppTheme.textPrimary)),
            Text('Adaptive Multi-Objective Framework', style: TextStyle(fontSize: 10, color: AppTheme.textMuted)),
          ]),
        ]),
      );
}

// ── Model selector ────────────────────────────────────────────────────────────
class _ModelSelector extends StatelessWidget {
  final ChatProvider provider;
  const _ModelSelector({required this.provider});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 4),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _Label('Language Model'),
          const SizedBox(height: 6),
          // Status row
          Row(children: [
            _StatusDot(online: provider.ollamaOnline),
            const SizedBox(width: 7),
            Text(
              provider.ollamaOnline
                  ? 'Ollama online · ${provider.availableModels.length} models'
                  : 'Ollama offline',
              style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
            ),
            const Spacer(),
            _StatusDot(online: provider.backendOnline),
            const SizedBox(width: 5),
            Text(provider.backendOnline ? 'Backend ✓' : 'Backend ✗',
                style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
          ]),
          const SizedBox(height: 8),
          // Model dropdown
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: AppTheme.bg3, borderRadius: BorderRadius.circular(10),
              border: Border.all(color: AppTheme.border),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                isExpanded: true,
                value: provider.selectedModel.isEmpty ? null : provider.selectedModel,
                dropdownColor: AppTheme.bg3,
                style: const TextStyle(color: AppTheme.textPrimary, fontSize: 13),
                hint: const Text('Select model…', style: TextStyle(color: AppTheme.textDim)),
                icon: const Icon(Icons.keyboard_arrow_down, color: AppTheme.textMuted, size: 18),
                items: provider.availableModels.map((m) => DropdownMenuItem(
                  value: m,
                  child: Text(m, overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: AppTheme.textPrimary, fontSize: 13)),
                )).toList(),
                onChanged: (v) { if (v != null) provider.setModel(v); },
              ),
            ),
          ),
        ]),
      );
}

// ── Mode selector ─────────────────────────────────────────────────────────────
class _ModeSelector extends StatelessWidget {
  final ChatProvider provider;
  const _ModeSelector({required this.provider});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 4),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _Label('Query Mode'),
          const SizedBox(height: 8),
          _ModeButton(
            icon: '🤖', label: 'LLM with AMOF',
            sublabel: 'RAG-routed external knowledge',
            active: provider.appMode == AppMode.withAmora,
            color: AppTheme.accent2,
            onTap: () => provider.setAppMode(AppMode.withAmora),
          ),
          const SizedBox(height: 6),
          _ModeButton(
            icon: '⚡', label: 'LLM without AMOF',
            sublabel: 'Pure model baseline, no routing',
            active: provider.appMode == AppMode.directLlm,
            color: AppTheme.orange,
            onTap: () => provider.setAppMode(AppMode.directLlm),
          ),
          const SizedBox(height: 6),
          _ModeButton(
            icon: '⚖️', label: 'Compare Both',
            sublabel: 'Side-by-side with vs without AMOF',
            active: provider.appMode == AppMode.compare,
            color: AppTheme.green,
            onTap: () => provider.setAppMode(AppMode.compare),
          ),
        ]),
      );
}

class _ModeButton extends StatelessWidget {
  final String icon, label, sublabel;
  final bool active;
  final Color color;
  final VoidCallback onTap;
  const _ModeButton({required this.icon, required this.label, required this.sublabel,
      required this.active, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          decoration: BoxDecoration(
            color: active ? color.withOpacity(0.12) : AppTheme.bg3,
            border: Border.all(color: active ? color : AppTheme.border, width: active ? 1.5 : 1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(children: [
            Text(icon, style: const TextStyle(fontSize: 18)),
            const SizedBox(width: 10),
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600,
                  color: active ? color : AppTheme.textPrimary)),
              Text(sublabel, style: const TextStyle(fontSize: 10, color: AppTheme.textMuted)),
            ]),
            if (active) ...[const Spacer(), Icon(Icons.check_circle, color: color, size: 16)],
          ]),
        ),
      );
}

// ── AMOF controls ────────────────────────────────────────────────────────────
class _AmoraControls extends StatelessWidget {
  final ChatProvider provider;
  const _AmoraControls({required this.provider});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 4),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _Label('AMOF Routing'),
          const SizedBox(height: 8),
          Row(children: [
            _ToggleChip('Weighted', provider.rankingMode == 'weighted',
                () => provider.setRankingMode('weighted')),
            const SizedBox(width: 6),
            _ToggleChip('Pareto', provider.rankingMode == 'pareto',
                () => provider.setRankingMode('pareto')),
          ]),
          const SizedBox(height: 12),
          _Slider(label: 'Top-K Sources', value: provider.topK.toDouble(), min: 1, max: 10,
              divisions: 9, display: '${provider.topK}',
              onChanged: (v) => provider.setTopK(v.round())),
          const SizedBox(height: 8),
          _Slider(label: 'Temperature', value: provider.temperature, min: 0, max: 1,
              display: provider.temperature.toStringAsFixed(2),
              onChanged: (v) => provider.setTemperature(v)),
        ]),
      );
}

// ── Constraints ───────────────────────────────────────────────────────────────
class _Constraints extends StatelessWidget {
  final ChatProvider provider;
  const _Constraints({required this.provider});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 4),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _Label('Query Constraints'),
          const SizedBox(height: 4),
          _Check('Cost-Sensitive', provider.costSensitive,
              (v) => provider.setCostSensitive(v!)),
          _Check('Conflict-Sensitive', provider.conflictSensitive,
              (v) => provider.setConflictSensitive(v!)),
          _Check('Force Retrieval', provider.forceRetrieval,
              (v) => provider.setForceRetrieval(v!)),
          _Check('Stream Response', provider.streamEnabled,
              (v) => provider.setStreamEnabled(v!)),
        ]),
      );
}

// ── Session stats ─────────────────────────────────────────────────────────────
class _SessionStats extends StatelessWidget {
  final ChatProvider provider;
  const _SessionStats({required this.provider});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 4),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _Label('Session'),
          const SizedBox(height: 8),
          Row(children: [
            _StatCard('Queries', '${provider.totalQueries}'),
            const SizedBox(width: 6),
            _StatCard('Tokens', '${provider.totalTokens}'),
            const SizedBox(width: 6),
            _StatCard('Avg ms', provider.totalQueries > 0
                ? (provider.totalLatency / provider.totalQueries).toStringAsFixed(0)
                : '—'),
          ]),
        ]),
      );
}

class _ClearButton extends StatelessWidget {
  final ChatProvider provider;
  const _ClearButton({required this.provider});
  @override
  Widget build(BuildContext context) => SizedBox(
        width: double.infinity,
        child: OutlinedButton.icon(
          icon: const Icon(Icons.delete_outline, size: 16),
          label: const Text('Clear Chat'),
          style: OutlinedButton.styleFrom(
            foregroundColor: AppTheme.red,
            side: const BorderSide(color: AppTheme.red, width: 0.8),
            padding: const EdgeInsets.symmetric(vertical: 10),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          onPressed: () => provider.clearChat(),
        ),
      );
}

// ── Reusable small widgets ────────────────────────────────────────────────────
class _Label extends StatelessWidget {
  final String text;
  const _Label(this.text);
  @override
  Widget build(BuildContext context) => Text(text.toUpperCase(),
      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700,
          color: AppTheme.textMuted, letterSpacing: 0.8));
}

class _Divider extends StatelessWidget {
  const _Divider();
  @override
  Widget build(BuildContext context) => const Padding(
        padding: EdgeInsets.symmetric(horizontal: 14),
        child: Divider(color: AppTheme.border, height: 1),
      );
}

class _StatusDot extends StatelessWidget {
  final bool online;
  const _StatusDot({required this.online});
  @override
  Widget build(BuildContext context) => Container(
        width: 8, height: 8,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: online ? AppTheme.green : AppTheme.red,
          boxShadow: [BoxShadow(color: (online ? AppTheme.green : AppTheme.red).withOpacity(0.5), blurRadius: 5)],
        ),
      );
}

class _ToggleChip extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;
  const _ToggleChip(this.label, this.active, this.onTap);
  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          decoration: BoxDecoration(
            color: active ? AppTheme.accent2.withOpacity(0.2) : AppTheme.bg3,
            border: Border.all(color: active ? AppTheme.accent2 : AppTheme.border),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(label,
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500,
                  color: active ? AppTheme.purple : AppTheme.textMuted)),
        ),
      );
}

class _Slider extends StatelessWidget {
  final String label, display;
  final double value, min, max;
  final int? divisions;
  final ValueChanged<double> onChanged;
  const _Slider({required this.label, required this.value, required this.min,
      required this.max, required this.display, required this.onChanged, this.divisions});
  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
          const Spacer(),
          Text(display, style: const TextStyle(fontSize: 12, color: AppTheme.accent2, fontWeight: FontWeight.w600)),
        ]),
        Slider(value: value, min: min, max: max, divisions: divisions, onChanged: onChanged),
      ]);
}

class _Check extends StatelessWidget {
  final String label;
  final bool value;
  final ValueChanged<bool?> onChanged;
  const _Check(this.label, this.value, this.onChanged);
  @override
  Widget build(BuildContext context) => CheckboxListTile(
        title: Text(label, style: const TextStyle(fontSize: 13, color: AppTheme.textMuted)),
        value: value, onChanged: onChanged,
        activeColor: AppTheme.accent2,
        checkColor: Colors.white,
        contentPadding: EdgeInsets.zero,
        dense: true,
        controlAffinity: ListTileControlAffinity.leading,
      );
}

class _StatCard extends StatelessWidget {
  final String label, value;
  const _StatCard(this.label, this.value);
  @override
  Widget build(BuildContext context) => Expanded(
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: AppTheme.bg3, borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppTheme.border),
          ),
          child: Column(children: [
            Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.purple)),
            Text(label, style: const TextStyle(fontSize: 10, color: AppTheme.textMuted)),
          ]),
        ),
      );
}
