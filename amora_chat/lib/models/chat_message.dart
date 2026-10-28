// models/chat_message.dart
import 'amora_pipeline.dart';
import 'direct_llm_pipeline.dart';

enum MessageRole { user, assistant }
enum ChatMode { withAmora, directLlm }

class ChatMessage {
  final String id;
  final MessageRole role;
  final String content;
  final ChatMode? mode;
  final AmoraPipeline? pipeline;
  final DateTime timestamp;
  final bool isStreaming;
  final String? model;
  final double latencyMs;
  final int tokens;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    this.mode,
    this.pipeline,
    this.isStreaming = false,
    this.model,
    this.latencyMs = 0.0,
    this.tokens = 0,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  ChatMessage copyWith({
    String? content,
    AmoraPipeline? pipeline,
    bool? isStreaming,
    double? latencyMs,
    int? tokens,
  }) =>
      ChatMessage(
        id: id,
        role: role,
        content: content ?? this.content,
        mode: mode,
        pipeline: pipeline ?? this.pipeline,
        isStreaming: isStreaming ?? this.isStreaming,
        model: model,
        latencyMs: latencyMs ?? this.latencyMs,
        tokens: tokens ?? this.tokens,
        timestamp: timestamp,
      );
}

/// Paired message for compare mode
class CompareMessage {
  final String id;
  final String query;
  final ChatMessage? amoraMessage;
  final ChatMessage? directMessage;
  final DateTime timestamp;

  CompareMessage({
    required this.id,
    required this.query,
    this.amoraMessage,
    this.directMessage,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  CompareMessage copyWith({
    ChatMessage? amoraMessage,
    ChatMessage? directMessage,
  }) =>
      CompareMessage(
        id: id,
        query: query,
        amoraMessage: amoraMessage ?? this.amoraMessage,
        directMessage: directMessage ?? this.directMessage,
        timestamp: timestamp,
      );
}
