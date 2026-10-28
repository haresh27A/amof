// AMOF API Models
class QueryResponse {
  final String query;
  final bool retrievalRequired;
  final double kActivationScore;
  final String retrievalQuery;
  final int totalCatalogSources;
  final int candidateCount;
  final Map<String, double> weights;
  final List<SelectedSource> selectedSources;
  final List<String> tools;
  final int retrievedEvidenceCount;
  final String evidenceContext;
  final String finalAnswer;
  final double latencyMs;
  final int tokens;
  final Map<String, int> tokenDetails;
  final double amoraEfficiencyScore;
  final double sourceReductionRatio;
  final double accuracyScore;
  // Which engine actually produced `finalAnswer`. 'STUB - ...' means no generative
  // model ran and the text is a canned template.
  final String providerUsed;
  final bool usedStubResponse;
  final String llmNote;

  QueryResponse({
    required this.query,
    required this.retrievalRequired,
    required this.kActivationScore,
    required this.retrievalQuery,
    required this.totalCatalogSources,
    required this.candidateCount,
    required this.weights,
    required this.selectedSources,
    required this.tools,
    required this.retrievedEvidenceCount,
    required this.evidenceContext,
    required this.finalAnswer,
    required this.latencyMs,
    required this.tokens,
    required this.tokenDetails,
    required this.amoraEfficiencyScore,
    required this.sourceReductionRatio,
    required this.accuracyScore,
    this.providerUsed = 'unknown',
    this.usedStubResponse = false,
    this.llmNote = '',
  });

  factory QueryResponse.fromJson(Map<String, dynamic> j) => QueryResponse(
    query: j['query'] ?? '',
    retrievalRequired: j['retrieval_required'] ?? false,
    kActivationScore: (j['k_activation_score'] ?? 0.0).toDouble(),
    retrievalQuery: j['retrieval_query'] ?? '',
    totalCatalogSources: j['total_catalog_sources'] ?? 0,
    candidateCount: j['candidate_count'] ?? 0,
    weights: Map<String, double>.from(
      (j['weights'] as Map<String, dynamic>? ?? {}).map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ),
    ),
    selectedSources: (j['selected_sources'] as List? ?? [])
        .map((s) => SelectedSource.fromJson(s))
        .toList(),
    tools: List<String>.from(j['tools'] ?? []),
    retrievedEvidenceCount: j['retrieved_evidence_count'] ?? 0,
    evidenceContext: j['evidence_context'] ?? '',
    finalAnswer: j['final_answer'] ?? '',
    latencyMs: (j['latency_ms'] ?? 0.0).toDouble(),
    tokens: j['tokens'] ?? 0,
    tokenDetails: Map<String, int>.from(
      (j['token_details'] as Map<String, dynamic>? ?? {}).map(
        (k, v) => MapEntry(k, (v as num).toInt()),
      ),
    ),
    amoraEfficiencyScore: (j['amora_efficiency_score'] ?? 0.0).toDouble(),
    sourceReductionRatio: (j['source_reduction_ratio'] ?? 0.0).toDouble(),
    accuracyScore: (j['accuracy_score'] ?? 0.95).toDouble(),
    providerUsed: j['provider_used'] ?? 'unknown',
    usedStubResponse: j['used_stub_response'] ?? false,
    llmNote: j['llm_note'] ?? '',
  );
}

class SelectedSource {
  final String sourceId;
  final String name;
  final double score;
  final String tool;
  final double relevance;
  final double reliability;
  final double freshness;
  final double cost;
  final double historicalSuccess;
  final double conflict;

  SelectedSource({
    required this.sourceId,
    required this.name,
    required this.score,
    required this.tool,
    required this.relevance,
    required this.reliability,
    required this.freshness,
    required this.cost,
    required this.historicalSuccess,
    required this.conflict,
  });

  factory SelectedSource.fromJson(Map<String, dynamic> j) => SelectedSource(
    sourceId: j['source_id'] ?? '',
    name: j['name'] ?? '',
    score: (j['score'] ?? 0.0).toDouble(),
    tool: j['tool'] ?? '',
    relevance: (j['relevance'] ?? 0.0).toDouble(),
    reliability: (j['reliability'] ?? 0.0).toDouble(),
    freshness: (j['freshness'] ?? 0.0).toDouble(),
    cost: (j['cost'] ?? 0.0).toDouble(),
    historicalSuccess: (j['historical_success'] ?? 0.0).toDouble(),
    conflict: (j['conflict'] ?? 0.0).toDouble(),
  );
}

class FreeChatResponse {
  final String question;
  final String answer;
  final String providerUsed;
  final int promptTokens;
  final int outputTokens;
  final int totalTokens;
  final double latencyMs;
  final double accuracyScore;
  final bool usedStubResponse;

  FreeChatResponse({
    required this.question,
    required this.answer,
    required this.providerUsed,
    required this.promptTokens,
    required this.outputTokens,
    required this.totalTokens,
    required this.latencyMs,
    required this.accuracyScore,
    this.usedStubResponse = false,
  });

  factory FreeChatResponse.fromJson(Map<String, dynamic> j) => FreeChatResponse(
    question: j['question'] ?? '',
    answer: j['answer'] ?? '',
    providerUsed: j['provider_used'] ?? '',
    promptTokens: j['prompt_tokens'] ?? 0,
    outputTokens: j['output_tokens'] ?? 0,
    totalTokens: j['total_tokens'] ?? 0,
    latencyMs: (j['latency_ms'] ?? 0.0).toDouble(),
    accuracyScore: (j['accuracy_score'] ?? 0.20).toDouble(),
    usedStubResponse: j['used_stub_response'] ?? false,
  );
}

class Source {
  final String sourceId;
  final String name;
  final String sourceType;
  final String domain;
  final String description;
  final double reliability;
  final double cost;

  Source({
    required this.sourceId,
    required this.name,
    required this.sourceType,
    required this.domain,
    required this.description,
    required this.reliability,
    required this.cost,
  });

  factory Source.fromJson(Map<String, dynamic> j) => Source(
    sourceId: j['source_id'] ?? '',
    name: j['name'] ?? '',
    sourceType: j['source_type'] ?? '',
    domain: j['domain'] ?? '',
    description: j['description'] ?? '',
    reliability: (j['reliability'] ?? 0.0).toDouble(),
    cost: (j['cost'] ?? 0.0).toDouble(),
  );
}

class ChatMessage {
  final String role; // 'user' | 'assistant'
  final String content;
  final QueryResponse? pipeline;
  final FreeChatResponse? freeMeta;
  final String? provider;
  final bool withAmora;

  ChatMessage({
    required this.role,
    required this.content,
    this.pipeline,
    this.freeMeta,
    this.provider,
    this.withAmora = true,
  });
}

class ProviderStatus {
  final String name;
  final bool configured;
  final String note;

  ProviderStatus({required this.name, required this.configured, required this.note});

  factory ProviderStatus.fromJson(String name, Map<String, dynamic> j) =>
    ProviderStatus(name: name, configured: j['configured'] ?? false, note: j['note'] ?? '');
}
