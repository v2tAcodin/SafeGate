import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../data/models/gate_stats.dart';
import '../../data/services/safegate_api_service.dart';

class AnalyticsScreen extends StatefulWidget {
  final SafeGateApiService apiService;

  const AnalyticsScreen({super.key, required this.apiService});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  GateStats _stats = GateStats.empty();
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    setState(() => _isLoading = true);
    final stats = await widget.apiService.fetchStats();
    if (mounted) {
      setState(() {
        _stats = stats;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'THỐNG KÊ & BÁO CÁO TUÂN THỦ AN TOÀN',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Đo lường thời gian thực tỷ lệ đạt chuẩn trang bị bảo hộ lao động tại công trường',
                    style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                  ),
                ],
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: _loadStats,
                icon: const Icon(Icons.refresh_rounded, size: 18),
                label: const Text('CẬP NHẬT'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.surfaceVariant,
                  foregroundColor: AppTheme.textPrimary,
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // 4 Metric KPI Cards
          Row(
            children: [
              _metricCard('TỔNG LƯỢT KIỂM TRA', _stats.totalChecks.toString(), AppTheme.primary, Icons.checklist_rounded),
              const SizedBox(width: 16),
              _metricCard('LƯỢT ĐẠT (PASS)', _stats.passCount.toString(), AppTheme.secondary, Icons.check_circle_rounded),
              const SizedBox(width: 16),
              _metricCard('LƯỢT VI PHẠM (FAIL)', _stats.failCount.toString(), AppTheme.error, Icons.warning_rounded),
              const SizedBox(width: 16),
              _metricCard('TỶ LỆ TUÂN THỦ', '${_stats.passRate.toStringAsFixed(1)}%', const Color(0xFF38BDF8), Icons.pie_chart_rounded),
            ],
          ),

          const SizedBox(height: 24),

          // Top Violations & Summary
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  flex: 6,
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '⚠️ TOP CÁC VI PHẠM PHỔ BIẾN NHẤT',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textPrimary),
                          ),
                          const Divider(height: 24),
                          if (_stats.topViolations.isEmpty)
                            const Expanded(
                              child: Center(
                                child: Text('Chưa có vi phạm nào được ghi nhận!', style: TextStyle(color: AppTheme.textSecondary)),
                              ),
                            )
                          else
                            Expanded(
                              child: ListView.separated(
                                itemCount: _stats.topViolations.length,
                                separatorBuilder: (_, _) => const Divider(height: 1),
                                itemBuilder: (context, i) {
                                  final v = _stats.topViolations[i];
                                  return ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: AppTheme.error.withValues(alpha: 0.2),
                                      child: Text('#${i + 1}', style: const TextStyle(color: AppTheme.error, fontWeight: FontWeight.bold)),
                                    ),
                                    title: Text(v.item, style: const TextStyle(fontWeight: FontWeight.w600)),
                                    trailing: Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: AppTheme.error.withValues(alpha: 0.15),
                                        borderRadius: BorderRadius.circular(6),
                                      ),
                                      child: Text(
                                        '${v.count} lần',
                                        style: const TextStyle(color: AppTheme.error, fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                ),

                const SizedBox(width: 20),

                Expanded(
                  flex: 4,
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'ℹ️ THÔNG TIN HỆ THỐNG SAFEGATE',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textPrimary),
                          ),
                          const Divider(height: 24),
                          _summaryRow('Tổng số nhân viên đã đăng ký:', '${_stats.totalEmployees} người'),
                          _summaryRow('Cơ chế kiểm tra hình học:', 'Mũ (<=38%), Áo (20%-85%)'),
                          _summaryRow('Ngưỡng voting đa khung hình:', 'Tối thiểu 8/10 frames'),
                          _summaryRow('Chế độ camera:', 'Hỗ trợ Webcam & Virtual Simulator'),
                          _summaryRow('Tiêu chuẩn quyền riêng tư:', 'Không lưu trữ ảnh'),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _metricCard(String label, String value, Color accent, IconData icon) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textSecondary)),
                  Icon(icon, color: accent, size: 20),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                value,
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: accent),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _summaryRow(String title, String val) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
          Text(val, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textPrimary, fontSize: 13)),
        ],
      ),
    );
  }
}
