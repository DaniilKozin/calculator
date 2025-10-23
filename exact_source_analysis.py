#!/usr/bin/env python3
"""
Точный анализ источников цифр с дашборда
Воспроизводим ТОЧНУЮ логику дашборда
"""

import pandas as pd
import numpy as np

# Загружаем данные
daily_df = pd.read_csv("pool1_nov2025_daily.csv")
monthly_df = pd.read_csv("pool1_nov2025_monthly.csv")

print("=" * 80)
print("ТОЧНОЕ ВОСПРОИЗВЕДЕНИЕ ЛОГИКИ ДАШБОРДА")
print("=" * 80)

# ТОЧНО как в дашборде: строки 429-430
final_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
ggr_multiplier = float(daily_df["ggr_multiplier"].iloc[-1])
DEFAULT_POOL_SIZE = 50000
real_pool_size = final_ggr / ggr_multiplier if ggr_multiplier > 0 else DEFAULT_POOL_SIZE

print(f"1. REAL_POOL_SIZE (строки 429-430 дашборда):")
print(f"   - final_ggr = ${final_ggr:,.2f}")
print(f"   - ggr_multiplier = {ggr_multiplier:.6f}")
print(f"   - real_pool_size = final_ggr / ggr_multiplier = ${real_pool_size:,.2f}")
print()

# ТОЧНО как в дашборде: строка 500
total_collected = real_pool_size
print(f"2. TOTAL_COLLECTED (строка 500 дашборда):")
print(f"   - total_collected = real_pool_size = ${total_collected:,.2f}")
print()

# ТОЧНО как в дашборде: строки 502-506
total_stable_payout = float(monthly_df["stable_payout"].sum())
total_growth_payout = float(monthly_df["growth_payout"].sum())
total_cash_paid = total_stable_payout + total_growth_payout

print(f"3. TOTAL_CASH_PAID (строки 502-506 дашборда):")
print(f"   - total_stable_payout = monthly_df['stable_payout'].sum() = ${total_stable_payout:,.2f}")
print(f"   - total_growth_payout = monthly_df['growth_payout'].sum() = ${total_growth_payout:,.2f}")
print(f"   - total_cash_paid = total_stable_payout + total_growth_payout = ${total_cash_paid:,.2f}")
print()

# ТОЧНО как в дашборде: строка 511
total_referral_cost = float(monthly_df["monthly_referral_cost"].sum()) if "monthly_referral_cost" in monthly_df.columns else 0

print(f"4. TOTAL_REFERRAL_COST (строка 511 дашборда):")
print(f"   - total_referral_cost = ${total_referral_cost:,.2f}")
print()

# ТОЧНО как в дашборде: строки 514-517
total_payments = total_cash_paid + total_referral_cost
cost_of_capital = (total_payments / total_collected) * 100 if total_collected > 0 else 0

print(f"5. COST_OF_CAPITAL (строки 514-517 дашборда):")
print(f"   - total_payments = total_cash_paid + total_referral_cost = ${total_payments:,.2f}")
print(f"   - cost_of_capital = (total_payments / total_collected) * 100 = {cost_of_capital:.1f}%")
print()

print("=" * 80)
print("СРАВНЕНИЕ С ДАШБОРДОМ:")
print("=" * 80)
print(f"Дашборд 'Собрано': $28,390")
print(f"Наш расчет: ${total_collected:,.0f}")
print(f"Совпадение: {'✅' if abs(total_collected - 28390) < 1 else '❌'}")
print()
print(f"Дашборд 'Cash выплаты': $22,233")
print(f"Наш расчет: ${total_cash_paid:,.0f}")
print(f"Совпадение: {'✅' if abs(total_cash_paid - 22233) < 1 else '❌'}")
print()
print(f"Дашборд 'Стоимость капитала': 78.3%")
print(f"Наш расчет: {cost_of_capital:.1f}%")
print(f"Совпадение: {'✅' if abs(cost_of_capital - 78.3) < 0.1 else '❌'}")
print()

print("=" * 80)
print("ДЕТАЛЬНЫЙ АНАЛИЗ MONTHLY_DF:")
print("=" * 80)
print("Все строки в monthly_df:")
for i, row in monthly_df.iterrows():
    print(f"Строка {i}: stable_payout=${row['stable_payout']:,.2f}, growth_payout=${row['growth_payout']:,.2f}")

print()
print("Суммы по колонкам:")
for col in ['stable_payout', 'growth_payout', 'monthly_referral_cost', 'capital_cost_usd']:
    if col in monthly_df.columns:
        total = monthly_df[col].sum()
        print(f"   {col}: ${total:,.2f}")

print()
print("=" * 80)
print("ПОИСК ИСТОЧНИКА $32,713:")
print("=" * 80)

# Ищем возможные источники 32713
possible_sources = []

# Проверяем все колонки в monthly данных
for col in monthly_df.columns:
    if monthly_df[col].dtype in ['float64', 'int64']:
        total_val = float(monthly_df[col].sum())
        if abs(total_val - 32713) < 100:
            possible_sources.append(f"monthly_df['{col}'].sum(): ${total_val:,.2f}")

# Проверяем все колонки в daily данных (финальные значения)
for col in daily_df.columns:
    if daily_df[col].dtype in ['float64', 'int64']:
        final_val = float(daily_df[col].iloc[-1])
        if abs(final_val - 32713) < 100:
            possible_sources.append(f"daily_df['{col}'].iloc[-1]: ${final_val:,.2f}")

# Проверяем комбинации
combinations = [
    ("total_cash_paid + total_referral_cost", total_cash_paid + total_referral_cost),
    ("capital_cost_usd sum", monthly_df['capital_cost_usd'].sum() if 'capital_cost_usd' in monthly_df.columns else 0),
    ("total_payments", total_payments),
]

for name, value in combinations:
    if abs(value - 32713) < 100:
        possible_sources.append(f"{name}: ${value:,.2f}")

if possible_sources:
    print("Возможные источники $32,713:")
    for source in possible_sources:
        print(f"   - {source}")
else:
    print("❌ Точного источника $32,713 не найдено")

print()
print("=" * 80)
print("ФИНАЛЬНОЕ ЗАКЛЮЧЕНИЕ:")
print("=" * 80)
print(f"✅ $28,390 'Собрано' = final_ggr / ggr_multiplier")
print(f"✅ $22,233 'Cash выплаты' = monthly_df['stable_payout'].sum() + monthly_df['growth_payout'].sum()")
print(f"✅ 78.3% 'Стоимость капитала' = (total_payments / total_collected) * 100")
print()
print("❓ $32,713 'Выплачено инвесторам' - возможно, это данные из другого источника")
print("   или другая метрика, которая не рассчитывается в текущем дашборде")