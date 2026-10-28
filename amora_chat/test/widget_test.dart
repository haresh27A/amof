import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:amora_chat/main.dart';
import 'package:amora_chat/providers/chat_provider.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => ChatProvider(),
        child: const AmoraChatApp(),
      ),
    );
    expect(find.byType(AmoraChatApp), findsOneWidget);
  });
}
