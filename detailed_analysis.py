#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def analyze_pool_data():
    """
    Детальный анализ данных пула для выявления расхождений в расчетах
    """
    
    print("=== ДЕТАЛЬНЫЙ АНАЛИЗ ДАННЫХ ПУЛА ===\n")
    
    # Загружаем данные
    try:
        monthly_df = pd.read_csv('pool1_nov2025_monthly.csv')
        daily_df = pd.read_csv('pool1_nov2025_daily.csv')
        tiers_df = pd.read_csv('pool1_nov2025_monthly_tiers_znx.csv')
        print("✓ Все CSV файлы успешно загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки файлов: {e}")
        return
    
    print(f"📊 Количество записей:")
    print(f"   - Месячные данные: {len(monthly_df)} строк")
    print(f"   - Дневные данные: {len(daily_df)} строк") 
    print(f"   - Данные по уровням: {len(tiers_df)} строк\n")
    
    # === АНАЛИЗ МЕСЯЧНЫХ ДАННЫХ ===
    print("=== АНАЛИЗ МЕСЯЧНЫХ ДАННЫХ ===")
    
    # Основные суммы из месячных данных
    total_stable_payout = monthly_df['stable_payout'].sum()
    total_growth_payout = monthly_df['growth_payout'].sum()
    total_cash_paid = total_stable_payout + total_growth_payout
    total_referral_cost = monthly_df['monthly_referral_cost'].sum()
    total_capital_cost = monthly_df['capital_cost_usd'].sum()
    final_ggr = monthly_df['cumulative_ggr'].iloc[-1]
    
    print(f"💰 Выплаты:")
    print(f"   - Stable выплаты: ${total_stable_payout:,.2f}")
    print(f"   - Growth выплаты: ${total_growth_payout:,.2f}")
    print(f"   - Общие cash выплаты: ${total_cash_paid:,.2f}")
    print(f"   - Реферальные расходы: ${total_referral_cost:,.2f}")
    print(f"   - Капитальные затраты: ${total_capital_cost:,.2f}")
    print(f"   - Итоговый GGR: ${final_ggr:,.2f}\n")
    
    # === АНАЛИЗ ДНЕВНЫХ ДАННЫХ ===
    print("=== АНАЛИЗ ДНЕВНЫХ ДАННЫХ ===")
    
    final_ggr_daily = daily_df['cumulative_ggr'].iloc[-1]
    final_multiplier = daily_df['ggr_multiplier'].iloc[-1]
    
    print(f"📈 Финальные значения из дневных данных:")
    print(f"   - Итоговый GGR: ${final_ggr_daily:,.2f}")
    print(f"   - GGR множитель: {final_multiplier:.2f}x\n")
    
    # === РАСЧЕТЫ ДАШБОРДА ===
    print("=== РАСЧЕТЫ КАК В ДАШБОРДЕ ===")
    
    # Расчет real_pool_size как в дашборде
    if final_multiplier > 0:
        dashboard_real_pool_size = final_ggr_daily / final_multiplier
    else:
        dashboard_real_pool_size = 50000  # DEFAULT_POOL_SIZE
    
    # Расчет стоимости капитала как в дашборде
    dashboard_cost_of_capital = (total_cash_paid / dashboard_real_pool_size) * 100
    
    print(f"🎯 Расчеты дашборда:")
    print(f"   - Real Pool Size: ${dashboard_real_pool_size:,.2f}")
    print(f"   - Cost of Capital: {dashboard_cost_of_capital:.1f}%")
    print(f"   - Формула: (${total_cash_paid:,.2f} / ${dashboard_real_pool_size:,.2f}) * 100\n")
    
    # === АЛЬТЕРНАТИВНЫЕ РАСЧЕТЫ ===
    print("=== АЛЬТЕРНАТИВНЫЕ РАСЧЕТЫ ===")
    
    # Расчет на основе капитальных затрат
    capital_cost_of_capital = (total_cash_paid / total_capital_cost) * 100
    
    print(f"💡 Расчет на основе капитальных затрат:")
    print(f"   - Собранный капитал: ${total_capital_cost:,.2f}")
    print(f"   - Cost of Capital: {capital_cost_of_capital:.1f}%")
    print(f"   - Формула: (${total_cash_paid:,.2f} / ${total_capital_cost:,.2f}) * 100\n")
    
    # === АНАЛИЗ ДАННЫХ ПО УРОВНЯМ ===
    print("=== АНАЛИЗ ДАННЫХ ПО УРОВНЯМ ===")
    
    if not tiers_df.empty:
        print(f"📋 Структура данных по уровням:")
        print(f"   - Колонки: {list(tiers_df.columns)}")
        
        # Проверяем есть ли данные о выплатах в tiers
        payout_columns = [col for col in tiers_df.columns if 'payout' in col.lower() or 'paid' in col.lower()]
        if payout_columns:
            print(f"   - Колонки с выплатами: {payout_columns}")
            
            for col in payout_columns:
                if col in tiers_df.columns:
                    total_tier_payout = tiers_df[col].sum()
                    print(f"   - Сумма {col}: ${total_tier_payout:,.2f}")
        
        # Показываем первые несколько строк
        print(f"\n📊 Первые 3 строки данных по уровням:")
        print(tiers_df.head(3).to_string())
        print(f"\n📊 Последние 3 строки данных по уровням:")
        print(tiers_df.tail(3).to_string())
    
    print("\n" + "="*60)
    
    # === СРАВНЕНИЕ С ДАШБОРДОМ ===
    print("=== СРАВНЕНИЕ С ДАШБОРДОМ ===")
    
    dashboard_values = {
        'Собрано': 28390,
        'Cash выплаты': 22233,
        'Стоимость капитала': 78.3
    }
    
    print(f"📊 Значения из дашборда:")
    for key, value in dashboard_values.items():
        if key == 'Стоимость капитала':
            print(f"   - {key}: {value}%")
        else:
            print(f"   - {key}: ${value:,}")
    
    print(f"\n🔍 Сравнение:")
    print(f"   - Собрано: Дашборд ${dashboard_values['Собрано']:,} vs Капитальные затраты ${total_capital_cost:,.0f}")
    print(f"   - Cash выплаты: Дашборд ${dashboard_values['Cash выплаты']:,} vs Расчет ${total_cash_paid:,.0f}")
    print(f"   - Стоимость капитала: Дашборд {dashboard_values['Стоимость капитала']}% vs Расчет {capital_cost_of_capital:.1f}%")
    
    # === ПОИСК ИСТОЧНИКА 32K ===
    print(f"\n=== ПОИСК ИСТОЧНИКА 32K ВЫПЛАТ ===")
    
    # Проверяем все возможные суммы
    possible_totals = []
    
    # Сумма всех выплат + реферальные
    total_with_referral = total_cash_paid + total_referral_cost
    possible_totals.append(('Cash выплаты + Реферальные', total_with_referral))
    
    # Проверяем есть ли другие колонки с выплатами
    for col in monthly_df.columns:
        if 'payout' in col.lower() or 'cost' in col.lower() or 'paid' in col.lower():
            if col not in ['stable_payout', 'growth_payout', 'monthly_referral_cost', 'capital_cost_usd']:
                col_sum = monthly_df[col].sum()
                if col_sum > 0:
                    possible_totals.append((f'Сумма {col}', col_sum))
    
    # Проверяем данные по уровням
    if not tiers_df.empty:
        for col in tiers_df.columns:
            if 'payout' in col.lower() or 'paid' in col.lower():
                col_sum = tiers_df[col].sum()
                if col_sum > 0:
                    possible_totals.append((f'Tiers {col}', col_sum))
    
    print(f"🔎 Возможные источники 32k:")
    for name, value in possible_totals:
        print(f"   - {name}: ${value:,.2f}")
        if 30000 <= value <= 35000:
            print(f"     ⭐ ВОЗМОЖНЫЙ ИСТОЧНИК 32K!")
    
    print(f"\n" + "="*60)
    print("АНАЛИЗ ЗАВЕРШЕН")

if __name__ == "__main__":
    analyze_pool_data()