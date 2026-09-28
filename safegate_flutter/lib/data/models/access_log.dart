class AccessLog {
  final int id;
  final String timestamp;
  final String employeeCode;
  final String employeeName;
  final String department;
  final String status;
  final String missingItems;
  final String voteScore;
  final double checkDuration;

  const AccessLog({
    required this.id,
    required this.timestamp,
    required this.employeeCode,
    required this.employeeName,
    required this.department,
    required this.status,
    required this.missingItems,
    required this.voteScore,
    required this.checkDuration,
  });

  bool get isPass => status.toUpperCase() == 'PASS';

  factory AccessLog.fromJson(Map<String, dynamic> json) {
    return AccessLog(
      id: (json['id'] as num?)?.toInt() ?? 0,
      timestamp: json['timestamp'] as String? ?? '',
      employeeCode: json['employee_code'] as String? ?? '',
      employeeName: json['employee_name'] as String? ?? 'N/A',
      department: json['department'] as String? ?? 'N/A',
      status: json['status'] as String? ?? 'FAIL',
      missingItems: json['missing_items'] as String? ?? '',
      voteScore: json['vote_score'] as String? ?? '0/10',
      checkDuration: (json['check_duration'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
