import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../data/services/safegate_api_service.dart';
import '../screens/gate_inspection_screen.dart';
import '../screens/logs_screen.dart';
import '../screens/employees_screen.dart';
import '../screens/analytics_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  final SafeGateApiService _apiService = SafeGateApiService();

  @override
  Widget build(BuildContext context) {
    final screens = [
      GateInspectionScreen(apiService: _apiService),
      LogsScreen(apiService: _apiService),
      EmployeesScreen(apiService: _apiService),
      AnalyticsScreen(apiService: _apiService),
    ];

    return Scaffold(
      body: Row(
        children: [
          // SIDEBAR NAVIGATION RAIL
          Container(
            width: 250,
            color: const Color(0xFF070D1E),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // SafeGate Brand Header
                Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AppTheme.primary.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.shield_rounded, color: AppTheme.primary, size: 28),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Text(
                              'SAFEGATE',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w900,
                                color: AppTheme.textPrimary,
                                letterSpacing: 1.0,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text(
                              'AI PPE GATE-CHECK',
                              style: TextStyle(
                                fontSize: 10,
                                color: AppTheme.primary,
                                fontWeight: FontWeight.bold,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const Divider(height: 1, color: AppTheme.border),
                const SizedBox(height: 12),

                // Navigation Items
                _navItem(0, 'CỔNG KIỂM TRA', Icons.camera_alt_rounded),
                _navItem(1, 'NHẬT KÝ RA VÀO', Icons.history_rounded),
                _navItem(2, 'QUẢN LÝ NHÂN VIÊN', Icons.badge_rounded),
                _navItem(3, 'THỐNG KÊ BÁO CÁO', Icons.bar_chart_rounded),

                const Spacer(),

                // Bottom Info Card
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppTheme.surface.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text('Đề tài CNPM 2026', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primary)),
                        SizedBox(height: 4),
                        Text('YOLO nano • OpenCV • SQLite\nFlutter Desktop & Web', style: TextStyle(fontSize: 11, color: AppTheme.textSecondary)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          // MAIN CONTENT AREA
          Expanded(
            child: Container(
              color: AppTheme.background,
              child: screens[_selectedIndex],
            ),
          ),
        ],
      ),
    );
  }

  Widget _navItem(int index, String title, IconData icon) {
    final isSelected = _selectedIndex == index;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: () => setState(() => _selectedIndex = index),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: isSelected ? AppTheme.primary.withValues(alpha: 0.15) : Colors.transparent,
              borderRadius: BorderRadius.circular(8),
              border: isSelected ? Border.all(color: AppTheme.primary.withValues(alpha: 0.4)) : null,
            ),
            child: Row(
              children: [
                Icon(
                  icon,
                  size: 20,
                  color: isSelected ? AppTheme.primary : AppTheme.textSecondary,
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Text(
                    title,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                      color: isSelected ? AppTheme.primary : AppTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
