import 'package:flutter/material.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_theme.dart';
import '../../data/models/employee.dart';
import '../../data/services/safegate_api_service.dart';

class EmployeesScreen extends StatefulWidget {
  final SafeGateApiService apiService;

  const EmployeesScreen({super.key, required this.apiService});

  @override
  State<EmployeesScreen> createState() => _EmployeesScreenState();
}

class _EmployeesScreenState extends State<EmployeesScreen> {
  List<Employee> _employees = [];
  bool _isLoading = true;
  Employee? _selectedEmployee;

  @override
  void initState() {
    super.initState();
    _loadEmployees();
  }

  Future<void> _loadEmployees() async {
    setState(() => _isLoading = true);
    final list = await widget.apiService.fetchEmployees();
    if (mounted) {
      setState(() {
        _employees = list;
        _isLoading = false;
        if (list.isNotEmpty && _selectedEmployee == null) {
          _selectedEmployee = list.first;
        }
      });
    }
  }

  void _showAddEmployeeDialog() {
    final codeCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final deptCtrl = TextEditingController();
    String role = 'Công nhân';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDlgState) => AlertDialog(
          backgroundColor: AppTheme.surface,
          title: const Text('ĐĂNG KÝ NHÂN VIÊN MỚI', style: TextStyle(fontWeight: FontWeight.bold)),
          content: SizedBox(
            width: 400,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: codeCtrl,
                  decoration: const InputDecoration(labelText: 'Mã nhân viên (duy nhất, VD: NV-1008)'),
                ),
                TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(labelText: 'Họ và tên'),
                ),
                TextField(
                  controller: deptCtrl,
                  decoration: const InputDecoration(labelText: 'Bộ phận / Nhà thầu'),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: role,
                  decoration: const InputDecoration(labelText: 'Chức danh'),
                  items: ['Công nhân', 'Kỹ sư', 'Cán bộ an toàn HSE', 'Giám sát', 'Khách']
                      .map((r) => DropdownMenuItem(value: r, child: Text(r)))
                      .toList(),
                  onChanged: (val) {
                    if (val != null) setDlgState(() => role = val);
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('HỦY'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (codeCtrl.text.isNotEmpty && nameCtrl.text.isNotEmpty) {
                  final newEmp = Employee(
                    employeeCode: codeCtrl.text.trim(),
                    fullName: nameCtrl.text.trim(),
                    department: deptCtrl.text.trim(),
                    role: role,
                  );
                  final ok = await widget.apiService.addEmployee(newEmp);
                  if (ok && ctx.mounted) {
                    Navigator.pop(ctx);
                    _loadEmployees();
                  }
                }
              },
              child: const Text('THÊM'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
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
                    'QUẢN LÝ NHÂN VIÊN & THẺ ĐỊNH DANH QR',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Tự động sinh mã QR chuẩn cho từng nhân viên phục vụ quét tại cổng',
                    style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                  ),
                ],
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: _showAddEmployeeDialog,
                icon: const Icon(Icons.person_add_rounded, size: 18),
                label: const Text('THÊM NHÂN VIÊN'),
              ),
            ],
          ),

          const SizedBox(height: 20),

          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Cột danh sách nhân viên (60%)
                Expanded(
                  flex: 6,
                  child: Card(
                    child: _isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : ListView.separated(
                            itemCount: _employees.length,
                            separatorBuilder: (_, _) => const Divider(height: 1),
                            itemBuilder: (context, index) {
                              final emp = _employees[index];
                              final isSelected = _selectedEmployee?.employeeCode == emp.employeeCode;

                              return ListTile(
                                selected: isSelected,
                                selectedTileColor: AppTheme.primary.withValues(alpha: 0.12),
                                leading: CircleAvatar(
                                  backgroundColor: isSelected ? AppTheme.primary : AppTheme.surfaceVariant,
                                  foregroundColor: isSelected ? const Color(0xFF0F172A) : AppTheme.textPrimary,
                                  child: Text(
                                    emp.fullName.isNotEmpty ? emp.fullName[0].toUpperCase() : '?',
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                ),
                                title: Text(
                                  emp.fullName,
                                  style: TextStyle(
                                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                                    color: isSelected ? AppTheme.primary : AppTheme.textPrimary,
                                  ),
                                ),
                                subtitle: Text('${emp.employeeCode} • ${emp.department} • ${emp.role}'),
                                trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14),
                                onTap: () => setState(() => _selectedEmployee = emp),
                              );
                            },
                          ),
                  ),
                ),

                const SizedBox(width: 20),

                // Cột hiển thị Thẻ QR nhân viên (40%)
                Expanded(
                  flex: 4,
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: _selectedEmployee == null
                          ? const Center(child: Text('Chọn nhân viên để xem thẻ'))
                          : Column(
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                const Text(
                                  'THẺ ĐỊNH DANH QR CHUẨN',
                                  style: TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.textSecondary,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                                const SizedBox(height: 16),
                                Expanded(
                                  child: Container(
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(12),
                                      boxShadow: [
                                        BoxShadow(
                                          color: Colors.black.withValues(alpha: 0.3),
                                          blurRadius: 10,
                                          offset: const Offset(0, 4),
                                        ),
                                      ],
                                    ),
                                    clipBehavior: Clip.antiAlias,
                                    child: Image.network(
                                      ApiConstants.badgeUrl(_selectedEmployee!.employeeCode),
                                      fit: BoxFit.contain,
                                      errorBuilder: (_, _, _) => const Center(
                                        child: Text(
                                          'Không tải được thẻ QR',
                                          style: TextStyle(color: Colors.black54),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  'Mã QR chứa: SAFEGATE:${_selectedEmployee!.employeeCode}',
                                  style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                                ),
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
}
