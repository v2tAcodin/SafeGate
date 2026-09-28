class Employee {
  final String employeeCode;
  final String fullName;
  final String department;
  final String role;

  const Employee({
    required this.employeeCode,
    required this.fullName,
    required this.department,
    required this.role,
  });

  factory Employee.fromJson(Map<String, dynamic> json) {
    return Employee(
      employeeCode: json['employee_code'] as String? ?? '',
      fullName: json['full_name'] as String? ?? 'Chưa rõ',
      department: json['department'] as String? ?? 'N/A',
      role: json['role'] as String? ?? 'Công nhân',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'employee_code': employeeCode,
      'full_name': fullName,
      'department': department,
      'role': role,
    };
  }
}
