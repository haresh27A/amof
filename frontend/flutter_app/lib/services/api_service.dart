// AMOF API Service — all HTTP calls to FastAPI backend
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiService {
  // Configurable at build time, e.g.
  //   flutter build web --dart-define=API_BASE_URL=http://10.0.2.2:8000
  // Defaults suit the web build served by FastAPI itself.
  static const String _compiledBaseUrl =
      String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000');

  static String baseUrl = _compiledBaseUrl;

  static Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // ── Health check ────────────────────────────────────────────
  static Future<Map<String, dynamic>> getHealth() async {
    final res = await http.get(Uri.parse('$baseUrl/'), headers: _headers)
        .timeout(const Duration(seconds: 5));
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Backend offline');
  }

  // ── Local LLM status ────────────────────────────────────────
  /// Confirms the local Ollama model is reachable and pulled, so the UI can warn
  /// before a query silently degrades to a canned stub.
  static Future<Map<String, dynamic>> getLlmStatus() async {
    final res = await http.get(Uri.parse('$baseUrl/llm/status'), headers: _headers)
        .timeout(const Duration(seconds: 8));
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('LLM status unavailable: ${res.statusCode}');
  }

  // ── AMORA Query Pipeline ────────────────────────────────────
  static Future<QueryResponse> query({
    required String query,
    String mode = 'weighted',
    int topK = 5,
    bool costSensitive = false,
    bool conflictSensitive = false,
    bool? forcedRetrieval,
    String? provider,
  }) async {
    final body = jsonEncode({
      'query': query,
      'mode': mode,
      'top_k': topK,
      'cost_sensitive': costSensitive,
      'conflict_sensitive': conflictSensitive,
      if (forcedRetrieval != null) 'forced_retrieval': forcedRetrieval,
      if (provider != null && provider.isNotEmpty) 'provider': provider,
    });
    final res = await http.post(
      Uri.parse('$baseUrl/query'),
      headers: _headers,
      body: body,
    ).timeout(const Duration(seconds: 900));
    if (res.statusCode == 200) return QueryResponse.fromJson(jsonDecode(res.body));
    throw Exception('Query failed: ${res.statusCode} — ${res.body}');
  }

  // ── Streaming query (SSE) ────────────────────────────────────
  /// Runs the same AMORA pipeline but consumes Server-Sent Events so answer tokens
  /// render as they arrive. A local reasoning model can take minutes, so this avoids
  /// leaving the user staring at a spinner with no feedback.
  ///
  /// [onDelta] receives each text fragment; [onRetrieval] receives the routed source
  /// and evidence payload as soon as retrieval finishes, before generation starts.
  /// Completes with the final [QueryResponse].
  static Future<QueryResponse> queryStream({
    required String query,
    required void Function(String text) onDelta,
    void Function(Map<String, dynamic> retrieval)? onRetrieval,
    String mode = 'weighted',
    int topK = 5,
    bool costSensitive = false,
    bool conflictSensitive = false,
    bool? forcedRetrieval,
    String? provider,
    Duration timeout = const Duration(minutes: 15),
  }) async {
    final body = jsonEncode({
      'query': query,
      'mode': mode,
      'top_k': topK,
      'cost_sensitive': costSensitive,
      'conflict_sensitive': conflictSensitive,
      if (forcedRetrieval != null) 'forced_retrieval': forcedRetrieval,
      if (provider != null && provider.isNotEmpty) 'provider': provider,
    });

    final request = http.Request('POST', Uri.parse('$baseUrl/query/stream'))
      ..headers.addAll({
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      })
      ..body = body;

    final response = await http.Client()
        .send(request)
        .timeout(const Duration(seconds: 30));
    if (response.statusCode != 200) {
      throw Exception('Stream failed: ${response.statusCode}');
    }

    String? event;
    Map<String, dynamic>? finalPayload;
    final deadline = DateTime.now().add(timeout);

    // SSE frames are separated by a blank line; each carries `event:` and `data:`.
    await for (final line
        in response.stream.transform(utf8.decoder).transform(const LineSplitter())) {
      if (DateTime.now().isAfter(deadline)) {
        throw Exception('Stream timed out after ${timeout.inMinutes} min');
      }
      final trimmed = line.trim();
      if (trimmed.isEmpty) continue;
      if (trimmed.startsWith('event:')) {
        event = trimmed.substring(6).trim();
      } else if (trimmed.startsWith('data:')) {
        final decoded = jsonDecode(trimmed.substring(5).trim());
        if (event == 'retrieval') {
          onRetrieval?.call(Map<String, dynamic>.from(decoded));
        } else if (event == 'delta') {
          onDelta((decoded['text'] ?? '').toString());
        } else if (event == 'done') {
          finalPayload = Map<String, dynamic>.from(decoded);
        } else if (event == 'error') {
          throw Exception('Stream error: ${decoded['detail']}');
        }
      }
    }

    if (finalPayload == null) {
      throw Exception('Stream ended without a final result');
    }
    return QueryResponse.fromJson(finalPayload);
  }

  static Future<QueryResponse> queryWithProvider({
    required String query,
    required String provider,
    String mode = 'weighted',
    int topK = 5,
    bool costSensitive = false,
    bool conflictSensitive = false,
  }) => ApiService.query(
    query: query,
    provider: provider,
    mode: mode,
    topK: topK,
    costSensitive: costSensitive,
    conflictSensitive: conflictSensitive,
  );

  // ── Free LLM Chat ───────────────────────────────────────────
  static Future<FreeChatResponse> freeChat({
    required String question,
    required String provider,
    String evidenceContext = '',
  }) async {
    final body = jsonEncode({
      'question': question,
      'provider': provider,
      'evidence_context': evidenceContext,
    });
    final res = await http.post(
      Uri.parse('$baseUrl/llm/chat'),
      headers: _headers,
      body: body,
    ).timeout(const Duration(seconds: 300));
    if (res.statusCode == 200) return FreeChatResponse.fromJson(jsonDecode(res.body));
    throw Exception('Free chat failed: ${res.statusCode}');
  }

  // ── Provider Status ─────────────────────────────────────────
  static Future<Map<String, dynamic>> getProviders() async {
    final res = await http.get(Uri.parse('$baseUrl/llm/providers'), headers: _headers)
        .timeout(const Duration(seconds: 5));
    if (res.statusCode == 200) return jsonDecode(res.body);
    return {'active_provider': 'groq', 'providers': {}};
  }

  // ── Sources ─────────────────────────────────────────────────
  static Future<List<Source>> getSources() async {
    final res = await http.get(Uri.parse('$baseUrl/sources'), headers: _headers)
        .timeout(const Duration(seconds: 10));
    if (res.statusCode == 200) {
      final List data = jsonDecode(res.body);
      return data.map((s) => Source.fromJson(s)).toList();
    }
    throw Exception('Failed to fetch sources');
  }

  static Future<Map<String, dynamic>> registerSource(Map<String, dynamic> payload) async {
    final res = await http.post(
      Uri.parse('$baseUrl/sources/register'),
      headers: _headers,
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 10));
    if (res.statusCode == 201) return jsonDecode(res.body);
    throw Exception('Register failed: ${res.body}');
  }

  // ── Benchmark ────────────────────────────────────────────────
  static Future<Map<String, dynamic>> runBenchmark() async {
    final res = await http.post(
      Uri.parse('$baseUrl/evaluation/run'),
      headers: _headers,
    ).timeout(const Duration(seconds: 120));
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('Benchmark failed: ${res.body}');
  }
}
