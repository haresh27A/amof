// Sources Management Screen
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class SourcesScreen extends StatefulWidget {
  const SourcesScreen({super.key});
  @override
  State<SourcesScreen> createState() => _SourcesScreenState();
}

class _SourcesScreenState extends State<SourcesScreen> {
  List<Source> _sources = [];
  bool _loading = false;
  bool _registering = false;
  String? _regSuccess;
  String? _regError;

  final _idCtrl      = TextEditingController(text: 'src_custom_01');
  final _nameCtrl    = TextEditingController(text: 'Custom HR Analytics SQL Database');
  final _domainCtrl  = TextEditingController(text: 'hr_analytics');
  final _descCtrl    = TextEditingController(text: 'Relational table containing employee roles, salary grades, and performance scores.');
  final _schemaCtrl  = TextEditingController(text: 'sqlite:///./demo_hr.db');
  String _sourceType = 'SQL Database';
  double _reliability = 0.95;
  double _cost = 0.05;

  @override
  void initState() {
    super.initState();
    _fetchSources();
  }

  Future<void> _fetchSources() async {
    setState(() => _loading = true);
    try {
      final list = await ApiService.getSources();
      if (mounted) setState(() { _sources = list; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _register() async {
    setState(() { _registering = true; _regSuccess = null; _regError = null; });
    try {
      await ApiService.registerSource({
        'source_id': _idCtrl.text,
        'name': _nameCtrl.text,
        'source_type': _sourceType,
        'domain': _domainCtrl.text,
        'description': _descCtrl.text,
        'endpoint_or_schema': _schemaCtrl.text,
        'reliability': _reliability,
        'cost': _cost,
      });
      setState(() { _regSuccess = '✅ Source "${_nameCtrl.text}" registered successfully!'; });
      _fetchSources();
    } catch (e) {
      setState(() { _regError = '⚠️ $e'; });
    } finally {
      if (mounted) setState(() => _registering = false);
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
            _sectionTitle('📂 Offline Source Metadata Registration'),
            Text('Register heterogeneous sources (SQL, REST API, PDF, FAISS/Vector, Web) for AMORA pre-filtering and ranking.',
                style: GoogleFonts.inter(fontSize: 13, color: AppTheme.textMuted)),
            const SizedBox(height: 20),
            // ── Registration form ────────────────────────────
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _fieldLabel('Source ID'),
                    _textField(_idCtrl, 'src_custom_01'),
                    const SizedBox(height: 12),
                    _fieldLabel('Source Name'),
                    _textField(_nameCtrl, 'My Data Source'),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _fieldLabel('Source Type'),
                            DropdownButtonFormField<String>(
                              initialValue: _sourceType,
                              dropdownColor: AppTheme.bgCard,
                              style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14),
                              decoration: InputDecoration(contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: AppTheme.border)),
                                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: AppTheme.border)),
                              ),
                              items: ['SQL Database', 'REST API', 'PDF Document', 'Vector DB', 'Web Source']
                                  .map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                              onChanged: (v) => setState(() => _sourceType = v!),
                            ),
                          ],
                        )),
                        const SizedBox(width: 12),
                        Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _fieldLabel('Domain'),
                            _textField(_domainCtrl, 'hr_analytics'),
                          ],
                        )),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _fieldLabel('Description'),
                    TextField(
                      controller: _descCtrl, maxLines: 3,
                      style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14),
                      decoration: InputDecoration(hintText: 'Describe this source…', border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)), enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: AppTheme.border))),
                    ),
                    const SizedBox(height: 12),
                    _fieldLabel('Connection String / File Path / Endpoint'),
                    _textField(_schemaCtrl, 'sqlite:///./data.db'),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _fieldLabel('Initial Reliability: ${_reliability.toStringAsFixed(2)}'),
                            Slider(value: _reliability, min: 0, max: 1, divisions: 100, activeColor: AppTheme.accent, inactiveColor: AppTheme.border, onChanged: (v) => setState(() => _reliability = v)),
                          ],
                        )),
                        const SizedBox(width: 12),
                        Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _fieldLabel('Normalized Cost: ${_cost.toStringAsFixed(2)}'),
                            Slider(value: _cost, min: 0, max: 1, divisions: 100, activeColor: AppTheme.orange, inactiveColor: AppTheme.border, onChanged: (v) => setState(() => _cost = v)),
                          ],
                        )),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (_regSuccess != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(color: AppTheme.green.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8), border: Border.all(color: AppTheme.green.withValues(alpha: 0.3))),
                        child: Text(_regSuccess!, style: GoogleFonts.inter(color: AppTheme.green, fontSize: 13)),
                      ),
                    if (_regError != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(color: AppTheme.red.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8), border: Border.all(color: AppTheme.red.withValues(alpha: 0.3))),
                        child: Text(_regError!, style: GoogleFonts.inter(color: AppTheme.red, fontSize: 13)),
                      ),
                    if (_regSuccess != null || _regError != null) const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        icon: _registering ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.check_circle_outline, size: 18),
                        label: Text(_registering ? 'Registering…' : '✅ Register Source', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                        style: FilledButton.styleFrom(backgroundColor: AppTheme.accent, padding: const EdgeInsets.symmetric(vertical: 14)),
                        onPressed: _registering ? null : _register,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 28),
            Row(
              children: [
                _sectionTitle('📋 Registered Active Sources'),
                const Spacer(),
                IconButton(icon: const Icon(Icons.refresh, color: AppTheme.accent), onPressed: _fetchSources),
              ],
            ),
            const SizedBox(height: 8),
            if (_loading)
              const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator(color: AppTheme.accent)))
            else if (_sources.isEmpty)
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(color: AppTheme.bgCard, borderRadius: BorderRadius.circular(12), border: Border.all(color: AppTheme.border)),
                child: Center(child: Text('ℹ️ No sources yet — register one above or start the backend server.', style: GoogleFonts.inter(color: AppTheme.textMuted, fontSize: 13))),
              )
            else
              Card(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: DataTable(
                    headingTextStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
                    dataTextStyle: GoogleFonts.inter(fontSize: 13, color: AppTheme.textPrimary),
                    headingRowColor: WidgetStateProperty.all(AppTheme.bg),
                    columns: const [
                      DataColumn(label: Text('Name')),
                      DataColumn(label: Text('Type')),
                      DataColumn(label: Text('Domain')),
                      DataColumn(label: Text('Reliability')),
                      DataColumn(label: Text('Cost')),
                    ],
                    rows: _sources.map((s) => DataRow(cells: [
                      DataCell(Text(s.name)),
                      DataCell(Text(s.sourceType)),
                      DataCell(Text(s.domain)),
                      DataCell(Text(s.reliability.toStringAsFixed(2))),
                      DataCell(Text(s.cost.toStringAsFixed(2))),
                    ])).toList(),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String t) => Padding(
    padding: const EdgeInsets.only(bottom: 4),
    child: Text(t, style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
  );
  Widget _fieldLabel(String t) => Padding(
    padding: const EdgeInsets.only(bottom: 6),
    child: Text(t, style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textMuted, fontWeight: FontWeight.w500)),
  );
  Widget _textField(TextEditingController ctrl, String hint) => TextField(
    controller: ctrl,
    style: GoogleFonts.inter(color: AppTheme.textPrimary, fontSize: 14),
    decoration: InputDecoration(hintText: hint),
  );
}
