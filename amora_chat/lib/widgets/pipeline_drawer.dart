// widgets/pipeline_drawer.dart
import 'package:flutter/material.dart';
import '../models/amora_pipeline.dart';
import '../theme/app_theme.dart';

class PipelineDrawer {
  static void show(BuildContext context, AmoraPipeline pipeline) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _PipelineSheet(pipeline: pipeline),
    );
  }
}

class _PipelineSheet extends StatelessWidget {
  final AmoraPipeline pipeline;
  const _PipelineSheet({required this.pipeline});

  @override
  Widget build(BuildContext context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.4,
        maxChildSize: 0.95,
        builder: (_, ctrl) => Container(
          decoration: const BoxDecoration(
            color: AppTheme.bg2,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            border: Border(top: BorderSide(color: AppTheme.border)),
          ),
          child: Column(children: [
            // Handle bar
            Center(
              child: Container(
                margin: const EdgeInsets.symmetric(vertical: 10),
                width: 40, height: 4,
                decoration: BoxDecoration(
                  color: AppTheme.border, borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 10),
              child: Row(
                children: [
                  ShaderMask(
                    shaderCallback: (b) => AppTheme.gradient.createShader(b),
                    child: const Text('📊 AMOF Pipeline Details',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white)),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close, color: AppTheme.textMuted),
                    onPressed: () => Navigator.pop(context),
                  )
                ],
              ),
            ),
            const Divider(color: AppTheme.border, height: 1),
            // Body
            Expanded(
              child: ListView(
                controller: ctrl,
                padding: const EdgeInsets.all(20),
                children: [
                  _MetricGrid(pipeline: pipeline),
                  const SizedBox(height: 20),
                  if (pipeline.retrievalQuery.isNotEmpty) ...[
                    _SectionTitle('Formulated Retrieval Query  (INKER IE-KQF)'),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppTheme.bg3, borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppTheme.border),
                      ),
                      child: Text('q⁺ = ${pipeline.retrievalQuery}',
                          style: const TextStyle(fontFamily: 'monospace', color: AppTheme.purple, fontSize: 13)),
                    ),
                    const SizedBox(height: 20),
                  ],
                  if (pipeline.weights.isNotEmpty) ...[
                    _SectionTitle('Dynamic AMOF Weights  (Σ W = 1.0)'),
                    const SizedBox(height: 10),
                    _WeightsBars(weights: pipeline.weights),
                    const SizedBox(height: 20),
                  ],
                  if (pipeline.selectedSources.isNotEmpty) ...[
                    _SectionTitle('Selected Sources  (ranked by DST-Combined Score)'),
                    const SizedBox(height: 10),
                    _SourcesTable(sources: pipeline.selectedSources),
                  ],
                ],
              ),
            ),
          ]),
        ),
      );
}

// ── Metric grid ───────────────────────────────────────────────────────────────
class _MetricGrid extends StatelessWidget {
  final AmoraPipeline pipeline;
  const _MetricGrid({required this.pipeline});

  @override
  Widget build(BuildContext context) => GridView.count(
        crossAxisCount: 4, shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        childAspectRatio: 1.6,
        crossAxisSpacing: 10, mainAxisSpacing: 10,
        children: [
          _mCard('K-Score', pipeline.kActivationScore.toStringAsFixed(4)),
          _mCard('Total Sources', '${pipeline.totalCatalogSources}'),
          _mCard('Candidates', '${pipeline.candidateCount}'),
          _mCard('Selected', '${pipeline.selectedSources.length}'),
          _mCard('Latency', '${pipeline.latencyMs.toStringAsFixed(0)}ms'),
          _mCard('Efficiency', pipeline.amoraEfficiencyScore.toStringAsFixed(3)),
          _mCard('SRR', pipeline.sourceReductionRatio.toStringAsFixed(4)),
          _mCard('Evidence', '${pipeline.retrievedEvidenceCount}'),
        ],
      );

  Widget _mCard(String label, String value) => Container(
        decoration: BoxDecoration(
          color: AppTheme.bg3, borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppTheme.border),
        ),
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.purple)),
          const SizedBox(height: 2),
          Text(label, style: const TextStyle(fontSize: 10, color: AppTheme.textMuted), textAlign: TextAlign.center),
        ]),
      );
}

// ── Weights bars ──────────────────────────────────────────────────────────────
class _WeightsBars extends StatelessWidget {
  final Map<String, double> weights;
  const _WeightsBars({required this.weights});

  @override
  Widget build(BuildContext context) => Column(
        children: weights.entries.map((e) {
          final pct = e.value.clamp(0.0, 1.0);
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(children: [
              SizedBox(
                width: 110,
                child: Text(e.key, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                    textAlign: TextAlign.right),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: Stack(children: [
                    Container(height: 10, color: AppTheme.bg3),
                    FractionallySizedBox(
                      widthFactor: pct,
                      child: Container(
                        height: 10,
                        decoration: BoxDecoration(
                          gradient: AppTheme.gradient,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                  ]),
                ),
              ),
              const SizedBox(width: 10),
              SizedBox(
                width: 42,
                child: Text(e.value.toStringAsFixed(3),
                    style: const TextStyle(fontSize: 11, color: AppTheme.purple, fontFamily: 'monospace')),
              ),
            ]),
          );
        }).toList(),
      );
}

// ── Sources table ─────────────────────────────────────────────────────────────
class _SourcesTable extends StatelessWidget {
  final List<AmoraSource> sources;
  const _SourcesTable({required this.sources});

  @override
  Widget build(BuildContext context) => Container(
        decoration: BoxDecoration(
          border: Border.all(color: AppTheme.border),
          borderRadius: BorderRadius.circular(10),
        ),
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            headingRowColor: WidgetStatePropertyAll(AppTheme.bg3),
            dataRowColor: WidgetStatePropertyAll(AppTheme.bg2),
            dividerThickness: 1,
            border: TableBorder(
              horizontalInside: BorderSide(color: AppTheme.border.withOpacity(0.5), width: 0.5),
            ),
            columns: const [
              DataColumn(label: Text('Source', style: TextStyle(color: AppTheme.textMuted, fontSize: 11))),
              DataColumn(label: Text('Tool', style: TextStyle(color: AppTheme.textMuted, fontSize: 11))),
              DataColumn(label: Text('AMORA Score', style: TextStyle(color: AppTheme.textMuted, fontSize: 11))),
              DataColumn(label: Text('DST Belief', style: TextStyle(color: AppTheme.textMuted, fontSize: 11))),
              DataColumn(label: Text('DST Combined', style: TextStyle(color: AppTheme.textMuted, fontSize: 11))),
              DataColumn(label: Text('Reliability', style: TextStyle(color: AppTheme.textMuted, fontSize: 11))),
              DataColumn(label: Text('Relevance', style: TextStyle(color: AppTheme.textMuted, fontSize: 11))),
            ],
            rows: sources.map((s) => DataRow(cells: [
              DataCell(Text(s.name, style: const TextStyle(color: AppTheme.textPrimary, fontSize: 12))),
              DataCell(_toolBadge(s.tool)),
              DataCell(_scoreText(s.score)),
              DataCell(_scoreText(s.dstBelief, color: AppTheme.green)),
              DataCell(_scoreText(s.dstCombinedScore, color: AppTheme.purple)),
              DataCell(_scoreText(s.reliability)),
              DataCell(_scoreText(s.relevance)),
            ])).toList(),
          ),
        ),
      );

  Widget _scoreText(double v, {Color color = AppTheme.textPrimary}) => Text(
        v.toStringAsFixed(4),
        style: TextStyle(fontFamily: 'monospace', color: color, fontSize: 12),
      );

  Widget _toolBadge(String tool) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
        decoration: BoxDecoration(
          color: AppTheme.accent2.withOpacity(0.12),
          border: Border.all(color: AppTheme.accent2.withOpacity(0.3)),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(tool, style: const TextStyle(color: AppTheme.purple, fontSize: 11)),
      );
}

// ── Section title ─────────────────────────────────────────────────────────────
class _SectionTitle extends StatelessWidget {
  final String text;
  const _SectionTitle(this.text);
  @override
  Widget build(BuildContext context) => Text(
        text,
        style: const TextStyle(
          fontSize: 11, fontWeight: FontWeight.w700,
          color: AppTheme.textMuted, letterSpacing: 0.8,
        ),
      );
}
