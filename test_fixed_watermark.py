#!/usr/bin/env python3

import sys
import pandas as pd
from revshare_pool import RevSharePoolGenerator

def test_high_watermark_logic():
    """Тест логики high watermark - выплаты должны быть только при росте GGR"""
    print("=== Тест исправленной логики High Watermark ===")
    
    # Создаем генератор с фиксированным seed для воспроизводимости
    generator = RevSharePoolGenerator(
        pool_size=35000,
        stable_znx_amount=60000,
        growth_znx_amount=40000,
        znx_amount=100000,  # Общее количество ZNX токенов
        znx_rate=1.5,
        seed=42,
        start_date="2025-11-01"
    )
    
    # Генерируем данные
    daily_data = generator.generate_daily_data()
    monthly_data = generator.get_monthly_summary(daily_data)
    
    print("Месячные данные:")
    print("Месяц | Cumulative GGR | Stable Payout | Growth Payout | Watermark Exceeded")
    print("-" * 80)
    
    for _, row in monthly_data.iterrows():
        print(f"{row['month']:2d}    | {row['cumulative_ggr']:13,.0f} | {row['stable_payout']:12,.0f} | {row['growth_payout']:12,.0f} | {row['watermark_exceeded']}")
    
    # Проверяем логику: выплаты должны быть только когда watermark_exceeded = True
    print("\n=== Проверка логики ===")
    for _, row in monthly_data.iterrows():
        if row['watermark_exceeded']:
            if row['stable_payout'] > 0 or row['growth_payout'] > 0:
                print(f"✅ Месяц {row['month']}: Watermark превышен, есть выплаты")
            else:
                print(f"❌ Месяц {row['month']}: Watermark превышен, но нет выплат!")
        else:
            if row['stable_payout'] == 0 and row['growth_payout'] == 0:
                print(f"✅ Месяц {row['month']}: Watermark не превышен, выплат нет")
            else:
                print(f"❌ Месяц {row['month']}: Watermark не превышен, но есть выплаты!")
    
    # Проверяем дневные данные - выплаты должны быть только в месяцы с превышением watermark
    print("\n=== Проверка дневных выплат ===")
    
    # Группируем по месяцам и проверяем
    for month in range(11, 13):  # Ноябрь и декабрь
        month_daily = daily_data[daily_data['month'] == month]
        month_summary = monthly_data[monthly_data['month'] == month]
        
        if len(month_summary) > 0:
            watermark_exceeded = month_summary.iloc[0]['watermark_exceeded']
            monthly_stable = month_summary.iloc[0]['stable_payout']
            monthly_growth = month_summary.iloc[0]['growth_payout']
            
            daily_stable_sum = month_daily['stable_payout'].sum()
            daily_growth_sum = month_daily['growth_payout'].sum()
            
            print(f"\nМесяц {month}:")
            print(f"  Watermark превышен: {watermark_exceeded}")
            print(f"  Месячная stable выплата: {monthly_stable:,.2f}")
            print(f"  Сумма дневных stable выплат: {daily_stable_sum:,.2f}")
            print(f"  Месячная growth выплата: {monthly_growth:,.2f}")
            print(f"  Сумма дневных growth выплат: {daily_growth_sum:,.2f}")
            
            # Проверяем соответствие
            if abs(monthly_stable - daily_stable_sum) < 0.01 and abs(monthly_growth - daily_growth_sum) < 0.01:
                print(f"  ✅ Дневные выплаты соответствуют месячным")
            else:
                print(f"  ❌ Дневные выплаты НЕ соответствуют месячным!")
            
            # Проверяем, что выплаты только в дни с положительным GGR
            negative_ggr_days = month_daily[month_daily['daily_ggr'] < 0]
            negative_days_with_payouts = negative_ggr_days[
                (negative_ggr_days['stable_payout'] > 0) | 
                (negative_ggr_days['growth_payout'] > 0)
            ]
            
            if len(negative_days_with_payouts) == 0:
                print(f"  ✅ Нет выплат в дни с отрицательным GGR")
            else:
                print(f"  ❌ Есть выплаты в дни с отрицательным GGR: {len(negative_days_with_payouts)} дней")

def test_no_payouts_when_ggr_flat():
    """Тест: нет выплат когда GGR не растет"""
    print("\n=== Тест: нет выплат при плоском GGR ===")
    
    # Создаем генератор с очень низкой волатильностью для более предсказуемого GGR
    generator = RevSharePoolGenerator(
        pool_size=35000,
        stable_znx_amount=60000,
        growth_znx_amount=40000,
        znx_amount=100000,  # Общее количество ZNX токенов
        znx_rate=1.5,
        ggr_volatility=0.05,  # Очень низкая волатильность
        seed=123,
        start_date="2025-11-01"
    )
    
    monthly_data = generator.get_monthly_summary()
    
    # Ищем месяцы где GGR не растет
    prev_ggr = 0
    for _, row in monthly_data.iterrows():
        current_ggr = row['cumulative_ggr']
        if current_ggr <= prev_ggr:
            # GGR не вырос
            if row['stable_payout'] == 0 and row['growth_payout'] == 0:
                print(f"✅ Месяц {row['month']}: GGR не вырос ({current_ggr:.0f} <= {prev_ggr:.0f}), выплат нет")
            else:
                print(f"❌ Месяц {row['month']}: GGR не вырос ({current_ggr:.0f} <= {prev_ggr:.0f}), но есть выплаты!")
        else:
            # GGR вырос
            if row['stable_payout'] > 0 or row['growth_payout'] > 0:
                print(f"✅ Месяц {row['month']}: GGR вырос ({prev_ggr:.0f} -> {current_ggr:.0f}), есть выплаты")
            else:
                print(f"⚠️  Месяц {row['month']}: GGR вырос ({prev_ggr:.0f} -> {current_ggr:.0f}), но выплат нет")
        
        prev_ggr = current_ggr

if __name__ == "__main__":
    test_high_watermark_logic()
    test_no_payouts_when_ggr_flat()
    print("\n=== Тестирование завершено ===")