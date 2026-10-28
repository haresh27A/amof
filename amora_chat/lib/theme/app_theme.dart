// theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  static const bg       = Color(0xFFF8FAFC);
  static const bg2      = Color(0xFFFFFFFF);
  static const bg3      = Color(0xFFF1F5F9);
  static const border   = Color(0xFFE2E8F0);
  static const accent   = Color(0xFF7C3AED);
  static const accent2  = Color(0xFF4F46E5);
  static const accentPink = Color(0xFFDB2777);
  static const textPrimary = Color(0xFF0F172A);
  static const textMuted   = Color(0xFF64748B);
  static const textDim     = Color(0xFF94A3B8);
  static const green   = Color(0xFF16A34A);
  static const red     = Color(0xFFDC2626);
  static const orange  = Color(0xFFEA580C);
  static const purple  = Color(0xFF6366F1);

  static final gradient = LinearGradient(
    colors: [accent2, accent, accentPink],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static ThemeData get light => ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: bg,
        fontFamily: 'Segoe UI',
        colorScheme: const ColorScheme.light(
          surface: bg2,
          primary: accent2,
          secondary: accent,
          onSurface: textPrimary,
        ),
        textTheme: ThemeData.light().textTheme.apply(
          bodyColor: textPrimary,
          displayColor: textPrimary,
          fontFamily: 'Segoe UI',
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: bg2,
          foregroundColor: textPrimary,
          elevation: 0,
          surfaceTintColor: Colors.transparent,
        ),
        dividerColor: border,
        cardColor: bg2,
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: bg3,
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
            borderSide: const BorderSide(color: accent2, width: 1.5),
          ),
          hintStyle: const TextStyle(color: textDim),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: accent2,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        ),
        sliderTheme: const SliderThemeData(
          activeTrackColor: accent2,
          thumbColor: accent,
          inactiveTrackColor: bg3,
        ),
      );

  static ThemeData get dark => light;
}
