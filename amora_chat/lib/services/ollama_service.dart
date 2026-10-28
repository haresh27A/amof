// services/ollama_service.dart
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class OllamaService {
  final String baseUrl;

  OllamaService({this.baseUrl = 'http://localhost:11434'});

  /// Fetch all model names from Ollama daemon
  Future<List<String>> listModels() async {
    try {
      final resp = await http
          .get(Uri.parse('$baseUrl/api/tags'))
          .timeout(const Duration(seconds: 5));
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        final models = (data['models'] as List? ?? []);
        final names = models.map((m) => m['name'] as String).toList();
        // Sort: qwen first
        names.sort((a, b) {
          final aq = a.toLowerCase().contains('qwen');
          final bq = b.toLowerCase().contains('qwen');
          if (aq && !bq) return -1;
          if (!aq && bq) return 1;
          return a.compareTo(b);
        });
        return names;
      }
    } catch (_) {}
    return [];
  }

  /// Check if Ollama is reachable
  Future<bool> isAvailable() async {
    try {
      final resp = await http
          .get(Uri.parse('$baseUrl/api/tags'))
          .timeout(const Duration(seconds: 3));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Stream chat response from Ollama, yielding token chunks
  Stream<String> streamChat({
    required String model,
    required List<Map<String, String>> messages,
    double temperature = 0.7,
  }) async* {
    final request = http.Request('POST', Uri.parse('$baseUrl/api/chat'));
    request.headers['Content-Type'] = 'application/json';
    request.body = jsonEncode({
      'model': model,
      'messages': messages,
      'stream': true,
      'options': {'temperature': temperature},
    });

    final client = http.Client();
    try {
      final response = await client.send(request).timeout(const Duration(seconds: 180));
      await for (final chunk in response.stream.transform(utf8.decoder)) {
        for (final line in chunk.split('\n')) {
          if (line.trim().isEmpty) continue;
          try {
            final obj = jsonDecode(line);
            final delta = obj['message']?['content'] as String? ?? '';
            if (delta.isNotEmpty) yield delta;
            if (obj['done'] == true) return;
          } catch (_) {}
        }
      }
    } finally {
      client.close();
    }
  }

  /// Non-streaming chat
  Future<String> chat({
    required String model,
    required List<Map<String, String>> messages,
    double temperature = 0.7,
  }) async {
    final resp = await http
        .post(
          Uri.parse('$baseUrl/api/chat'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'model': model,
            'messages': messages,
            'stream': false,
            'options': {'temperature': temperature},
          }),
        )
        .timeout(const Duration(seconds: 120));
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      return data['message']?['content'] as String? ?? '';
    }
    throw Exception('Ollama returned ${resp.statusCode}');
  }
}
