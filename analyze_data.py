import pandas as pd

# Load data
monthly_df = pd.read_csv('pool1_nov2025_monthly.csv')
daily_df = pd.read_csv('pool1_nov2025_daily.csv')

# Calculate totals from monthly data
total_stable = monthly_df['stable_payout'].sum()
total_growth = monthly_df['growth_payout'].sum()
total_cash = total_stable + total_growth
total_referral = monthly_df['monthly_referral_cost'].sum()
total_capital_cost = monthly_df['capital_cost_usd'].sum()
final_ggr = monthly_df['cumulative_ggr'].iloc[-1]

print("=== АНАЛИЗ ДАННЫХ ===")
print(f'Total Stable Payout: ${total_stable:,.2f}')
print(f'Total Growth Payout: ${total_growth:,.2f}')
print(f'Total Cash Paid: ${total_cash:,.2f}')
print(f'Total Referral Cost: ${total_referral:,.2f}')
print(f'Total Capital Cost (собрано): ${total_capital_cost:,.2f}')
print(f'Final GGR: ${final_ggr:,.2f}')

# Get data from daily CSV
final_ggr_daily = daily_df['cumulative_ggr'].iloc[-1]
final_multiplier = daily_df['ggr_multiplier'].iloc[-1]

print(f'\n=== ДАННЫЕ ИЗ DAILY CSV ===')
print(f'Final GGR (daily): ${final_ggr_daily:,.2f}')
print(f'Final GGR Multiplier: {final_multiplier:.2f}x')

# Dashboard calculation (НЕПРАВИЛЬНАЯ)
dashboard_real_pool_size = final_ggr_daily / final_multiplier if final_multiplier > 0 else 50000
dashboard_cost_of_capital = (total_cash / dashboard_real_pool_size) * 100

print(f'\n=== РАСЧЕТ ДАШБОРДА (НЕПРАВИЛЬНЫЙ) ===')
print(f'Dashboard Real Pool Size: ${dashboard_real_pool_size:,.2f}')
print(f'Dashboard Cost of Capital: {dashboard_cost_of_capital:.1f}%')

# ПРАВИЛЬНЫЙ расчет
correct_pool_size = total_capital_cost  # Реально собранная сумма
correct_cost_of_capital = (total_cash / correct_pool_size) * 100

print(f'\n=== ПРАВИЛЬНЫЙ РАСЧЕТ ===')
print(f'Correct Pool Size (собрано): ${correct_pool_size:,.2f}')
print(f'Correct Cost of Capital: {correct_cost_of_capital:.1f}%')

print(f'\n=== ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ ===')
print(f'Выплачено: ${total_cash:,.0f}')
print(f'Собрано: ${correct_pool_size:,.0f}')
print(f'Процент выплат: {(total_cash / correct_pool_size * 100):.1f}%')
print(f'Стоимость капитала: {correct_cost_of_capital:.1f}%')