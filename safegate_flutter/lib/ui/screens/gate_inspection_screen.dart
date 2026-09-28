import 'dart:async';
import 'package:flutter/material.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_theme.dart';
import '../../data/services/safegate_api_service.dart';

class GateInspectionScreen extends StatefulWidget {
  final SafeGateApiService apiService;

  const GateInspectionScreen({super.key, required this.apiService});

  @override
  State<GateInspectionScreen> createState() => _GateInspectionScreenState();
}

class _GateInspectionScreenState extends State<GateInspectionScreen> {
  Timer? _statusTimer;
  Map<String, dynamic> _gateState = {};
  bool _isOnline = false;
  bool _isSimHelmet = true;
  bool _isSimVest = true;
  bool _isHoldingHelmet = false;
  int _imageKey = 0;

  @override
  void initState() {
    super.initState();
    _checkServer();
    _startStatusPolling();
  }

  @override
  void dispose() {
    _statusTimer?.cancel();
    super.dispose();
  }

  Future<void> _checkServer() async {
    final online = await widget.apiService.checkHealth();
    if (mounted) {
      setState(() => _isOnline = online);
    }
  }

  void _startStatusPolling() {
    _statusTimer = Timer.periodic(const Duration(milliseconds: 700), (_) async {
      final state = await widget.apiService.fetchGateState();
      if (mounted) {
        setState(() {
          _gateState = state;
          _isOnline = state['state'] != 'OFFLINE';
          if (state['sim_helmet'] != null) _isSimHelmet = state['sim_helmet'] as bool;
          if (state['sim_vest'] != null) _isSimVest = state['sim_vest'] as bool;
        });
      }
    });
  }

  Future<void> _sendAction(String action) async {
    await widget.apiService.sendControlAction(action);
    setState(() => _imageKey++);
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 850;

        if (isWide) {
          return Padding(
            padding: const EdgeInsets.all(20.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 7, child: _buildStreamCard()),
                const SizedBox(width: 20),
                Expanded(flex: 4, child: SingleChildScrollView(child: _buildControlPanel())),
              ],
            ),
          );
        } else {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(height: 380, child: _buildStreamCard()),
                const SizedBox(height: 16),
                _buildControlPanel(),
              ],
            ),
          );
        }
      },
    );
  }

  Widget _buildStreamCard() {
    final stateName = _gateState['state'] as String? ?? 'SCANNING_QR';
    final fps = _gateState['fps'] as num? ?? 0.0;
    final voteScore = _gateState['voting_score'] as String? ?? '0/10';
    final finalStatus = _gateState['final_status'] as String? ?? 'CHECKING';

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header Bar
          Container(
            color: const Color(0xFF161E34),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: _isOnline ? AppTheme.secondary : AppTheme.error,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _isOnline ? 'LIVE FEED (ONLINE)' : 'SERVER CHƯA KHỞI ĐỘNG',
                    style: TextStyle(
                      color: _isOnline ? AppTheme.secondary : AppTheme.error,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    '${fps.toStringAsFixed(1)} FPS',
                    style: const TextStyle(
                      color: AppTheme.primary,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Video Stream
          Expanded(
            child: Container(
              color: Colors.black,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  if (_isOnline)
                    Image.network(
                      '${ApiConstants.videoFeedUrl}?k=$_imageKey',
                      fit: BoxFit.contain,
                      gaplessPlayback: true,
                      errorBuilder: (_, _, _) => _buildPlaceholderStream(),
                    )
                  else
                    _buildPlaceholderStream(),

                  Positioned(
                    top: 12,
                    left: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.6),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'TRẠNG THÁI: $stateName',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Bottom Banner
          Container(
            color: finalStatus == 'PASS'
                ? const Color(0xFF065F46)
                : (finalStatus == 'FAIL' ? const Color(0xFF991B1B) : const Color(0xFF1E293B)),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              children: [
                Icon(
                  finalStatus == 'PASS'
                      ? Icons.check_circle_rounded
                      : (finalStatus == 'FAIL' ? Icons.cancel_rounded : Icons.sync_rounded),
                  color: Colors.white,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    finalStatus == 'PASS'
                        ? 'PASS - ĐẠT TIÊU CHUẨN'
                        : (finalStatus == 'FAIL' ? 'FAIL - VI PHẠM AN TOÀN' : 'ĐANG KIỂM TRA QUY CHUẨN...'),
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Text(
                  'Voting: $voteScore',
                  style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControlPanel() {
    final employee = _gateState['employee'] as Map<String, dynamic>?;
    final missingItems = (_gateState['missing_items'] as List<dynamic>? ?? []).cast<String>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Employee Info Card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.badge_rounded, color: AppTheme.primary, size: 20),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'CÔNG NHÂN ĐANG KIỂM TRA',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppTheme.textSecondary),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const Divider(height: 20),
                if (employee != null) ...[
                  _infoRow('Họ và tên:', employee['full_name'] as String? ?? 'Chưa rõ'),
                  _infoRow('Mã nhân viên:', employee['employee_code'] as String? ?? ''),
                  _infoRow('Bộ phận:', employee['department'] as String? ?? 'N/A'),
                  _infoRow('Chức vụ:', employee['role'] as String? ?? 'Công nhân'),
                ] else ...[
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8.0),
                    child: Text(
                      'Chưa quét thẻ nhân viên.\nHãy đưa thẻ QR trước camera hoặc bấm nút dưới.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Controls Card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.tune_rounded, color: AppTheme.primary, size: 20),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'BẢNG ĐIỀU KHIỂN GIẢ LẬP',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppTheme.textSecondary),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const Divider(height: 20),

                ElevatedButton.icon(
                  onPressed: () => _sendAction('scan_card'),
                  icon: const Icon(Icons.qr_code_scanner_rounded),
                  label: const Text('GIƠ THẺ QR (NV-1001)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primary,
                    foregroundColor: const Color(0xFF0B132B),
                    minimumSize: const Size.fromHeight(44),
                  ),
                ),
                const SizedBox(height: 10),

                OutlinedButton.icon(
                  onPressed: () => _sendAction('check'),
                  icon: const Icon(Icons.play_arrow_rounded),
                  label: const Text('KÍCH HOẠT KIỂM TRA NGAY'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppTheme.textPrimary,
                    side: const BorderSide(color: AppTheme.border),
                    minimumSize: const Size.fromHeight(44),
                  ),
                ),

                const SizedBox(height: 14),
                const Text('Kịch bản kiểm thử AI & Luật hình học:', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary, fontWeight: FontWeight.w600)),
                const SizedBox(height: 6),

                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Mũ bảo hộ', style: TextStyle(fontSize: 13)),
                  subtitle: Text(_isSimHelmet ? 'Đang đội mũ' : 'Thiếu mũ bảo hộ', style: const TextStyle(fontSize: 11)),
                  value: _isSimHelmet,
                  onChanged: (val) {
                    setState(() => _isSimHelmet = val);
                    _sendAction('toggle_helmet');
                  },
                ),

                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Áo phản quang', style: TextStyle(fontSize: 13)),
                  subtitle: Text(_isSimVest ? 'Đang mặc áo' : 'Thiếu áo phản quang', style: const TextStyle(fontSize: 11)),
                  value: _isSimVest,
                  onChanged: (val) {
                    setState(() => _isSimVest = val);
                    _sendAction('toggle_vest');
                  },
                ),

                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Cầm mũ trên tay (Gian lận)', style: TextStyle(fontSize: 13, color: Color(0xFFF87171))),
                  subtitle: const Text('Test luật hình học phát hiện vị trí sai', style: TextStyle(fontSize: 11)),
                  value: _isHoldingHelmet,
                  onChanged: (val) {
                    setState(() => _isHoldingHelmet = val);
                    _sendAction('toggle_holding');
                  },
                ),

                const SizedBox(height: 8),
                OutlinedButton.icon(
                  onPressed: () => _sendAction('reset'),
                  icon: const Icon(Icons.refresh_rounded, size: 16),
                  label: const Text('RESET CỔNG'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppTheme.textSecondary,
                    side: const BorderSide(color: AppTheme.border),
                    minimumSize: const Size.fromHeight(38),
                  ),
                ),
              ],
            ),
          ),
        ),

        if (missingItems.isNotEmpty) ...[
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.error.withValues(alpha: 0.15),
              border: Border.all(color: AppTheme.error.withValues(alpha: 0.4)),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: AppTheme.error, size: 16),
                    SizedBox(width: 6),
                    Text('CÁC MÓN CHƯA ĐẠT:', style: TextStyle(color: AppTheme.error, fontWeight: FontWeight.bold, fontSize: 12)),
                  ],
                ),
                const SizedBox(height: 4),
                ...missingItems.map(
                  (item) => Padding(
                    padding: const EdgeInsets.only(left: 22.0, top: 2),
                    child: Text('• $item', style: const TextStyle(color: Colors.white, fontSize: 12)),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildPlaceholderStream() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.videocam_off_rounded, size: 40, color: AppTheme.textSecondary),
          const SizedBox(height: 10),
          const Text('Chưa kết nối được luồng Video Stream', style: TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
          const SizedBox(height: 4),
          Text('Khởi động backend SafeGate: python safegate/api/server.py', style: TextStyle(color: AppTheme.textSecondary.withValues(alpha: 0.8), fontSize: 11)),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textPrimary, fontSize: 12)),
        ],
      ),
    );
  }
}
