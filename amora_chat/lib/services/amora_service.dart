// services/amora_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/amora_pipeline.dart';

class AmoraQueryResult {
  final AmoraPipeline pipeline;
  final String finalAnswer;
  final String evidenceContext;

  AmoraQueryResult({
    required this.pipeline,
    required this.finalAnswer,
    required this.evidenceContext,
  });
}

class AmoraService {
  final String baseUrl;

  AmoraService({this.baseUrl = 'http://localhost:8000'});

  Future<bool> isAvailable() async {
    try {
      final resp = await http
          .get(Uri.parse('$baseUrl/'))
          .timeout(const Duration(seconds: 3));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Run full AMOF routing pipeline and return pipeline data + real evidence context
  Future<AmoraQueryResult> route({
    required String query,
    String mode = 'weighted',
    int topK = 5,
    bool costSensitive = false,
    bool conflictSensitive = false,
    bool? forcedRetrieval,
  }) async {
    final resp = await http
        .post(
          Uri.parse('$baseUrl/amof/retrieve'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'query': query,
            'mode': mode,
            'top_k': topK,
            'cost_sensitive': costSensitive,
            'conflict_sensitive': conflictSensitive,
            if (forcedRetrieval != null) 'forced_retrieval': forcedRetrieval,
          }),
        )
        .timeout(const Duration(seconds: 30));

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      final pipeline = AmoraPipeline.fromJson(data);

      // Extract real evidence context from backend fusion engine
      String evidenceCtx = (data['evidence_context'] as String? ?? '').trim();
      
      // If empty, construct structured reference context from selected sources
      if (evidenceCtx.isEmpty && pipeline.selectedSources.isNotEmpty) {
        evidenceCtx = pipeline.selectedSources
            .asMap()
            .entries
            .map((e) =>
                '[Source ${e.key + 1}: ${e.value.name}]\n'
                'Tool: ${e.value.tool} | Score: ${e.value.score.toStringAsFixed(4)} '
                '| DST Belief: ${e.value.dstBelief.toStringAsFixed(4)} '
                '| Reliability: ${e.value.reliability.toStringAsFixed(3)}')
            .join('\n\n');
      }

      return AmoraQueryResult(
        pipeline: pipeline,
        finalAnswer: data['final_answer'] as String? ?? '',
        evidenceContext: evidenceCtx,
      );
    }
    throw Exception('AMOF backend returned ${resp.statusCode}: ${resp.body}');
  }

  /// Fetch registered sources
  Future<List<Map<String, dynamic>>> listSources() async {
    final resp = await http
        .get(Uri.parse('$baseUrl/sources'))
        .timeout(const Duration(seconds: 10));
    if (resp.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(resp.body));
    }
    return [];
  }
}
