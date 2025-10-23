#!/usr/bin/env python3
"""
Анализ точных значений с дашборда
===============================

Дашборд показывает:
- Собрано: $28,390
- Cash выплаты: $22,233  
- Стоимость капитала: 78.3%

Пользователь утверждает:
- Привлечено: $28,390
- Инвесторам выплачено: $32,713

Найдем источник этих цифр в CSV данных.
"""

import pandas as pd
import numpy as np

def main():
    print("=" * 80)
    print("АНАЛИЗ ТОЧНЫХ ЗНАЧЕНИЙ С ДАШБОРДА")
    print("=" * 80)
    
    # Загружаем данные
    daily_df = pd.read_csv("pool1_nov2025_daily.csv")
    monthly_df = pd.read_csv("pool1_nov2025_monthly.csv")
    tiers_df = pd.read_csv("pool1_nov2025_monthly_tiers_znx.csv")
    
    print("\n1. ЗНАЧЕНИЯ С ДАШБОРДА:")
    print("-" * 40)
    print("Собрано: $28,390")
    print("Cash выплаты: $22,233")
    print("Стоимость капитала: 78.3%")
    
    print("\n2. УТВЕРЖДЕНИЯ ПОЛЬЗОВАТЕЛЯ:")
    print("-" * 40)
    print("Привлечено: $28,390")
    print("Инвесторам выплачено: $32,713")
    
    print("\n3. ПОИСК ИСТОЧНИКА $28,390 (СОБРАНО):")
    print("-" * 40)
    
    # Проверяем различные колонки на предмет значения 28,390
    target_collected = 28390
    
    # Проверяем daily данные
    final_ggr = daily_df["cumulative_ggr"].iloc[-1]
    final_multiplier = daily_df["ggr_multiplier"].iloc[-1]
    calculated_pool_size = final_ggr / final_multiplier if final_multiplier > 0 else 50000
    
    print(f"Расчетный размер пула (final_ggr / multiplier): ${calculated_pool_size:,.2f}")
    
    # Проверяем monthly данные
    total_deposits = monthly_df["total_deposits"].sum()
    print(f"Сумма total_deposits: ${total_deposits:,.2f}")
    
    capital_cost_usd = monthly_df["capital_cost_usd"].sum()
    print(f"Сумма capital_cost_usd: ${capital_cost_usd:,.2f}")
    
    # Проверяем другие возможные источники
    monthly_ggr_sum = monthly_df["monthly_ggr"].sum()
    print(f"Сумма monthly_ggr: ${monthly_ggr_sum:,.2f}")
    
    traffic_spend = monthly_df["traffic_spend"].sum()
    print(f"Сумма traffic_spend: ${traffic_spend:,.2f}")
    
    print("\n4. ПОИСК ИСТОЧНИКА $22,233 (CASH ВЫПЛАТЫ):")
    print("-" * 40)
    
    # Проверяем выплаты
    stable_payout = monthly_df["stable_payout"].sum()
    growth_payout = monthly_df["growth_payout"].sum()
    total_cash_payouts = stable_payout + growth_payout
    
    print(f"Stable payouts: ${stable_payout:,.2f}")
    print(f"Growth payouts: ${growth_payout:,.2f}")
    print(f"Общие cash выплаты: ${total_cash_payouts:,.2f}")
    
    # Проверяем referral costs
    referral_cost = monthly_df["monthly_referral_cost"].sum()
    print(f"Referral costs: ${referral_cost:,.2f}")
    
    print("\n5. ПОИСК ИСТОЧНИКА $32,713 (ВЫПЛАЧЕНО ИНВЕСТОРАМ):")
    print("-" * 40)
    
    # Различные комбинации
    cash_plus_referrals = total_cash_payouts + referral_cost
    print(f"Cash выплаты + Referrals: ${cash_plus_referrals:,.2f}")
    
    # Проверяем tiers данные
    print(f"\nПроверяем tiers данные:")
    print(f"Колонки в tiers: {list(tiers_df.columns)}")
    
    # Ищем все колонки с 'payout' в названии
    payout_columns = [col for col in tiers_df.columns if 'payout' in col.lower()]
    print(f"Колонки с 'payout': {payout_columns}")
    
    for col in payout_columns:
        total_val = tiers_df[col].sum()
        print(f"  {col}: ${total_val:,.2f}")
        
        # Проверяем, близко ли к искомым значениям
        if abs(total_val - 22233) < 100:
            print(f"    *** НАЙДЕНО! Близко к $22,233")
        if abs(total_val - 32713) < 100:
            print(f"    *** НАЙДЕНО! Близко к $32,713")
    
    print("\n6. ПРОВЕРКА РАСЧЕТА СТОИМОСТИ КАПИТАЛА:")
    print("-" * 40)
    
    # Если собрано $28,390 и выплачено $22,233
    if target_collected > 0:
        cost_of_capital_dashboard = (22233 / target_collected) * 100
        print(f"Стоимость капитала (22233 / 28390): {cost_of_capital_dashboard:.1f}%")
    
    # Если выплачено $32,713
    if target_collected > 0:
        cost_of_capital_user = (32713 / target_collected) * 100
        print(f"Стоимость капитала (32713 / 28390): {cost_of_capital_user:.1f}%")
    
    print("\n7. ДЕТАЛЬНЫЙ АНАЛИЗ MONTHLY ДАННЫХ:")
    print("-" * 40)
    
    print("Все колонки в monthly данных:")
    for col in monthly_df.columns:
        if monthly_df[col].dtype in ['int64', 'float64']:
            total_val = monthly_df[col].sum()
            print(f"  {col}: ${total_val:,.2f}")
            
            # Проверяем близость к искомым значениям
            if abs(total_val - 28390) < 100:
                print(f"    *** НАЙДЕНО! Близко к $28,390 (собрано)")
            if abs(total_val - 22233) < 100:
                print(f"    *** НАЙДЕНО! Близко к $22,233 (cash выплаты)")
            if abs(total_val - 32713) < 100:
                print(f"    *** НАЙДЕНО! Близко к $32,713 (выплачено инвесторам)")
    
    print("\n8. АНАЛИЗ DAILY ДАННЫХ:")
    print("-" * 40)
    
    print("Финальные значения из daily данных:")
    for col in daily_df.columns:
        if daily_df[col].dtype in ['int64', 'float64']:
            final_val = daily_df[col].iloc[-1]
            print(f"  {col} (финальное): ${final_val:,.2f}")
            
            # Проверяем близость к искомым значениям
            if abs(final_val - 28390) < 100:
                print(f"    *** НАЙДЕНО! Близко к $28,390 (собрано)")
    
    print("\n" + "=" * 80)
    print("ЗАКЛЮЧЕНИЕ:")
    print("Ищем точные источники цифр $28,390, $22,233 и $32,713 в CSV данных")
    print("=" * 80)

if __name__ == "__main__":
    main()