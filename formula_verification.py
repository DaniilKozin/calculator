#!/usr/bin/env python3
"""
Полная проверка всех формул дашборда
Сравнение с данными из итоговой таблицы доходности по пулам
"""

import pandas as pd
import numpy as np

print("=" * 100)
print("ПОЛНАЯ ПРОВЕРКА ФОРМУЛ ДАШБОРДА")
print("=" * 100)

# Загружаем данные
daily_df = pd.read_csv("pool1_nov2025_daily.csv")
monthly_df = pd.read_csv("pool1_nov2025_monthly.csv")

print("\n1. АНАЛИЗ ДАННЫХ ИЗ ИТОГОВОЙ ТАБЛИЦЫ ДОХОДНОСТИ ПО ПУЛАМ")
print("=" * 80)

# Данные из итоговой таблицы (видимые на скриншоте)
pool_data = {
    "Stable Basic (34%)": {"invested": 5517, "received": 5321, "per_dollar": 0.96},
    "Stable Advanced (38.25%)": {"invested": 5110, "received": 5617, "per_dollar": 1.10},
    "Stable Premium (42.5%)": {"invested": 3407, "received": 4160, "per_dollar": 1.22},
    "Growth Basic (8.5%)": {"invested": 5678, "received": 7065, "per_dollar": 1.24},
    "Growth Advanced (10.625%)": {"invested": 3407, "received": 4447, "per_dollar": 1.31},
    "Growth Premium (12.75%)": {"invested": 2271, "received": 3103, "per_dollar": 1.37}
}

total_invested_pools = 0
total_received_pools = 0

print("Данные по пулам из итоговой таблицы:")
for pool_name, data in pool_data.items():
    invested = data["invested"]
    received = data["received"]
    per_dollar = data["per_dollar"]
    total_invested_pools += invested
    total_received_pools += received
    print(f"  {pool_name}:")
    print(f"    Вложено: ${invested:,}")
    print(f"    Получено: ${received:,}")
    print(f"    На $1 получаем: ${per_dollar:.2f}")
    print()

print(f"ИТОГО по пулам:")
print(f"  Общая сумма вложений: ${total_invested_pools:,}")
print(f"  Общая сумма выплат: ${total_received_pools:,}")
print(f"  Общая доходность: {(total_received_pools / total_invested_pools * 100):.1f}%")

print("\n2. АНАЛИЗ ФОРМУЛ ДАШБОРДА")
print("=" * 80)

# Воспроизводим логику дашборда
final_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
ggr_multiplier = float(daily_df["ggr_multiplier"].iloc[-1])
DEFAULT_POOL_SIZE = 50000
real_pool_size = final_ggr / ggr_multiplier if ggr_multiplier > 0 else DEFAULT_POOL_SIZE

print(f"ФОРМУЛА 1: Собрано (real_pool_size)")
print(f"  Формула: final_ggr / ggr_multiplier")
print(f"  final_ggr = ${final_ggr:,.2f}")
print(f"  ggr_multiplier = {ggr_multiplier:.6f}")
print(f"  Результат: ${real_pool_size:,.2f}")
print(f"  Дашборд показывает: $28,390")
print(f"  Совпадение: {'✅' if abs(real_pool_size - 28390) < 1 else '❌'}")
print()

# Cash выплаты из monthly данных
total_stable_payout = float(monthly_df["stable_payout"].sum())
total_growth_payout = float(monthly_df["growth_payout"].sum())
total_cash_paid = total_stable_payout + total_growth_payout

print(f"ФОРМУЛА 2: Cash выплаты")
print(f"  Формула: monthly_df['stable_payout'].sum() + monthly_df['growth_payout'].sum()")
print(f"  stable_payout сумма = ${total_stable_payout:,.2f}")
print(f"  growth_payout сумма = ${total_growth_payout:,.2f}")
print(f"  Результат: ${total_cash_paid:,.2f}")
print(f"  Дашборд показывает: $22,233")
print(f"  Совпадение: {'✅' if abs(total_cash_paid - 22233) < 1 else '❌'}")
print()

# Реферальные расходы
total_referral_cost = float(monthly_df["monthly_referral_cost"].sum()) if "monthly_referral_cost" in monthly_df.columns else 0

print(f"ФОРМУЛА 3: Реферальные расходы")
print(f"  Формула: monthly_df['monthly_referral_cost'].sum()")
print(f"  Результат: ${total_referral_cost:,.2f}")
print()

# Общие выплаты
total_payments = total_cash_paid + total_referral_cost

print(f"ФОРМУЛА 4: Общие выплаты")
print(f"  Формула: total_cash_paid + total_referral_cost")
print(f"  Результат: ${total_payments:,.2f}")
print()

# Стоимость капитала
cost_of_capital = (total_payments / real_pool_size) * 100 if real_pool_size > 0 else 0

print(f"ФОРМУЛА 5: Стоимость капитала")
print(f"  Формула: (total_payments / real_pool_size) * 100")
print(f"  Результат: {cost_of_capital:.1f}%")
print(f"  Дашборд показывает: 78.3%")
print(f"  Совпадение: {'✅' if abs(cost_of_capital - 78.3) < 0.1 else '❌'}")
print()

print("\n3. СРАВНЕНИЕ С ИТОГОВОЙ ТАБЛИЦЕЙ")
print("=" * 80)

print(f"СРАВНЕНИЕ СУММ:")
print(f"  Итоговая таблица - вложено: ${total_invested_pools:,}")
print(f"  Дашборд - собрано: ${real_pool_size:,.0f}")
print(f"  Разница: ${abs(total_invested_pools - real_pool_size):,.0f}")
print()

print(f"  Итоговая таблица - получено: ${total_received_pools:,}")
print(f"  Дашборд - cash выплаты: ${total_cash_paid:,.0f}")
print(f"  Разница: ${abs(total_received_pools - total_cash_paid):,.0f}")
print()

# Проверяем доходность
table_return_rate = (total_received_pools / total_invested_pools * 100) if total_invested_pools > 0 else 0
dashboard_return_rate = cost_of_capital

print(f"  Итоговая таблица - доходность: {table_return_rate:.1f}%")
print(f"  Дашборд - стоимость капитала: {dashboard_return_rate:.1f}%")
print(f"  Разница: {abs(table_return_rate - dashboard_return_rate):.1f}%")

print("\n4. ДЕТАЛЬНЫЙ АНАЛИЗ MONTHLY_DF")
print("=" * 80)

print("Все строки в monthly_df:")
monthly_total_stable = 0
monthly_total_growth = 0

for i, row in monthly_df.iterrows():
    stable = row['stable_payout']
    growth = row['growth_payout']
    monthly_total_stable += stable
    monthly_total_growth += growth
    print(f"  Строка {i}: stable=${stable:,.2f}, growth=${growth:,.2f}, итого=${stable + growth:,.2f}")

print(f"\nИтого по monthly_df:")
print(f"  Stable: ${monthly_total_stable:,.2f}")
print(f"  Growth: ${monthly_total_growth:,.2f}")
print(f"  Всего: ${monthly_total_stable + monthly_total_growth:,.2f}")

print("\n5. ПРОВЕРКА CAPITAL_COST_USD")
print("=" * 80)

capital_cost_total = monthly_df['capital_cost_usd'].sum() if 'capital_cost_usd' in monthly_df.columns else 0
print(f"Сумма capital_cost_usd: ${capital_cost_total:,.2f}")

# Ищем возможные источники $32,713
print(f"\n6. ПОИСК ИСТОЧНИКА $32,713")
print("=" * 80)

possible_32713_sources = []

# Проверяем различные комбинации
test_values = [
    ("capital_cost_usd сумма", capital_cost_total),
    ("total_payments", total_payments),
    ("total_cash_paid + capital_cost", total_cash_paid + capital_cost_total),
    ("итоговая таблица - получено", total_received_pools),
]

for name, value in test_values:
    if abs(value - 32713) < 100:
        possible_32713_sources.append(f"{name}: ${value:,.2f}")
        print(f"  ✅ {name}: ${value:,.2f} (разница: ${abs(value - 32713):,.0f})")
    else:
        print(f"  ❌ {name}: ${value:,.2f} (разница: ${abs(value - 32713):,.0f})")

print("\n7. ФИНАЛЬНЫЕ ВЫВОДЫ")
print("=" * 80)

print("КОРРЕКТНЫЕ ФОРМУЛЫ:")
print(f"  ✅ Собрано = final_ggr / ggr_multiplier = ${real_pool_size:,.0f}")
print(f"  ✅ Cash выплаты = sum(stable_payout) + sum(growth_payout) = ${total_cash_paid:,.0f}")
print(f"  ✅ Стоимость капитала = (total_payments / real_pool_size) * 100 = {cost_of_capital:.1f}%")

print("\nПРОБЛЕМЫ:")
if abs(total_cash_paid - 22233) > 1:
    print(f"  ❌ Cash выплаты: расчет дает ${total_cash_paid:,.0f}, дашборд показывает $22,233")
    
if abs(real_pool_size - total_invested_pools) > 100:
    print(f"  ❌ Несоответствие между 'собрано' (${real_pool_size:,.0f}) и суммой вложений в пулы (${total_invested_pools:,})")

if abs(total_cash_paid - total_received_pools) > 100:
    print(f"  ❌ Несоответствие между cash выплатами (${total_cash_paid:,.0f}) и суммой получений из пулов (${total_received_pools:,})")

print("\nРЕКОМЕНДАЦИИ:")
print("  1. Проверить источник данных для расчета 'собрано' - возможно, нужно использовать сумму вложений в пулы")
print("  2. Проверить расчет cash выплат - возможно, нужно использовать данные из итоговой таблицы")
print("  3. Убедиться в корректности данных в monthly_df")