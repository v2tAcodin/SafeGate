import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../core/constants/api_constants.dart';
import '../models/employee.dart';
import '../models/access_log.dart';
import '../models/gate_stats.dart';

class SafeGateApiService {
  Future<bool> checkHealth() async {
    try {
      final response = await http
          .get(Uri.parse(ApiConstants.baseUrl))
          .timeout(const Duration(seconds: 2));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>> fetchGateState() async {
    try {
      final response = await http
          .get(Uri.parse(ApiConstants.stateEndpoint))
          .timeout(const Duration(seconds: 2));
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      }
    } catch (_) {}
    return {
      'state': 'OFFLINE',
      'fps': 0.0,
      'voting_score': '0/10',
      'final_status': 'CHECKING',
      'missing_items': [],
      'is_virtual_cam': true,
    };
  }

  Future<GateStats> fetchStats() async {
    try {
      final response = await http
          .get(Uri.parse(ApiConstants.statsEndpoint))
          .timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        return GateStats.fromJson(data);
      }
    } catch (_) {}
    return GateStats.empty();
  }

  Future<List<AccessLog>> fetchLogs({String? status, String? search, int limit = 100}) async {
    try {
      final queryParams = <String, String>{'limit': limit.toString()};
      if (status != null && status.isNotEmpty && status != 'Tất cả') {
        queryParams['status'] = status;
      }
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }

      final uri = Uri.parse(ApiConstants.logsEndpoint).replace(queryParameters: queryParams);
      final response = await http.get(uri).timeout(const Duration(seconds: 3));

      if (response.statusCode == 200) {
        final list = json.decode(utf8.decode(response.bodyBytes)) as List<dynamic>;
        return list.map((item) => AccessLog.fromJson(item as Map<String, dynamic>)).toList();
      }
    } catch (_) {}
    return [];
  }

  Future<List<Employee>> fetchEmployees() async {
    try {
      final response = await http
          .get(Uri.parse(ApiConstants.employeesEndpoint))
          .timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        final list = json.decode(utf8.decode(response.bodyBytes)) as List<dynamic>;
        return list.map((item) => Employee.fromJson(item as Map<String, dynamic>)).toList();
      }
    } catch (_) {}
    return [];
  }

  Future<bool> addEmployee(Employee emp) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConstants.employeesEndpoint),
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: json.encode(emp.toJson()),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<void> sendControlAction(String action, {String? employeeCode}) async {
    try {
      await http.post(
        Uri.parse(ApiConstants.controlEndpoint),
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: json.encode({
          'action': action,
          'employee_code': employeeCode ?? 'NV-1001',
        }),
      );
    } catch (_) {}
  }
}
