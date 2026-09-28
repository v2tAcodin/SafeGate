import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:safegate_flutter/main.dart';

void main() {
  testWidgets('SafeGate app smoke test', (WidgetTester tester) async {
    // Thiết lập kích thước desktop cho widget test
    tester.view.physicalSize = const Size(1280, 800);
    tester.view.devicePixelRatio = 1.0;

    await tester.pumpWidget(const SafeGateApp());
    expect(find.text('SAFEGATE'), findsWidgets);
    expect(find.text('CỔNG KIỂM TRA'), findsWidgets);

    // Dọn dẹp kích thước test
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
  });
}
