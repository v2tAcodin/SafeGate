import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../data/models/access_log.dart';
import '../../data/services/safegate_api_service.dart';

class LogsScreen extends StatefulWidget {
  final SafeGateApiService apiService;

  const LogsScreen({super.key, required this.apiService});

  @override
  State<LogsScreen> createState() => _LogsScreenState();
}

class _LogsScreenState extends State<LogsScreen> {
  List<AccessLog> _logs = [];
  bool _isLoading = true;
  String _selectedStatus = 'Tất cả';
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadLogs();
  }

  Future<void> _loadLogs() async {
    setState(() => _isLoading = true);
    final status = _selectedStatus == 'Tất cả' ? null : _selectedStatus;
    final search = _searchController.text.trim();
    final logs = await widget.apiService.fetchLogs(status: status, search: search);
    if (mounted) {
      setState(() {
        _logs = logs;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header & Filters
          Row(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'NHẬT KÝ KIỂM TRA RA VÀO CỔNG',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Lưu trữ SQLite theo tiêu chí bảo mật: Tuyệt đối không lưu ảnh công nhân',
                    style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                  ),
                ],
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: _loadLogs,
                icon: const Icon(Icons.refresh_rounded, size: 18),
                label: const Text('LÀM MỚI'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.surfaceVariant,
                  foregroundColor: AppTheme.textPrimary,
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Search Bar & Status Chips
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      decoration: const InputDecoration(
                        hintText: 'Tìm kiếm theo tên, mã NV, phòng ban...',
                        prefixIcon: Icon(Icons.search_rounded, color: AppTheme.textSecondary),
                        border: InputBorder.none,
                        isDense: true,
                      ),
                      onSubmitted: (_) => _loadLogs(),
                    ),
                  ),
                  const VerticalDivider(width: 24),
                  Wrap(
                    spacing: 8,
                    children: ['Tất cả', 'PASS', 'FAIL'].map((st) {
                      final isSelected = _selectedStatus == st;
                      return ChoiceChip(
                        label: Text(st),
                        selected: isSelected,
                        selectedColor: st == 'PASS'
                            ? AppTheme.secondary.withValues(alpha: 0.3)
                            : (st == 'FAIL' ? AppTheme.error.withValues(alpha: 0.3) : AppTheme.primary.withValues(alpha: 0.3)),
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : AppTheme.textSecondary,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          fontSize: 12,
                        ),
                        onSelected: (val) {
                          if (val) {
                            setState(() => _selectedStatus = st);
                            _loadLogs();
                          }
                        },
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Data Table
          Expanded(
            child: Card(
              clipBehavior: Clip.antiAlias,
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _logs.isEmpty
                      ? const Center(
                          child: Text(
                            'Chưa có dữ liệu kiểm tra nào phù hợp.',
                            style: TextStyle(color: AppTheme.textSecondary),
                          ),
                        )
                      : ListView.separated(
                          itemCount: _logs.length,
                          separatorBuilder: (_, _) => const Divider(height: 1),
                          itemBuilder: (context, index) {
                            final log = _logs[index];
                            final isPass = log.isPass;

                            return ListTile(
                              leading: Container(
                                width: 44,
                                height: 44,
                                decoration: BoxDecoration(
                                  color: isPass
                                      ? AppTheme.secondary.withValues(alpha: 0.15)
                                      : AppTheme.error.withValues(alpha: 0.15),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(
                                  isPass ? Icons.check_circle_rounded : Icons.cancel_rounded,
                                  color: isPass ? AppTheme.secondary : AppTheme.error,
                                ),
                              ),
                              title: Row(
                                children: [
                                  Text(
                                    log.employeeName,
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                  ),
                                  const SizedBox(width: 8),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: AppTheme.surfaceVariant,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      log.employeeCode,
                                      style: const TextStyle(fontSize: 11, color: AppTheme.primary),
                                    ),
                                  ),
                                  const Spacer(),
                                  Text(
                                    log.timestamp,
                                    style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                                  ),
                                ],
                              ),
                              subtitle: Padding(
                                padding: const EdgeInsets.only(top: 4.0),
                                child: Row(
                                  children: [
                                    Text('Phòng ban: ${log.department}  •  Voting: ${log.voteScore}'),
                                    const Spacer(),
                                    if (!isPass && log.missingItems.isNotEmpty)
                                      Text(
                                        'Thiếu: ${log.missingItems}',
                                        style: const TextStyle(color: Color(0xFFF87171), fontWeight: FontWeight.w600, fontSize: 12),
                                      )
                                    else if (isPass)
                                      const Text(
                                        'Đủ đồ bảo hộ',
                                        style: TextStyle(color: Color(0xFF4ADE80), fontWeight: FontWeight.w600, fontSize: 12),
                                      ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
            ),
          ),
        ],
      ),
    );
  }
}
