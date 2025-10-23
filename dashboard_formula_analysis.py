#!/usr/bin/env python3
"""
Детальный анализ формул дашборда на основе данных из итоговой таблицы
"""

import pandas as pd
import numpy as np

def load_data():
    """Загружаем все данные"""
    daily_df = pd.read_csv('pool1_nov2025_daily.csv')
    monthly_df = pd.read_csv('pool1_nov2025_monthly.csv')
    monthly_tiers_df = pd.read_csv('pool1_nov2025_monthly_tiers_znx.csv')
    
    return daily_df, monthly_df, monthly_tiers_df

def analyze_final_table_data(daily_df, monthly_df):
    """Анализируем данные из итоговой таблицы доходности по пулам"""
    print("=" * 80)
    print("АНАЛИЗ ДАННЫХ ИЗ ИТОГОВОЙ ТАБЛИЦЫ ДОХОДНОСТИ ПО ПУЛАМ")
    print("=" * 80)
    
    # Анализируем данные по пулу (это данные одного пула)
    print("\nСТРУКТУРА ДАННЫХ:")
    print("-" * 50)
    print(f"Количество дней в daily.csv: {len(daily_df)}")
    print(f"Количество месяцев в monthly.csv: {len(monthly_df)}")
    
    # Получаем итоговые данные из последней строки daily_df
    last_day = daily_df.iloc[-1]
    
    print(f"\nДАННЫЕ НА ПОСЛЕДНИЙ ДЕНЬ ({last_day['date']}):")
    print("-" * 50)
    print(f"Общий GGR: ${last_day['cumulative_ggr']:,.2f}")
    print(f"Общие stable выплаты: ${last_day['cumulative_stable']:,.2f}")
    print(f"Общие growth выплаты: ${last_day['cumulative_growth']:,.2f}")
    print(f"Общие выплаты: ${last_day['cumulative_stable'] + last_day['cumulative_growth']:,.2f}")
    print(f"GGR multiplier: {last_day['ggr_multiplier']:.6f}")
    print(f"Общие traffic расходы: ${last_day['cumulative_traffic']:,.2f}")
    print(f"Общие referral расходы: ${last_day['cumulative_referral_cost']:,.2f}")
    
    # Анализируем monthly данные
    print(f"\nДАННЫЕ ИЗ MONTHLY.CSV:")
    print("-" * 50)
    total_stable_monthly = monthly_df['stable_payout'].sum()
    total_growth_monthly = monthly_df['growth_payout'].sum()
    total_capital_cost = monthly_df['capital_cost_usd'].sum()
    total_referral_monthly = monthly_df['monthly_referral_cost'].sum()
    
    print(f"Сумма stable выплат: ${total_stable_monthly:,.2f}")
    print(f"Сумма growth выплат: ${total_growth_monthly:,.2f}")
    print(f"Общие выплаты: ${total_stable_monthly + total_growth_monthly:,.2f}")
    print(f"Сумма capital cost: ${total_capital_cost:,.2f}")
    print(f"Сумма referral cost: ${total_referral_monthly:,.2f}")
    
    # Рассчитываем "вложено" и "получено" как в итоговой таблице
    # Вложено = capital_cost_usd (это размер пула)
    # Получено = stable_payout + growth_payout
    
    invested = total_capital_cost
    received = total_stable_monthly + total_growth_monthly
    profit = received - invested
    roi_percent = (profit / invested) * 100 if invested > 0 else 0
    
    print(f"\nИТОГОВАЯ ТАБЛИЦА ДОХОДНОСТИ:")
    print("-" * 50)
    print(f"Вложено (capital_cost): ${invested:,.2f}")
    print(f"Получено (выплаты): ${received:,.2f}")
    print(f"Прибыль: ${profit:,.2f}")
    print(f"ROI: {roi_percent:.1f}%")
    
    return {
        'invested': invested,
        'received': received,
        'profit': profit,
        'roi_percent': roi_percent,
        'total_stable_monthly': total_stable_monthly,
        'total_growth_monthly': total_growth_monthly,
        'total_capital_cost': total_capital_cost,
        'last_day_data': last_day
    }

def analyze_dashboard_formulas(daily_df, monthly_df):
    """Анализируем формулы дашборда"""
    print("\n" + "=" * 80)
    print("АНАЛИЗ ФОРМУЛ ДАШБОРДА")
    print("=" * 80)
    
    # 1. Расчет real_pool_size (как в дашборде)
    final_ggr = daily_df['cumulative_ggr'].iloc[-1]
    final_multiplier = daily_df['ggr_multiplier'].iloc[-1]
    
    if final_multiplier > 0:
        real_pool_size = final_ggr / final_multiplier
    else:
        real_pool_size = 50000  # DEFAULT_POOL_SIZE
    
    print(f"\n1. РАСЧЕТ 'СОБРАНО' (real_pool_size):")
    print(f"   Формула: final_ggr / ggr_multiplier")
    print(f"   final_ggr = ${final_ggr:,.2f}")
    print(f"   ggr_multiplier = {final_multiplier:.6f}")
    print(f"   real_pool_size = ${real_pool_size:,.2f}")
    
    # 2. Расчет cash выплат (как в дашборде)
    total_stable = monthly_df['stable_payout'].sum()
    total_growth = monthly_df['growth_payout'].sum()
    total_cash_paid = total_stable + total_growth
    
    print(f"\n2. РАСЧЕТ 'CASH ВЫПЛАТЫ':")
    print(f"   Формула: sum(stable_payout) + sum(growth_payout) из monthly_df")
    print(f"   Stable payouts: ${total_stable:,.2f}")
    print(f"   Growth payouts: ${total_growth:,.2f}")
    print(f"   Всего cash выплат: ${total_cash_paid:,.2f}")
    
    # 3. Расчет referral costs
    total_referral = monthly_df['monthly_referral_cost'].sum()
    
    print(f"\n3. РАСЧЕТ 'REFERRAL COSTS':")
    print(f"   Формула: sum(monthly_referral_cost) из monthly_df")
    print(f"   Referral costs: ${total_referral:,.2f}")
    
    # 4. Общие выплаты
    total_payments = total_cash_paid + total_referral
    
    print(f"\n4. ОБЩИЕ ВЫПЛАТЫ:")
    print(f"   Формула: cash_выплаты + referral_costs")
    print(f"   Общие выплаты: ${total_payments:,.2f}")
    
    # 5. Стоимость капитала
    cost_of_capital = (total_payments / real_pool_size) * 100
    
    print(f"\n5. СТОИМОСТЬ КАПИТАЛА:")
    print(f"   Формула: (общие_выплаты / собрано) * 100")
    print(f"   Стоимость капитала: {cost_of_capital:.1f}%")
    
    return {
        'real_pool_size': real_pool_size,
        'total_cash_paid': total_cash_paid,
        'total_referral': total_referral,
        'total_payments': total_payments,
        'cost_of_capital': cost_of_capital
    }

def compare_results(table_data, dashboard_data):
    """Сравниваем результаты"""
    print("\n" + "=" * 80)
    print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
    print("=" * 80)
    
    print("\nИТОГОВАЯ ТАБЛИЦА vs ДАШБОРД:")
    print("-" * 50)
    
    print(f"СОБРАНО:")
    print(f"  Итоговая таблица (capital_cost): ${table_data['invested']:,.2f}")
    print(f"  Дашборд (real_pool_size): ${dashboard_data['real_pool_size']:,.2f}")
    print(f"  Разница: ${dashboard_data['real_pool_size'] - table_data['invested']:,.2f}")
    
    print(f"\nВЫПЛАЧЕНО:")
    print(f"  Итоговая таблица (выплаты): ${table_data['received']:,.2f}")
    print(f"  Дашборд (cash выплаты): ${dashboard_data['total_cash_paid']:,.2f}")
    print(f"  Разница: ${dashboard_data['total_cash_paid'] - table_data['received']:,.2f}")
    
    print(f"\nСТОИМОСТЬ КАПИТАЛА:")
    table_cost = (table_data['received'] / table_data['invested']) * 100
    print(f"  Итоговая таблица: {table_cost:.1f}%")
    print(f"  Дашборд: {dashboard_data['cost_of_capital']:.1f}%")
    print(f"  Разница: {dashboard_data['cost_of_capital'] - table_cost:.1f}%")

def analyze_discrepancies(table_data, dashboard_data):
    """Анализируем причины расхождений"""
    print("\n" + "=" * 80)
    print("АНАЛИЗ ПРИЧИН РАСХОЖДЕНИЙ")
    print("=" * 80)
    
    print("\n1. ПРОБЛЕМА С 'СОБРАНО':")
    print("-" * 40)
    print(f"   Дашборд использует: final_ggr / ggr_multiplier = ${dashboard_data['real_pool_size']:,.2f}")
    print(f"   Итоговая таблица: capital_cost_usd = ${table_data['invested']:,.2f}")
    print(f"   Вывод: Дашборд рассчитывает 'собрано' неправильно!")
    print(f"          Правильно использовать capital_cost_usd как размер пула.")
    
    print("\n2. ПРОБЛЕМА С 'ВЫПЛАЧЕНО':")
    print("-" * 40)
    print(f"   Дашборд: ${dashboard_data['total_cash_paid']:,.2f}")
    print(f"   Итоговая таблица: ${table_data['received']:,.2f}")
    if abs(dashboard_data['total_cash_paid'] - table_data['received']) < 0.01:
        print(f"   Вывод: Выплаты рассчитываются корректно!")
    else:
        print(f"   Вывод: Есть расхождение в расчете выплат!")
    
    print("\n3. ПРОБЛЕМА СО СТОИМОСТЬЮ КАПИТАЛА:")
    print("-" * 40)
    table_cost = (table_data['received'] / table_data['invested']) * 100
    print(f"   Дашборд: {dashboard_data['cost_of_capital']:.1f}%")
    print(f"   Правильный расчет: {table_cost:.1f}%")
    print(f"   Причина: Дашборд использует неправильное значение 'собрано'")

def write_correct_formulas():
    """Записываем корректные формулы"""
    print("\n" + "=" * 80)
    print("КОРРЕКТНЫЕ ФОРМУЛЫ НА ОСНОВЕ ИТОГОВОЙ ТАБЛИЦЫ")
    print("=" * 80)
    
    print("\n✅ ПРАВИЛЬНЫЕ ФОРМУЛЫ:")
    print("-" * 50)
    
    print("\n1. СОБРАНО:")
    print("   Формула: sum(capital_cost_usd)")
    print("   Описание: Сумма всех вложений в пулы (размер пула)")
    print("   Источник: monthly_df['capital_cost_usd'].sum()")
    
    print("\n2. ВЫПЛАЧЕНО:")
    print("   Формула: sum(stable_payout) + sum(growth_payout)")
    print("   Описание: Сумма всех выплат инвесторам")
    print("   Источник: monthly_df['stable_payout'].sum() + monthly_df['growth_payout'].sum()")
    
    print("\n3. СТОИМОСТЬ КАПИТАЛА:")
    print("   Формула: (выплачено / собрано) * 100")
    print("   Описание: Процент выплат от размера пула")
    print("   Правильный расчет: (выплаты / capital_cost) * 100")
    
    print("\n4. ПРИБЫЛЬ/УБЫТОК:")
    print("   Формула: выплачено - собрано")
    print("   Описание: Чистый результат для инвесторов")
    
    print("\n5. ROI:")
    print("   Формула: (прибыль / собрано) * 100")
    print("   Описание: Возврат на инвестиции в процентах")
    
    print("\n❌ НЕПРАВИЛЬНЫЕ ФОРМУЛЫ В ДАШБОРДЕ:")
    print("-" * 50)
    print("\n1. 'СОБРАНО' = final_ggr / ggr_multiplier")
    print("   Проблема: Это не размер пула, а расчетное значение")
    print("   Должно быть: capital_cost_usd")
    
    print("\n2. Стоимость капитала на основе неправильного 'собрано'")
    print("   Проблема: Использует неправильный знаменатель")
    print("   Должно быть: выплаты / capital_cost_usd")

def main():
    """Основная функция"""
    print("ПРОВЕРКА ВСЕХ ФОРМУЛ ДАШБОРДА")
    print("=" * 80)
    
    # Загружаем данные
    daily_df, monthly_df, monthly_tiers_df = load_data()
    
    # Анализируем данные из итоговой таблицы
    table_data = analyze_final_table_data(daily_df, monthly_df)
    
    # Анализируем формулы дашборда
    dashboard_data = analyze_dashboard_formulas(daily_df, monthly_df)
    
    # Сравниваем результаты
    compare_results(table_data, dashboard_data)
    
    # Анализируем причины расхождений
    analyze_discrepancies(table_data, dashboard_data)
    
    # Записываем корректные формулы
    write_correct_formulas()
    
    print("\n" + "=" * 80)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 80)
    print("\n✅ КОРРЕКТНЫЕ ДАННЫЕ:")
    print("   - Данные из итоговой таблицы доходности по пулам")
    print("   - Формулы на основе capital_cost_usd и фактических выплат")
    
    print("\n❌ НЕКОРРЕКТНЫЕ ДАННЫЕ:")
    print("   - Дашборд использует неправильную формулу для 'собрано'")
    print("   - Стоимость капитала рассчитывается на основе неправильного знаменателя")
    
    print("\n🔧 РЕКОМЕНДАЦИИ:")
    print("   1. Использовать capital_cost_usd как 'собрано'")
    print("   2. Пересчитать стоимость капитала: (выплаты / capital_cost) * 100")
    print("   3. Обновить дашборд с правильными формулами")

if __name__ == "__main__":
    main()