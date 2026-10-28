// providers/chat_provider.dart
import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/chat_message.dart';
import '../models/amora_pipeline.dart';
import '../services/ollama_service.dart';
import '../services/amora_service.dart';

enum AppMode { withAmora, directLlm, compare }

class ChatProvider extends ChangeNotifier {
  final OllamaService _ollama = OllamaService();
  final AmoraService _amora = AmoraService();

  // ── Connection state ──────────────────────────────────────────
  bool ollamaOnline = false;
  bool backendOnline = false;
  List<String> availableModels = [];
  String selectedModel = '';

  // ── Settings ──────────────────────────────────────────────────
  AppMode appMode = AppMode.withAmora;
  String rankingMode = 'weighted';
  int topK = 5;
  double temperature = 0.7;
  bool costSensitive = false;
  bool conflictSensitive = false;
  bool forceRetrieval = false;
  bool streamEnabled = true;

  // ── Chat state ────────────────────────────────────────────────
  // Single mode messages
  List<ChatMessage> messages = [];
  // Compare mode messages (pairs)
  List<CompareMessage> compareMessages = [];

  bool isGenerating = false;

  // ── Session stats ─────────────────────────────────────────────
  int totalQueries = 0;
  int totalTokens = 0;
  double totalLatency = 0;

  ChatProvider() {
    _init();
  }

  Future<void> _init() async {
    await refreshConnections();
    // Periodic check every 15s
    Timer.periodic(const Duration(seconds: 15), (_) => refreshConnections());
  }

  Future<void> refreshConnections() async {
    final results = await Future.wait([
      _ollama.isAvailable(),
      _amora.isAvailable(),
      _ollama.listModels(),
    ]);
    ollamaOnline = results[0] as bool;
    backendOnline = results[1] as bool;
    availableModels = results[2] as List<String>;
    if (selectedModel.isEmpty && availableModels.isNotEmpty) {
      selectedModel = availableModels.first;
    }
    notifyListeners();
  }

  void setModel(String m) {
    selectedModel = m;
    notifyListeners();
  }

  void setAppMode(AppMode m) {
    appMode = m;
    notifyListeners();
  }

  void setRankingMode(String m) {
    rankingMode = m;
    notifyListeners();
  }

  void setTopK(int k) {
    topK = k;
    notifyListeners();
  }

  void setTemperature(double t) {
    temperature = t;
    notifyListeners();
  }

  void setCostSensitive(bool v) {
    costSensitive = v;
    notifyListeners();
  }

  void setConflictSensitive(bool v) {
    conflictSensitive = v;
    notifyListeners();
  }

  void setForceRetrieval(bool v) {
    forceRetrieval = v;
    notifyListeners();
  }

  void setStreamEnabled(bool v) {
    streamEnabled = v;
    notifyListeners();
  }

  void clearChat() {
    messages.clear();
    compareMessages.clear();
    totalQueries = 0;
    totalTokens = 0;
    totalLatency = 0;
    notifyListeners();
  }

  // ── Helper token counter ───────────────────────────────────────
  int _countTokens(String text) {
    if (text.trim().isEmpty) return 0;
    return (text.trim().split(RegExp(r'\s+')).length * 1.3).round();
  }

  // ─────────────────────────────────────────────────────────────
  //  SEND QUERY
  // ─────────────────────────────────────────────────────────────
  Future<void> sendQuery(String query) async {
    if (isGenerating || query.trim().isEmpty) return;
    isGenerating = true;
    totalQueries++;
    notifyListeners();

    if (appMode == AppMode.compare) {
      await _sendCompare(query.trim());
    } else {
      await _sendSingle(query.trim());
    }

    isGenerating = false;
    notifyListeners();
  }

  // ── Single mode ───────────────────────────────────────────────
  Future<void> _sendSingle(String query) async {
    final sw = Stopwatch()..start();
    final userId = _id();
    messages.add(ChatMessage(id: userId, role: MessageRole.user, content: query));
    notifyListeners();

    AmoraPipeline? pipeline;
    String evidenceCtx = '';

    // 1. If LLM with AMOF mode, route & retrieve first
    if (appMode == AppMode.withAmora && backendOnline) {
      try {
        final result = await _amora.route(
          query: query,
          mode: rankingMode,
          topK: topK,
          costSensitive: costSensitive,
          conflictSensitive: conflictSensitive,
          forcedRetrieval: forceRetrieval ? true : null,
        );
        pipeline = result.pipeline;
        evidenceCtx = result.evidenceContext;
      } catch (e) {
        debugPrint('AMOF route error: $e');
      }
    }

    // 2. Generate with Ollama
    final assistId = _id();
    final assistMsg = ChatMessage(
      id: assistId,
      role: MessageRole.assistant,
      mode: appMode == AppMode.withAmora ? ChatMode.withAmora : ChatMode.directLlm,
      content: '',
      isStreaming: true,
      model: selectedModel,
      pipeline: pipeline,
    );
    messages.add(assistMsg);
    notifyListeners();

    final ollamaMessages = _buildMessages(query, evidenceCtx);
    final buf = StringBuffer();

    if (streamEnabled) {
      try {
        await for (final chunk in _ollama.streamChat(
          model: selectedModel,
          messages: ollamaMessages,
          temperature: temperature,
        )) {
          buf.write(chunk);
          _updateLastMessage(buf.toString(), isStreaming: true, pipeline: pipeline);
        }
      } catch (e) {
        buf.write('\n\n⚠️ Streaming error: $e');
      }
    } else {
      try {
        final resp = await _ollama.chat(
          model: selectedModel,
          messages: ollamaMessages,
          temperature: temperature,
        );
        buf.write(resp);
      } catch (e) {
        buf.write('⚠️ Error: $e');
      }
    }

    sw.stop();
    final elapsedMs = sw.elapsedMilliseconds.toDouble();
    final promptToks = _countTokens(query) + (evidenceCtx.isNotEmpty ? _countTokens(evidenceCtx) : 0);
    final outputToks = _countTokens(buf.toString());
    final msgTokens = promptToks + outputToks;

    if (pipeline != null) {
      pipeline = pipeline.copyWith(
        latencyMs: elapsedMs,
        tokens: msgTokens,
      );
    }
    totalTokens += msgTokens;
    totalLatency += elapsedMs;

    _updateLastMessage(
      buf.toString(),
      isStreaming: false,
      pipeline: pipeline,
      latencyMs: elapsedMs,
      tokens: msgTokens,
    );
  }

  // ── Compare mode ──────────────────────────────────────────────
  Future<void> _sendCompare(String query) async {
    final cmpId = _id();
    final cmp = CompareMessage(id: cmpId, query: query);
    compareMessages.add(cmp);
    notifyListeners();

    // Run sequentially to ensure local Ollama doesn't struggle with concurrency
    await _runAmoraColumn(cmpId, query);
    await _runDirectColumn(cmpId, query);
  }

  Future<void> _runAmoraColumn(String cmpId, String query) async {
    final sw = Stopwatch()..start();
    AmoraPipeline? pipeline;
    String evidenceCtx = '';

    if (backendOnline) {
      try {
        final result = await _amora.route(
          query: query,
          mode: rankingMode,
          topK: topK,
          costSensitive: costSensitive,
          conflictSensitive: conflictSensitive,
          forcedRetrieval: forceRetrieval ? true : null,
        );
        pipeline = result.pipeline;
        evidenceCtx = result.evidenceContext;
      } catch (e) {
        debugPrint('AMOF error: $e');
      }
    }

    final buf = StringBuffer();
    final ollamaMessages = _buildMessages(query, evidenceCtx);

    _updateCompare(cmpId, amoraMsg: ChatMessage(
      id: _id(), role: MessageRole.assistant,
      content: '', mode: ChatMode.withAmora,
      isStreaming: true, model: selectedModel, pipeline: pipeline,
    ));

    if (streamEnabled) {
      try {
        await for (final chunk in _ollama.streamChat(
          model: selectedModel, messages: ollamaMessages, temperature: temperature,
        )) {
          buf.write(chunk);
          _updateCompare(cmpId, amoraMsg: ChatMessage(
            id: _id(), role: MessageRole.assistant,
            content: buf.toString(), mode: ChatMode.withAmora,
            isStreaming: true, model: selectedModel, pipeline: pipeline,
          ));
        }
      } catch (e) {
        buf.write('\n\n⚠️ $e');
      }
    } else {
      try {
        final r = await _ollama.chat(model: selectedModel, messages: ollamaMessages, temperature: temperature);
        buf.write(r);
      } catch (e) {
        buf.write('⚠️ $e');
      }
    }

    sw.stop();
    final elapsedMs = sw.elapsedMilliseconds.toDouble();
    final promptToks = _countTokens(query) + (evidenceCtx.isNotEmpty ? _countTokens(evidenceCtx) : 0);
    final outputToks = _countTokens(buf.toString());
    final colTokens = promptToks + outputToks;

    if (pipeline != null) {
      pipeline = pipeline.copyWith(
        latencyMs: elapsedMs,
        tokens: colTokens,
      );
    }
    totalTokens += colTokens;
    totalLatency += elapsedMs;

    _updateCompare(cmpId, amoraMsg: ChatMessage(
      id: _id(), role: MessageRole.assistant,
      content: buf.toString(), mode: ChatMode.withAmora,
      isStreaming: false, model: selectedModel, pipeline: pipeline,
      latencyMs: elapsedMs,
      tokens: colTokens,
    ));
  }

  Future<void> _runDirectColumn(String cmpId, String query) async {
    final sw = Stopwatch()..start();
    final buf = StringBuffer();
    final rawMessages = [
      {'role': 'system', 'content': 'You are a helpful AI assistant. Answer directly and concisely based on your general knowledge.'},
      {'role': 'user', 'content': query},
    ];

    _updateCompare(cmpId, directMsg: ChatMessage(
      id: _id(), role: MessageRole.assistant,
      content: '', mode: ChatMode.directLlm,
      isStreaming: true, model: selectedModel,
    ));

    if (streamEnabled) {
      try {
        await for (final chunk in _ollama.streamChat(
          model: selectedModel, messages: rawMessages, temperature: temperature,
        )) {
          buf.write(chunk);
          _updateCompare(cmpId, directMsg: ChatMessage(
            id: _id(), role: MessageRole.assistant,
            content: buf.toString(), mode: ChatMode.directLlm,
            isStreaming: true, model: selectedModel,
          ));
        }
      } catch (e) {
        buf.write('\n\n⚠️ $e');
      }
    } else {
      try {
        final r = await _ollama.chat(model: selectedModel, messages: rawMessages, temperature: temperature);
        buf.write(r);
      } catch (e) {
        buf.write('⚠️ $e');
      }
    }

    sw.stop();
    final elapsedMs = sw.elapsedMilliseconds.toDouble();
    final promptToks = _countTokens(query);
    final outputToks = _countTokens(buf.toString());
    final dirTokens = promptToks + outputToks;
    totalTokens += dirTokens;
    totalLatency += elapsedMs;

    _updateCompare(cmpId, directMsg: ChatMessage(
      id: _id(), role: MessageRole.assistant,
      content: buf.toString(), mode: ChatMode.directLlm,
      isStreaming: false, model: selectedModel,
      latencyMs: elapsedMs,
      tokens: dirTokens,
    ));
  }

  // ── Helpers ───────────────────────────────────────────────────
  void _updateLastMessage(String content, {bool? isStreaming, AmoraPipeline? pipeline, double? latencyMs, int? tokens}) {
    if (messages.isEmpty) return;
    final last = messages.last;
    messages[messages.length - 1] = last.copyWith(
      content: content,
      isStreaming: isStreaming,
      pipeline: pipeline ?? last.pipeline,
      latencyMs: latencyMs ?? last.latencyMs,
      tokens: tokens ?? last.tokens,
    );
    notifyListeners();
  }

  void _updateCompare(String cmpId, {ChatMessage? amoraMsg, ChatMessage? directMsg}) {
    final idx = compareMessages.indexWhere((c) => c.id == cmpId);
    if (idx == -1) return;
    compareMessages[idx] = compareMessages[idx].copyWith(
      amoraMessage: amoraMsg,
      directMessage: directMsg,
    );
    notifyListeners();
  }

  List<Map<String, String>> _buildMessages(String query, String evidenceCtx) {
    const system = '''You are an expert AI assistant enhanced with the AMOF (Adaptive Multi-Objective Framework) RAG system.
Your task is to answer the user query accurately and comprehensively.
GUIDELINES:
1. When external evidence is provided, ground your answer directly in the facts, quantities, dates, and specifications from that evidence.
2. Cite the sources using [Source: Source Name].
3. Highlight specific numbers and details found in the evidence.
4. If no external evidence is provided, provide the best answer from your model knowledge.''';

    final userContent = evidenceCtx.isNotEmpty
        ? 'USER QUERY:\n$query\n\nRETRIEVED EXTERNAL EVIDENCE (via AMOF Multi-Source):\n$evidenceCtx\n\nPlease answer the user query based on the above evidence, citing specific sources.'
        : query;

    return [
      {'role': 'system', 'content': system},
      {'role': 'user', 'content': userContent},
    ];
  }

  String _id() => DateTime.now().microsecondsSinceEpoch.toString();
}
