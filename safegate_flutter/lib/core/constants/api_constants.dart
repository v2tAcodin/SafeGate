class ApiConstants {
  static const String baseUrl = 'http://localhost:8000';
  static const String videoFeedUrl = '$baseUrl/video_feed';
  static const String stateEndpoint = '$baseUrl/api/state';
  static const String statsEndpoint = '$baseUrl/api/stats';
  static const String logsEndpoint = '$baseUrl/api/logs';
  static const String employeesEndpoint = '$baseUrl/api/employees';
  static const String controlEndpoint = '$baseUrl/api/control';
  static String badgeUrl(String code) => '$baseUrl/api/badge/$code';
}
