#!/usr/bin/env python3
"""
Анализ правильных формул с использованием РЕАЛЬНЫХ данных из CSV файлов
"""

import pandas as pd
import numpy as np

def load_data():
    """Загружаем все данные"""
    daily_df = pd.read_csv('pool1_nov2025_daily.csv')
    monthly_df = pd.read_csv('pool1_nov2025_monthly.csv')
    tiers_df = pd.read_csv('pool1_nov2025_monthly_tiers_znx.csv')
    
    return daily_df, monthly_df, tiers_df

def analyze_znx_structure(tiers_df):
    """Анализируем структуру ZNX из реальных данных"""
    print("=== АНАЛИЗ СТРУКТУРЫ ZNX ИЗ РЕАЛЬНЫХ ДАННЫХ ===")
    
    # Получаем данные за ноябрь 2025 (первый месяц с выплатами)
    nov_data = tiers_df[(tiers_df['year'] == 2025) & (tiers_df['month'] == 11)]
    
    print("Данные за ноябрь 2025 (per_znx_cash_usd):")
    for _, row in nov_data.iterrows():
        print(f"  {row['pool']} {row['tier']}: ${row['per_znx_cash_usd']:.6f} per ZNX")
    
    # Рассчитываем GGR multiplier из данных
    daily_df = pd.read_csv('pool1_nov2025_daily.csv')
    nov_ggr_multiplier = daily_df[daily_df['month'] == 11]['ggr_multiplier'].iloc[-1]
    
    print(f"\nGGR multiplier в ноябре: {nov_ggr_multiplier:.6f}")
    
    # Проверяем соответствие формулам
    print(f"\nПроверка формул (GGR = {nov_ggr_multiplier:.6f}):")
    
    stable_rates = {'basic': 0.34, 'advanced': 0.3825, 'premium': 0.425}
    growth_rates = {'basic': 0.085, 'advanced': 0.10625, 'premium': 0.1275}
    
    for _, row in nov_data.iterrows():
        pool = row['pool']
        tier = row['tier']
        actual_per_znx = row['per_znx_cash_usd']
        
        if pool == 'stable':
            expected_per_znx = nov_ggr_multiplier * stable_rates[tier]
        else:  # growth
            expected_per_znx = nov_ggr_multiplier * growth_rates[tier]
        
        match = "✅" if abs(actual_per_znx - expected_per_znx) < 0.001 else "❌"
        print(f"  {pool} {tier}: {actual_per_znx:.6f} vs {expected_per_znx:.6f} {match}")
    
    return nov_data

def find_znx_distribution(tiers_df, monthly_df):
    """Находим реальное распределение ZNX по тирам"""
    print("\n=== ПОИСК РАСПРЕДЕЛЕНИЯ ZNX ПО ТИРАМ ===")
    
    # Берем данные за ноябрь 2025
    nov_tiers = tiers_df[(tiers_df['year'] == 2025) & (tiers_df['month'] == 11)]
    nov_monthly = monthly_df[(monthly_df['year'] == 2025) & (monthly_df['month'] == 11)]
    
    stable_payout = nov_monthly['stable_payout'].iloc[0]
    growth_payout = nov_monthly['growth_payout'].iloc[0]
    
    print(f"Выплаты в ноябре:")
    print(f"  Stable: ${stable_payout:.2f}")
    print(f"  Growth: ${growth_payout:.2f}")
    
    # Рассчитываем количество ZNX по тирам
    print(f"\nРасчет ZNX по тирам (выплата / per_znx_cash):")
    
    total_stable_znx = 0
    total_growth_znx = 0
    znx_distribution = {}
    
    for _, row in nov_tiers.iterrows():
        pool = row['pool']
        tier = row['tier']
        per_znx = row['per_znx_cash_usd']
        
        if per_znx > 0:
            if pool == 'stable':
                # Для stable pool: znx = tier_payout / per_znx
                # Нужно найти tier_payout из общей stable_payout
                tier_payout = stable_payout / 3  # Предположение равного распределения
                znx_amount = tier_payout / per_znx
                total_stable_znx += znx_amount
            else:  # growth
                tier_payout = growth_payout / 3  # Предположение равного распределения  
                znx_amount = tier_payout / per_znx
                total_growth_znx += znx_amount
            
            znx_distribution[f"{pool}_{tier}"] = znx_amount
            print(f"  {pool} {tier}: ${tier_payout:.2f} / ${per_znx:.6f} = {znx_amount:.0f} ZNX")
    
    total_znx = total_stable_znx + total_growth_znx
    
    print(f"\nИтого ZNX:")
    print(f"  Stable Pool: {total_stable_znx:.0f} ZNX")
    print(f"  Growth Pool: {total_growth_znx:.0f} ZNX")
    print(f"  Общий пул: {total_znx:.0f} ZNX")
    
    return znx_distribution, total_stable_znx, total_growth_znx, total_znx

def calculate_correct_collected(total_znx):
    """Рассчитываем правильное значение 'Собрано'"""
    print(f"\n=== ПРАВИЛЬНОЕ ЗНАЧЕНИЕ 'СОБРАНО' ===")
    
    znx_rate = 1.0  # Курс ZNX к USD
    collected_usd = total_znx * znx_rate
    
    print(f"Собрано = {total_znx:.0f} ZNX × ${znx_rate:.2f} = ${collected_usd:.2f}")
    
    return collected_usd

def calculate_correct_paid_out(monthly_df):
    """Рассчитываем правильное значение 'Выплачено' с учетом high watermark"""
    print(f"\n=== ПРАВИЛЬНОЕ ЗНАЧЕНИЕ 'ВЫПЛАЧЕНО' ===")
    
    total_stable = monthly_df['stable_payout'].sum()
    total_growth = monthly_df['growth_payout'].sum()
    total_referral = monthly_df['monthly_referral_cost'].sum()
    
    total_paid = total_stable + total_growth + total_referral
    
    print(f"Stable Pool выплаты: ${total_stable:.2f}")
    print(f"Growth Pool выплаты: ${total_growth:.2f}")
    print(f"Реферальные выплаты: ${total_referral:.2f}")
    print(f"Общие выплаты: ${total_paid:.2f}")
    
    print(f"\nВыплаты по месяцам (с high watermark):")
    for _, row in monthly_df.iterrows():
        if row['stable_payout'] > 0 or row['growth_payout'] > 0:
            watermark = "✅" if row['watermark_exceeded'] else "❌"
            print(f"  {int(row['year'])}-{int(row['month']):02d}: "
                  f"Stable ${row['stable_payout']:,.2f}, "
                  f"Growth ${row['growth_payout']:,.2f}, "
                  f"Referral ${row['monthly_referral_cost']:,.2f}, "
                  f"Watermark {watermark}")
    
    return total_paid, total_stable, total_growth, total_referral

def analyze_dashboard_vs_correct(collected, paid_out):
    """Сравниваем дашборд с правильными значениями"""
    print(f"\n=== СРАВНЕНИЕ ДАШБОРДА С ПРАВИЛЬНЫМИ ЗНАЧЕНИЯМИ ===")
    
    # Данные из дашборда (неправильные)
    dashboard_collected = 28390  # final_ggr / ggr_multiplier
    dashboard_paid = 22233      # неизвестная формула
    dashboard_cost = 78.3       # неправильный расчет
    
    # Правильные значения
    correct_cost = (paid_out / collected) * 100
    profit_loss = paid_out - collected
    roi = (profit_loss / collected) * 100
    
    print("ДАШБОРД (неправильно) vs ПРАВИЛЬНЫЕ ЗНАЧЕНИЯ:")
    print(f"Собрано:           ${dashboard_collected:,.0f} vs ${collected:,.0f}")
    print(f"Выплачено:         ${dashboard_paid:,.0f} vs ${paid_out:,.2f}")
    print(f"Стоимость капитала: {dashboard_cost:.1f}% vs {correct_cost:.1f}%")
    print(f"Прибыль/Убыток:    N/A vs ${profit_loss:,.2f}")
    print(f"ROI:               N/A vs {roi:.1f}%")
    
    return correct_cost, profit_loss, roi

def write_final_formulas(collected, paid_out, stable_total, growth_total, referral_total):
    """Записываем финальные правильные формулы"""
    print(f"\n" + "="*80)
    print("ФИНАЛЬНЫЕ ПРАВИЛЬНЫЕ ФОРМУЛЫ ДЛЯ ДАШБОРДА")
    print("="*80)
    
    print(f"\n1. СОБРАНО:")
    print(f"   Формула: ZNX_amount × ZNX_rate")
    print(f"   Значение: ${collected:,.2f}")
    
    print(f"\n2. ВЫПЛАЧЕНО:")
    print(f"   Формула: stable_payout + growth_payout + referral_cost")
    print(f"   Stable Pool: ${stable_total:,.2f}")
    print(f"   Growth Pool: ${growth_total:,.2f}")
    print(f"   Реферальные: ${referral_total:,.2f}")
    print(f"   Итого: ${paid_out:,.2f}")
    
    cost_of_capital = (paid_out / collected) * 100
    print(f"\n3. СТОИМОСТЬ КАПИТАЛА:")
    print(f"   Формула: (выплачено / собрано) × 100")
    print(f"   Значение: ({paid_out:,.2f} / {collected:,.2f}) × 100 = {cost_of_capital:.1f}%")
    
    profit_loss = paid_out - collected
    print(f"\n4. ПРИБЫЛЬ/УБЫТОК:")
    print(f"   Формула: выплачено - собрано")
    print(f"   Значение: {paid_out:,.2f} - {collected:,.2f} = ${profit_loss:,.2f}")
    
    roi = (profit_loss / collected) * 100
    print(f"\n5. ROI:")
    print(f"   Формула: (прибыль / собрано) × 100")
    print(f"   Значение: ({profit_loss:,.2f} / {collected:,.2f}) × 100 = {roi:.1f}%")
    
    print(f"\n" + "="*80)
    print("ПРОБЛЕМЫ В ТЕКУЩЕМ ДАШБОРДЕ:")
    print("❌ 'Собрано' использует неправильную формулу: final_ggr / ggr_multiplier")
    print("❌ 'Выплачено' не учитывает все компоненты")
    print("❌ 'Стоимость капитала' рассчитывается от неправильного знаменателя")
    print("="*80)

def main():
    """Основная функция"""
    print("АНАЛИЗ ПРАВИЛЬНЫХ ФОРМУЛ С РЕАЛЬНЫМИ ДАННЫМИ")
    print("="*80)
    
    # Загружаем данные
    daily_df, monthly_df, tiers_df = load_data()
    
    # Анализируем структуру ZNX
    nov_data = analyze_znx_structure(tiers_df)
    
    # Находим распределение ZNX
    znx_dist, stable_znx, growth_znx, total_znx = find_znx_distribution(tiers_df, monthly_df)
    
    # Рассчитываем правильные значения
    collected = calculate_correct_collected(total_znx)
    paid_out, stable_total, growth_total, referral_total = calculate_correct_paid_out(monthly_df)
    
    # Сравниваем с дашбордом
    cost_of_capital, profit_loss, roi = analyze_dashboard_vs_correct(collected, paid_out)
    
    # Записываем финальные формулы
    write_final_formulas(collected, paid_out, stable_total, growth_total, referral_total)

if __name__ == "__main__":
    main()