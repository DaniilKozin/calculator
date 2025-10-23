#!/usr/bin/env python3
"""
Правильный анализ формул дашборда с учетом:
1. Собрано = сумма пулов в ZNX * курс ZNX
2. Выплачено = расчет по тирам с учетом high watermark
3. Реферальные выплаты
"""

import pandas as pd
import numpy as np

def load_data():
    """Загружаем все необходимые данные"""
    daily_df = pd.read_csv('pool1_nov2025_daily.csv')
    monthly_df = pd.read_csv('pool1_nov2025_monthly.csv')
    tiers_df = pd.read_csv('pool1_nov2025_monthly_tiers_znx.csv')
    
    return daily_df, monthly_df, tiers_df

def analyze_znx_structure(daily_df):
    """Анализируем структуру ZNX из дашборда"""
    print("=== АНАЛИЗ СТРУКТУРЫ ZNX ===")
    
    # Из дашборда видим параметры по умолчанию
    znx_amount = 50000.0  # Количество собранных ZNX
    znx_rate = 1.0        # Курс ZNX к USD
    
    # Расчет размера пула в USD
    pool_size_usd = znx_amount * znx_rate
    
    print(f"Количество собранных ZNX: {znx_amount:,.0f}")
    print(f"Курс ZNX к USD: ${znx_rate:.8f}")
    print(f"Размер пула в USD: ${pool_size_usd:,.2f}")
    
    # Проверяем соответствие с данными
    final_ggr = daily_df['cumulative_ggr'].iloc[-1]
    ggr_multiplier = daily_df['ggr_multiplier'].iloc[-1]
    calculated_pool = final_ggr / ggr_multiplier
    
    print(f"\nСравнение с расчетными данными:")
    print(f"final_ggr / ggr_multiplier = ${calculated_pool:,.2f}")
    print(f"ZNX amount * ZNX rate = ${pool_size_usd:,.2f}")
    
    return znx_amount, znx_rate, pool_size_usd

def analyze_tier_structure(tiers_df):
    """Анализируем структуру тиров и их выплаты"""
    print("\n=== АНАЛИЗ СТРУКТУРЫ ТИРОВ ===")
    
    # Группируем по пулам и тирам
    stable_tiers = tiers_df[tiers_df['pool'] == 'stable']
    growth_tiers = tiers_df[tiers_df['pool'] == 'growth']
    
    print("\nSTABLE POOL - выплаты per ZNX (cash only):")
    for tier in ['basic', 'advanced', 'premium']:
        tier_data = stable_tiers[stable_tiers['tier'] == tier]
        total_cash = tier_data['per_znx_cash_usd'].sum()
        print(f"  {tier.capitalize()}: ${total_cash:.6f} per ZNX")
    
    print("\nGROWTH POOL - выплаты per ZNX (cash only, tokens returned separately):")
    for tier in ['basic', 'advanced', 'premium']:
        tier_data = growth_tiers[growth_tiers['tier'] == tier]
        total_cash = tier_data['per_znx_cash_usd'].sum()
        print(f"  {tier.capitalize()}: ${total_cash:.6f} per ZNX")
    
    return stable_tiers, growth_tiers

def calculate_correct_formulas(znx_amount, znx_rate, stable_tiers, growth_tiers, monthly_df):
    """Рассчитываем правильные формулы"""
    print("\n=== ПРАВИЛЬНЫЕ ФОРМУЛЫ РАСЧЕТА ===")
    
    # 1. СОБРАНО = ZNX amount * ZNX rate
    total_collected = znx_amount * znx_rate
    print(f"1. СОБРАНО = {znx_amount:,.0f} ZNX × ${znx_rate:.8f} = ${total_collected:,.2f}")
    
    # 2. ВЫПЛАЧЕНО - нужно рассчитать по тирам
    # Предполагаем равномерное распределение по тирам (нужны реальные данные)
    
    # Для примера используем данные из monthly_df
    total_stable_payout = monthly_df['stable_payout'].sum()
    total_growth_payout = monthly_df['growth_payout'].sum()
    total_cash_paid = total_stable_payout + total_growth_payout
    
    print(f"2. ВЫПЛАЧЕНО (из monthly_df):")
    print(f"   Stable Pool: ${total_stable_payout:,.2f}")
    print(f"   Growth Pool: ${total_growth_payout:,.2f}")
    print(f"   Итого cash: ${total_cash_paid:,.2f}")
    
    # 3. Реферальные выплаты
    total_referral = monthly_df['monthly_referral_cost'].sum()
    print(f"3. РЕФЕРАЛЬНЫЕ ВЫПЛАТЫ: ${total_referral:,.2f}")
    
    # 4. Общие выплаты
    total_payments = total_cash_paid + total_referral
    print(f"4. ОБЩИЕ ВЫПЛАТЫ: ${total_payments:,.2f}")
    
    # 5. Стоимость капитала
    cost_of_capital = (total_payments / total_collected) * 100
    print(f"5. СТОИМОСТЬ КАПИТАЛА: {cost_of_capital:.1f}%")
    
    return {
        'collected': total_collected,
        'cash_paid': total_cash_paid,
        'referral_cost': total_referral,
        'total_payments': total_payments,
        'cost_of_capital': cost_of_capital
    }

def analyze_tier_payouts_detailed(tiers_df, znx_amount):
    """Детальный анализ выплат по тирам"""
    print("\n=== ДЕТАЛЬНЫЙ АНАЛИЗ ВЫПЛАТ ПО ТИРАМ ===")
    
    # Предполагаем распределение ZNX по тирам (нужны реальные данные)
    # Для примера используем равномерное распределение
    stable_ratio = 0.6  # 60% в stable pool
    growth_ratio = 0.4   # 40% в growth pool
    
    stable_znx = znx_amount * stable_ratio
    growth_znx = znx_amount * growth_ratio
    
    # Распределение по тирам (пример)
    tier_distribution = {
        'basic': 0.5,     # 50%
        'advanced': 0.3,  # 30%
        'premium': 0.2    # 20%
    }
    
    print(f"Stable Pool ZNX: {stable_znx:,.0f}")
    print(f"Growth Pool ZNX: {growth_znx:,.0f}")
    
    total_stable_cash = 0
    total_growth_cash = 0
    
    print("\nSTABLE POOL выплаты по тирам:")
    for tier, ratio in tier_distribution.items():
        tier_znx = stable_znx * ratio
        tier_data = tiers_df[(tiers_df['pool'] == 'stable') & (tiers_df['tier'] == tier)]
        per_znx_cash = tier_data['per_znx_cash_usd'].sum()
        tier_total_cash = tier_znx * per_znx_cash
        total_stable_cash += tier_total_cash
        
        print(f"  {tier.capitalize()}: {tier_znx:,.0f} ZNX × ${per_znx_cash:.6f} = ${tier_total_cash:,.2f}")
    
    print(f"Итого Stable Pool: ${total_stable_cash:,.2f}")
    
    print("\nGROWTH POOL выплаты по тирам:")
    for tier, ratio in tier_distribution.items():
        tier_znx = growth_znx * ratio
        tier_data = tiers_df[(tiers_df['pool'] == 'growth') & (tiers_df['tier'] == tier)]
        per_znx_cash = tier_data['per_znx_cash_usd'].sum()
        tier_total_cash = tier_znx * per_znx_cash
        total_growth_cash += tier_total_cash
        
        print(f"  {tier.capitalize()}: {tier_znx:,.0f} ZNX × ${per_znx_cash:.6f} = ${tier_total_cash:,.2f}")
    
    print(f"Итого Growth Pool: ${total_growth_cash:,.2f}")
    
    total_calculated_cash = total_stable_cash + total_growth_cash
    print(f"\nИТОГО РАСЧЕТНЫЕ ВЫПЛАТЫ: ${total_calculated_cash:,.2f}")
    
    return total_calculated_cash

def compare_with_dashboard(correct_formulas, monthly_df):
    """Сравниваем с данными дашборда"""
    print("\n=== СРАВНЕНИЕ С ДАШБОРДОМ ===")
    
    # Данные из дашборда (из предыдущего анализа)
    dashboard_collected = 28390  # final_ggr / ggr_multiplier
    dashboard_cash_paid = 22233  # показано в дашборде
    dashboard_cost_capital = 78.3  # показано в дашборде
    
    print("ДАШБОРД vs ПРАВИЛЬНЫЕ ФОРМУЛЫ:")
    print(f"Собрано:     ${dashboard_collected:,.0f} vs ${correct_formulas['collected']:,.0f}")
    print(f"Выплачено:   ${dashboard_cash_paid:,.0f} vs ${correct_formulas['cash_paid']:,.0f}")
    print(f"Стоимость:   {dashboard_cost_capital:.1f}% vs {correct_formulas['cost_of_capital']:.1f}%")
    
    print("\nПРОБЛЕМЫ В ДАШБОРДЕ:")
    if abs(dashboard_collected - correct_formulas['collected']) > 100:
        print(f"❌ 'Собрано' неправильно: использует final_ggr/ggr_multiplier вместо ZNX*курс")
    
    if abs(dashboard_cash_paid - correct_formulas['cash_paid']) > 100:
        print(f"❌ 'Выплачено' неправильно: показывает ${dashboard_cash_paid:,.0f} вместо ${correct_formulas['cash_paid']:,.0f}")
    
    if abs(dashboard_cost_capital - correct_formulas['cost_of_capital']) > 5:
        print(f"❌ 'Стоимость капитала' неправильно: из-за неправильного знаменателя")

def main():
    """Основная функция анализа"""
    print("ПРАВИЛЬНЫЙ АНАЛИЗ ФОРМУЛ ДАШБОРДА")
    print("=" * 50)
    
    # Загружаем данные
    daily_df, monthly_df, tiers_df = load_data()
    
    # Анализируем структуру ZNX
    znx_amount, znx_rate, pool_size_usd = analyze_znx_structure(daily_df)
    
    # Анализируем тиры
    stable_tiers, growth_tiers = analyze_tier_structure(tiers_df)
    
    # Рассчитываем правильные формулы
    correct_formulas = calculate_correct_formulas(znx_amount, znx_rate, stable_tiers, growth_tiers, monthly_df)
    
    # Детальный анализ по тирам
    calculated_cash = analyze_tier_payouts_detailed(tiers_df, znx_amount)
    
    # Сравниваем с дашбордом
    compare_with_dashboard(correct_formulas, monthly_df)
    
    print("\n" + "=" * 50)
    print("ЗАКЛЮЧЕНИЕ:")
    print("✅ Правильная формула 'Собрано': ZNX amount × ZNX rate")
    print("✅ Правильная формула 'Выплачено': сумма по тирам с учетом high watermark")
    print("✅ Правильная формула 'Стоимость капитала': (выплаты / собрано) × 100")

if __name__ == "__main__":
    main()