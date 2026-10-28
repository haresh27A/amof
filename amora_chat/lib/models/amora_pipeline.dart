// models/amora_pipeline.dart

class AmoraSource {
  final String sourceId;
  final String name;
  final String tool;
  final double score;
  final double dstBelief;
  final double dstCombinedScore;
  final double relevance;
  final double reliability;
  final double freshness;
  final double cost;
  final double historicalSuccess;
  final double conflict;

  AmoraSource({
    required this.sourceId,
    required this.name,
    required this.tool,
    required this.score,
    required this.dstBelief,
    required this.dstCombinedScore,
    required this.relevance,
    required this.reliability,
    required this.freshness,
    required this.cost,
    required this.historicalSuccess,
    required this.conflict,
  });

  factory AmoraSource.fromJson(Map<String, dynamic> j) => AmoraSource(
        sourceId: j['source_id'] ?? '',
        name: j['name'] ?? j['source_id'] ?? '',
        tool: j['tool'] ?? '',
        score: (j['score'] ?? 0.0).toDouble(),
        dstBelief: (j['dst_belief'] ?? 0.0).toDouble(),
        dstCombinedScore: (j['dst_combined_score'] ?? 0.0).toDouble(),
        relevance: (j['relevance'] ?? 0.0).toDouble(),
        reliability: (j['reliability'] ?? 0.0).toDouble(),
        freshness: (j['freshness'] ?? 0.0).toDouble(),
        cost: (j['cost'] ?? 0.0).toDouble(),
        historicalSuccess: (j['historical_success'] ?? 0.0).toDouble(),
        conflict: (j['conflict'] ?? 0.0).toDouble(),
      );
}

class AmoraPipeline {
  final bool retrievalRequired;
  final double kActivationScore;
  final String retrievalQuery;
  final int totalCatalogSources;
  final int candidateCount;
  final List<AmoraSource> selectedSources;
  final Map<String, double> weights;
  final int retrievedEvidenceCount;
  final double latencyMs;
  final int tokens;
  final double amoraEfficiencyScore;
  final double sourceReductionRatio;
  final bool conflictDetected;

  AmoraPipeline({
    required this.retrievalRequired,
    required this.kActivationScore,
    required this.retrievalQuery,
    required this.totalCatalogSources,
    required this.candidateCount,
    required this.selectedSources,
    required this.weights,
    required this.retrievedEvidenceCount,
    required this.latencyMs,
    required this.tokens,
    required this.amoraEfficiencyScore,
    required this.sourceReductionRatio,
    required this.conflictDetected,
  });

  factory AmoraPipeline.fromJson(Map<String, dynamic> j) => AmoraPipeline(
        retrievalRequired: j['retrieval_required'] ?? true,
        kActivationScore: (j['k_activation_score'] ?? 0.0).toDouble(),
        retrievalQuery: j['retrieval_query'] ?? '',
        totalCatalogSources: j['total_catalog_sources'] ?? 0,
        candidateCount: j['candidate_count'] ?? 0,
        selectedSources: ((j['selected_sources'] ?? []) as List)
            .map((s) => AmoraSource.fromJson(s))
            .toList(),
        weights: Map<String, double>.from(
          (j['weights'] ?? {}).map((k, v) => MapEntry(k.toString(), (v as num).toDouble())),
        ),
        retrievedEvidenceCount: j['retrieved_evidence_count'] ?? 0,
        latencyMs: (j['latency_ms'] ?? 0.0).toDouble(),
        tokens: j['tokens'] ?? 0,
        amoraEfficiencyScore: (j['amora_efficiency_score'] ?? 0.0).toDouble(),
        sourceReductionRatio: (j['source_reduction_ratio'] ?? 0.0).toDouble(),
        conflictDetected: j['conflict_detected'] ?? false,
      );

  AmoraPipeline copyWith({
    bool? retrievalRequired,
    double? kActivationScore,
    String? retrievalQuery,
    int? totalCatalogSources,
    int? candidateCount,
    List<AmoraSource>? selectedSources,
    Map<String, double>? weights,
    int? retrievedEvidenceCount,
    double? latencyMs,
    int? tokens,
    double? amoraEfficiencyScore,
    double? sourceReductionRatio,
    bool? conflictDetected,
  }) =>
      AmoraPipeline(
        retrievalRequired: retrievalRequired ?? this.retrievalRequired,
        kActivationScore: kActivationScore ?? this.kActivationScore,
        retrievalQuery: retrievalQuery ?? this.retrievalQuery,
        totalCatalogSources: totalCatalogSources ?? this.totalCatalogSources,
        candidateCount: candidateCount ?? this.candidateCount,
        selectedSources: selectedSources ?? this.selectedSources,
        weights: weights ?? this.weights,
        retrievedEvidenceCount: retrievedEvidenceCount ?? this.retrievedEvidenceCount,
        latencyMs: latencyMs ?? this.latencyMs,
        tokens: tokens ?? this.tokens,
        amoraEfficiencyScore: amoraEfficiencyScore ?? this.amoraEfficiencyScore,
        sourceReductionRatio: sourceReductionRatio ?? this.sourceReductionRatio,
        conflictDetected: conflictDetected ?? this.conflictDetected,
      );
}
