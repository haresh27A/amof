// Benchmark & Experiments Screen
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class BenchmarkScreen extends StatefulWidget {
  const BenchmarkScreen({super.key});
  @override
  State<BenchmarkScreen> createState() => _BenchmarkScreenState();
}

class _BenchmarkScreenState extends State<BenchmarkScreen> {
  bool _running = false;
  Map<String, dynamic>? _results;
  String? _error;

  Future<void> _run() async {
    setState(() { _running = true; _results = null; _error = null; });
    try {
      final data = await ApiService.runBenchmark();
      if (mounted) setState(() { _results = data['results']; });
    } catch (e) {
      if (mounted) setState(() { _error = '⚠️ $e\n\nMake sure the backend is running.'; });
    } finally {
      if (mounted) setState(() => _running = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('📊 AMORA Empirical Research Evaluation',
                style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
            const SizedBox(height: 4),
            Text('Run automated benchmark suites comparing 6 baselines, scalability tests (100→10,000 sources), and ablation matrices.',
                style: GoogleFonts.inter(fontSize: 13, color: AppTheme.textMuted)),
            const SizedBox(height: 20),
            // ── Run button ──────────────────────────────────
            SizedBox(
              width: 260,
              child: FilledButton.icon(
                icon: _running
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.science_outlined, size: 18),
                label: Text(_running ? 'Running Benchmark…' : '🔬 Run Full Benchmark Suite',
                    style: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14)),
                style: FilledButton.styleFrom(
                  backgroundColor: AppTheme.accent,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                onPressed: _running ? null : _run,
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(color: AppTheme.red.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(10), border: Border.all(color: AppTheme.red.withValues(alpha: 0.3))),
                child: Text(_error!, style: GoogleFonts.inter(color: AppTheme.red, fontSize: 13)),
              ),
            ],
            if (_results != null) ...[
              const SizedBox(height: 28),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: AppTheme.green.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(10), border: Border.all(color: AppTheme.green.withValues(alpha: 0.3))),
                child: Row(children: [
                  const Icon(Icons.check_circle, color: AppTheme.green, size: 18),
                  const SizedBox(width: 8),
                  Text('✅ Benchmark Execution Complete!', style: GoogleFonts.inter(color: AppTheme.green, fontWeight: FontWeight.w600)),
                ]),
              ),
              const SizedBox(height: 24),
              // ── 1. Baselines ──────────────────────────────
              const _SectionTitle('1. Comparative Baselines Summary'),
              const SizedBox(height: 10),
              _BaselinesTable(data: _results!['baselines_summary'] as Map<String, dynamic>? ?? {}),
              const SizedBox(height: 28),
              // ── 2. Scalability chart ──────────────────────
              const _SectionTitle('2. Source Scalability Experiment (100 → 10,000 Catalog)'),
              const SizedBox(height: 10),
              _ScalabilityChart(data: List<Map<String, dynamic>>.from(_results!['scalability_experiment'] ?? [])),
              const SizedBox(height: 28),
              // ── 3. Ablation ───────────────────────────────
              const _SectionTitle('3. AMORA Ablation Matrix'),
              const SizedBox(height: 10),
              _AblationTable(data: _results!['ablation_study'] as Map<String, dynamic>? ?? {}),
            ],
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String text;
  const _SectionTitle(this.text);
  @override
  Widget build(BuildContext context) => Text(text,
    style: GoogleFonts.inter(fontSize: 15, fontWeight: FontWeight.w700, color: AppTheme.textPrimary));
}

class _BaselinesTable extends StatelessWidget {
  final Map<String, dynamic> data;
  const _BaselinesTable({required this.data});

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) return Text('No data', style: GoogleFonts.inter(color: AppTheme.textMuted));
    final keys = data.keys.toList();
    final metricKeys = (data[keys.first] as Map<String, dynamic>? ?? {}).keys.toList();
    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingTextStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
          dataTextStyle: GoogleFonts.inter(fontSize: 12, color: AppTheme.textPrimary),
          headingRowColor: WidgetStateProperty.all(AppTheme.bg),
          columns: [const DataColumn(label: Text('Baseline')), ...metricKeys.map((k) => DataColumn(label: Text(k)))],
          rows: keys.map((name) {
            final row = data[name] as Map<String, dynamic>? ?? {};
            return DataRow(cells: [
              DataCell(Text(name, style: GoogleFonts.inter(fontWeight: FontWeight.w600))),
              ...metricKeys.map((k) => DataCell(Text('${row[k] ?? '-'}'))),
            ]);
          }).toList(),
        ),
      ),
    );
  }
}

class _ScalabilityChart extends StatelessWidget {
  final List<Map<String, dynamic>> data;
  const _ScalabilityChart({required this.data});

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) return Text('No data', style: GoogleFonts.inter(color: AppTheme.textMuted));
    final spots = data.asMap().entries.map((e) => FlSpot(
      (e.value['source_catalog_size'] as num).toDouble(),
      (e.value['routing_latency_ms'] as num).toDouble(),
    )).toList();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('AMORA Routing Latency vs Source Catalog Scale',
                style: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textSecond)),
            const SizedBox(height: 16),
            SizedBox(
              height: 220,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: true, getDrawingHorizontalLine: (_) => const FlLine(color: AppTheme.border, strokeWidth: 1), getDrawingVerticalLine: (_) => const FlLine(color: AppTheme.border, strokeWidth: 1)),
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 28, getTitlesWidget: (v, _) => Text('${v.toInt()}', style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted)))),
                    leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40, getTitlesWidget: (v, _) => Text('${v.toInt()}ms', style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textMuted)))),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      gradient: const LinearGradient(colors: [AppTheme.accent, AppTheme.accentPink]),
                      barWidth: 3,
                      dotData: FlDotData(getDotPainter: (_, __, ___, ____) => FlDotCirclePainter(radius: 4, color: AppTheme.accent, strokeWidth: 0)),
                      belowBarData: BarAreaData(show: true, gradient: LinearGradient(colors: [AppTheme.accent.withValues(alpha: 0.15), AppTheme.accent.withValues(alpha: 0)], begin: Alignment.topCenter, end: Alignment.bottomCenter)),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AblationTable extends StatelessWidget {
  final Map<String, dynamic> data;
  const _AblationTable({required this.data});

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) return Text('No data', style: GoogleFonts.inter(color: AppTheme.textMuted));
    final keys = data.keys.toList();
    final metricKeys = (data[keys.first] as Map<String, dynamic>? ?? {}).keys.toList();
    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingTextStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
          dataTextStyle: GoogleFonts.inter(fontSize: 12, color: AppTheme.textPrimary),
          headingRowColor: WidgetStateProperty.all(AppTheme.bg),
          columns: [const DataColumn(label: Text('Variant')), ...metricKeys.map((k) => DataColumn(label: Text(k)))],
          rows: keys.map((name) {
            final row = data[name] as Map<String, dynamic>? ?? {};
            return DataRow(cells: [
              DataCell(Text(name, style: GoogleFonts.inter(fontWeight: FontWeight.w600))),
              ...metricKeys.map((k) => DataCell(Text('${row[k] ?? '-'}'))),
            ]);
          }).toList(),
        ),
      ),
    );
  }
}
