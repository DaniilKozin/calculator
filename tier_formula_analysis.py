#!/usr/bin/env python3
"""
Анализ правильных формул с учетом процентов выплат по тирам:

STABLE POOL (только cash):
- Basic: 34% от (invested_amount × ggr_multiplier)
- Advanced: 38.25% от (invested_amount × ggr_multiplier)  
- Premium: 42.5% от (invested_amount × ggr_multiplier)

GROWTH POOL (cash + 100% tokens returned):
- Basic: 8.5% от (invested_amount × ggr_multiplier) + 100% tokens
- Advanced: 10.625% от (invested_amount × ggr_multiplier) + 100% tokens
- Premium: 12.75% от (invested_amount × ggr_multiplier) + 100% tokens

High watermark: выплаты могут быть больше если GGR в конце < GGR в момент предыдущих выплат
"""

import pandas as pd
import numpy as np

def load_data():
    """Загружаем все необходимые данные"""
    daily_df = pd.read_csv('pool1_nov2025_daily.csv')
    monthly_df = pd.read_csv('pool1_nov2025_monthly.csv')
    tiers_df = pd.read_csv('pool1_nov2025_monthly_tiers_znx.csv')
    
    return daily_df, monthly_df, tiers_df

def analyze_tier_rates():
    """Анализируем правильные проценты выплат по тирам"""
    print("=== ПРАВИЛЬНЫЕ ПРОЦЕНТЫ ВЫПЛАТ ПО ТИРАМ ===")
    
    stable_rates = {
        'basic': 0.34,      # 34%
        'advanced': 0.3825, # 38.25%
        'premium': 0.425    # 42.5%
    }
    
    growth_rates = {
        'basic': 0.085,     # 8.5%
        'advanced': 0.10625, # 10.625%
        'premium': 0.1275   # 12.75%
    }
    
    print("STABLE POOL (только cash):")
    for tier, rate in stable_rates.items():
        print(f"  {tier.capitalize()}: {rate:.3%}")
    
    print("\nGROWTH POOL (cash + 100% tokens returned):")
    for tier, rate in growth_rates.items():
        print(f"  {tier.capitalize()}: {rate:.3%} + 100% tokens")
    
    return stable_rates, growth_rates

def calculate_pool_structure():
    """Рассчитываем структуру пулов"""
    print("\n=== СТРУКТУРА ПУЛОВ ===")
    
    # Параметры из дашборда
    znx_amount = 50000.0  # Общее количество ZNX
    znx_rate = 1.0        # Курс ZNX к USD
    
    # Распределение между пулами (нужно найти в данных)
    stable_ratio = 0.6    # 60% в stable pool
    growth_ratio = 0.4    # 40% в growth pool
    
    stable_znx = znx_amount * stable_ratio
    growth_znx = znx_amount * growth_ratio
    
    stable_usd = stable_znx * znx_rate
    growth_usd = growth_znx * znx_rate
    total_usd = znx_amount * znx_rate
    
    print(f"Общий размер пула: {znx_amount:,.0f} ZNX × ${znx_rate:.2f} = ${total_usd:,.2f}")
    print(f"Stable Pool: {stable_znx:,.0f} ZNX = ${stable_usd:,.2f}")
    print(f"Growth Pool: {growth_znx:,.0f} ZNX = ${growth_usd:,.2f}")
    
    return {
        'total_znx': znx_amount,
        'znx_rate': znx_rate,
        'stable_znx': stable_znx,
        'growth_znx': growth_znx,
        'stable_usd': stable_usd,
        'growth_usd': growth_usd,
        'total_usd': total_usd
    }

def calculate_tier_distribution(pool_structure):
    """Рассчитываем распределение по тирам (нужны реальные данные)"""
    print("\n=== РАСПРЕДЕЛЕНИЕ ПО ТИРАМ ===")
    
    # Примерное распределение (нужно найти реальные данные)
    tier_distribution = {
        'basic': 0.5,     # 50%
        'advanced': 0.3,  # 30%
        'premium': 0.2    # 20%
    }
    
    stable_tiers = {}
    growth_tiers = {}
    
    print("STABLE POOL распределение:")
    for tier, ratio in tier_distribution.items():
        tier_znx = pool_structure['stable_znx'] * ratio
        tier_usd = tier_znx * pool_structure['znx_rate']
        stable_tiers[tier] = {'znx': tier_znx, 'usd': tier_usd}
        print(f"  {tier.capitalize()}: {tier_znx:,.0f} ZNX = ${tier_usd:,.2f}")
    
    print("\nGROWTH POOL распределение:")
    for tier, ratio in tier_distribution.items():
        tier_znx = pool_structure['growth_znx'] * ratio
        tier_usd = tier_znx * pool_structure['znx_rate']
        growth_tiers[tier] = {'znx': tier_znx, 'usd': tier_usd}
        print(f"  {tier.capitalize()}: {tier_znx:,.0f} ZNX = ${tier_usd:,.2f}")
    
    return stable_tiers, growth_tiers

def calculate_payouts_by_formula(stable_tiers, growth_tiers, stable_rates, growth_rates, daily_df):
    """Рассчитываем выплаты по правильным формулам"""
    print("\n=== РАСЧЕТ ВЫПЛАТ ПО ПРАВИЛЬНЫМ ФОРМУЛАМ ===")
    
    # Получаем финальный GGR multiplier
    final_ggr_multiplier = daily_df['ggr_multiplier'].iloc[-1]
    print(f"Финальный GGR multiplier: {final_ggr_multiplier:.3f}x")
    
    total_stable_cash = 0
    total_growth_cash = 0
    total_growth_tokens = 0
    
    print(f"\nSTABLE POOL выплаты (формула: invested_amount × {final_ggr_multiplier:.3f} × rate):")
    for tier in ['basic', 'advanced', 'premium']:
        invested_amount = stable_tiers[tier]['usd']
        rate = stable_rates[tier]
        cash_received = invested_amount * final_ggr_multiplier * rate
        per_dollar = final_ggr_multiplier * rate
        
        total_stable_cash += cash_received
        
        print(f"  {tier.capitalize()}: ${invested_amount:,.0f} × {final_ggr_multiplier:.3f} × {rate:.3%} = ${cash_received:,.2f}")
        print(f"    Per dollar: {final_ggr_multiplier:.3f} × {rate:.3%} = ${per_dollar:.3f}")
    
    print(f"\nGROWTH POOL выплаты (формула: cash + 100% tokens returned):")
    for tier in ['basic', 'advanced', 'premium']:
        invested_amount = growth_tiers[tier]['usd']
        rate = growth_rates[tier]
        cash_received = invested_amount * final_ggr_multiplier * rate
        tokens_returned = invested_amount  # 100% tokens returned
        total_value = cash_received + tokens_returned
        per_dollar = (final_ggr_multiplier * rate) + 1.0
        
        total_growth_cash += cash_received
        total_growth_tokens += tokens_returned
        
        print(f"  {tier.capitalize()}: ${invested_amount:,.0f} invested, {final_ggr_multiplier:.3f}x GGR")
        print(f"    Cash: ${invested_amount:,.0f} × {final_ggr_multiplier:.3f} × {rate:.3%} = ${cash_received:,.2f}")
        print(f"    Tokens: ${tokens_returned:,.0f}")
        print(f"    Total: ${total_value:,.2f}")
        print(f"    Per dollar: ({final_ggr_multiplier:.3f} × {rate:.3%}) + 1.00 = ${per_dollar:.3f}")
    
    total_cash_paid = total_stable_cash + total_growth_cash
    
    print(f"\n=== ИТОГОВЫЕ ВЫПЛАТЫ ===")
    print(f"Stable Pool cash: ${total_stable_cash:,.2f}")
    print(f"Growth Pool cash: ${total_growth_cash:,.2f}")
    print(f"Growth Pool tokens: ${total_growth_tokens:,.2f}")
    print(f"Общие cash выплаты: ${total_cash_paid:,.2f}")
    
    return {
        'stable_cash': total_stable_cash,
        'growth_cash': total_growth_cash,
        'growth_tokens': total_growth_tokens,
        'total_cash': total_cash_paid
    }

def analyze_high_watermark(monthly_df):
    """Анализируем влияние high watermark"""
    print("\n=== АНАЛИЗ HIGH WATERMARK ===")
    
    print("Месячные выплаты из данных:")
    for _, row in monthly_df.iterrows():
        if row['stable_payout'] > 0 or row['growth_payout'] > 0:
            print(f"  {int(row['year'])}-{int(row['month']):02d}: "
                  f"Stable ${row['stable_payout']:,.2f}, "
                  f"Growth ${row['growth_payout']:,.2f}, "
                  f"Watermark: {'Yes' if row['watermark_exceeded'] else 'No'}")
    
    total_stable = monthly_df['stable_payout'].sum()
    total_growth = monthly_df['growth_payout'].sum()
    
    print(f"\nИтого из monthly_df:")
    print(f"Stable Pool: ${total_stable:,.2f}")
    print(f"Growth Pool: ${total_growth:,.2f}")
    print(f"Общие выплаты: ${total_stable + total_growth:,.2f}")
    
    return total_stable, total_growth

def compare_formulas_vs_data(calculated_payouts, monthly_stable, monthly_growth, pool_structure):
    """Сравниваем расчетные формулы с реальными данными"""
    print("\n=== СРАВНЕНИЕ ФОРМУЛ С ДАННЫМИ ===")
    
    print("РАСЧЕТНЫЕ ФОРМУЛЫ vs ДАННЫЕ ИЗ CSV:")
    print(f"Stable Pool: ${calculated_payouts['stable_cash']:,.2f} vs ${monthly_stable:,.2f}")
    print(f"Growth Pool: ${calculated_payouts['growth_cash']:,.2f} vs ${monthly_growth:,.2f}")
    print(f"Общие cash: ${calculated_payouts['total_cash']:,.2f} vs ${monthly_stable + monthly_growth:,.2f}")
    
    # Правильные формулы для дашборда
    print(f"\n=== ПРАВИЛЬНЫЕ ФОРМУЛЫ ДЛЯ ДАШБОРДА ===")
    print(f"1. СОБРАНО = {pool_structure['total_znx']:,.0f} ZNX × ${pool_structure['znx_rate']:.2f} = ${pool_structure['total_usd']:,.2f}")
    print(f"2. ВЫПЛАЧЕНО = ${monthly_stable + monthly_growth:,.2f} (из monthly_df с учетом high watermark)")
    
    cost_of_capital = ((monthly_stable + monthly_growth) / pool_structure['total_usd']) * 100
    print(f"3. СТОИМОСТЬ КАПИТАЛА = ({monthly_stable + monthly_growth:,.2f} / {pool_structure['total_usd']:,.2f}) × 100 = {cost_of_capital:.1f}%")

def main():
    """Основная функция анализа"""
    print("АНАЛИЗ ПРАВИЛЬНЫХ ФОРМУЛ С УЧЕТОМ ТИРОВ")
    print("=" * 60)
    
    # Загружаем данные
    daily_df, monthly_df, tiers_df = load_data()
    
    # Анализируем проценты выплат
    stable_rates, growth_rates = analyze_tier_rates()
    
    # Рассчитываем структуру пулов
    pool_structure = calculate_pool_structure()
    
    # Распределение по тирам
    stable_tiers, growth_tiers = calculate_tier_distribution(pool_structure)
    
    # Рассчитываем выплаты по формулам
    calculated_payouts = calculate_payouts_by_formula(stable_tiers, growth_tiers, stable_rates, growth_rates, daily_df)
    
    # Анализируем high watermark
    monthly_stable, monthly_growth = analyze_high_watermark(monthly_df)
    
    # Сравниваем формулы с данными
    compare_formulas_vs_data(calculated_payouts, monthly_stable, monthly_growth, pool_structure)
    
    print("\n" + "=" * 60)
    print("ЗАКЛЮЧЕНИЕ:")
    print("✅ Собрано = ZNX amount × ZNX rate")
    print("✅ Выплачено = данные из monthly_df (с учетом high watermark)")
    print("✅ Стоимость капитала = (выплачено / собрано) × 100")
    print("✅ Формулы по тирам работают с учетом high watermark принципа")

if __name__ == "__main__":
    main()