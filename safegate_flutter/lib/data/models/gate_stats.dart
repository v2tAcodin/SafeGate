class GateStats {
  final int totalChecks;
  final int passCount;
  final int failCount;
  final double passRate;
  final int totalEmployees;
  final List<ViolationStat> topViolations;

  const GateStats({
    required this.totalChecks,
    required this.passCount,
    required this.failCount,
    required this.passRate,
    required this.totalEmployees,
    required this.topViolations,
  });

  factory GateStats.empty() {
    return const GateStats(
      totalChecks: 0,
      passCount: 0,
      failCount: 0,
      passRate: 0.0,
      totalEmployees: 0,
      topViolations: [],
    );
  }

  factory GateStats.fromJson(Map<String, dynamic> json) {
    final violations = (json['top_violations'] as List<dynamic>? ?? [])
        .map((v) => ViolationStat.fromJson(v as Map<String, dynamic>))
        .toList();

    return GateStats(
      totalChecks: (json['total_checks'] as num?)?.toInt() ?? 0,
      passCount: (json['pass_count'] as num?)?.toInt() ?? 0,
      failCount: (json['fail_count'] as num?)?.toInt() ?? 0,
      passRate: (json['pass_rate'] as num?)?.toDouble() ?? 0.0,
      totalEmployees: (json['total_employees'] as num?)?.toInt() ?? 0,
      topViolations: violations,
    );
  }
}

class ViolationStat {
  final String item;
  final int count;

  const ViolationStat({required this.item, required this.count});

  factory ViolationStat.fromJson(Map<String, dynamic> json) {
    return ViolationStat(
      item: json['missing_items'] as String? ?? 'Chưa rõ',
      count: (json['cnt'] as num?)?.toInt() ?? 0,
    );
  }
}
