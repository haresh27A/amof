// AMOF App Theme
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── Palette (Light Mode) ────────────────────────────────────
  static const Color bg           = Color(0xFFF8FAFC); // Slate 50 clean surface
  static const Color bgCard       = Color(0xFFFFFFFF); // Pure white card
  static const Color bgCard2      = Color(0xFFF1F5F9); // Slate 100 appbar / nav
  static const Color border       = Color(0xFFE2E8F0); // Slate 200 border
  static const Color textPrimary  = Color(0xFF0F172A); // Slate 900 crisp primary text
  static const Color textSecond   = Color(0xFF475569); // Slate 600 secondary text
  static const Color textMuted    = Color(0xFF64748B); // Slate 500 muted text
  static const Color accent       = Color(0xFF4F46E5); // Indigo 600
  static const Color accentLight  = Color(0xFF6366F1); // Indigo 500
  static const Color accentPurple = Color(0xFF7C3AED); // Violet 600
  static const Color accentPink   = Color(0xFFDB2777); // Pink 600
  static const Color green        = Color(0xFF16A34A); // Emerald 600
  static const Color red          = Color(0xFFDC2626); // Red 600
  static const Color orange       = Color(0xFFEA580C); // Orange 600

  // Free AI Chat palette
  static const Color freeGreen    = Color(0xFF059669);
  static const Color freeBlue     = Color(0xFF2563EB);
  static const Color freeGreenL   = Color(0xFF10B981);

  // ── Gradients ──────────────────────────────────────────────
  static const LinearGradient accentGrad = LinearGradient(
    colors: [Color(0xFF4F46E5), Color(0xFF7C3AED), Color(0xFFDB2777)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  static const LinearGradient freeGrad = LinearGradient(
    colors: [Color(0xFF059669), Color(0xFF2563EB)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  static const LinearGradient userBubbleGrad = LinearGradient(
    colors: [Color(0xFF4F46E5), Color(0xFF7C3AED)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  static const LinearGradient freeBubbleGrad = LinearGradient(
    colors: [Color(0xFF059669), Color(0xFF0284C7)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // ── ThemeData ──────────────────────────────────────────────
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    scaffoldBackgroundColor: bg,
    colorScheme: const ColorScheme.light(
      surface: bgCard,
      primary: accent,
      secondary: accentPurple,
      onPrimary: Colors.white,
      onSurface: textPrimary,
    ),
    textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme).apply(
      bodyColor: textPrimary,
      displayColor: textPrimary,
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: bgCard,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: GoogleFonts.inter(
        color: textPrimary,
        fontSize: 18,
        fontWeight: FontWeight.w700,
      ),
      iconTheme: const IconThemeData(color: textPrimary),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: bgCard,
      indicatorColor: const Color.fromRGBO(79, 70, 229, 0.12),
      labelTextStyle: WidgetStateProperty.all(
        GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w500, color: textSecond),
      ),
      iconTheme: WidgetStateProperty.all(
        const IconThemeData(color: textSecond, size: 22),
      ),
    ),
    cardTheme: CardThemeData(
      color: bgCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: border, width: 1),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: bgCard,
      hintStyle: GoogleFonts.inter(color: textMuted, fontSize: 14),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: accent, width: 1.5),
      ),
    ),
    dividerTheme: const DividerThemeData(color: border, space: 1),
  );

  static ThemeData get dark => light;
}
