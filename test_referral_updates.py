#!/usr/bin/env python3
"""
Тестирование обновленной логики реферальных выплат
"""

from revshare_pool import RevSharePoolGenerator, PartnerStatus, ReferralTurnoverTier

def test_partner_status_system():
    """Тестирует накопительную систему статусов партнеров"""
    print("=== Тестирование системы статусов партнеров ===")
    
    # Тест 1: По количеству активных рефералов
    status1 = PartnerStatus.calculate_status(active_referrals=10, znx_investment=1000)
    print(f"10 рефералов, 1000 ZNX -> {status1.name}")
    
    # Тест 2: По ZNX инвестициям
    status2 = PartnerStatus.calculate_status(active_referrals=3, znx_investment=25000)
    print(f"3 реферала, 25000 ZNX -> {status2.name}")
    
    # Тест 3: Максимальный статус
    status3 = PartnerStatus.calculate_status(active_referrals=200, znx_investment=150000)
    print(f"200 рефералов, 150000 ZNX -> {status3.name}")
    
    # Показать все статусы
    print("\nВсе доступные статусы:")
    for status in PartnerStatus.get_all_statuses():
        print(f"  {status.name}: {status.min_active_referrals} рефералов ИЛИ {status.min_znx_investment} ZNX")

def test_turnover_tiers():
    """Тестирует тарифы по месячному обороту"""
    print("\n=== Тестирование тарифов по обороту ===")
    
    test_turnovers = [25000, 75000, 200000, 350000, 600000]
    
    for turnover in test_turnovers:
        rate = ReferralTurnoverTier.get_commission_rate(turnover)
        print(f"Оборот {turnover:,} EUR -> {rate:.3f}% комиссия")
    
    # Показать все тарифы
    print("\nВсе тарифы по обороту:")
    for tier in ReferralTurnoverTier.get_turnover_tiers():
        max_str = f"{tier.max_turnover:,.0f}" if tier.max_turnover != float('inf') else "∞"
        print(f"  {tier.name}: {tier.min_turnover:,.0f} - {max_str} EUR -> {tier.commission_rate:.3f}%")

def test_new_referral_calculations():
    """Тестирует новые расчеты реферальных выплат"""
    print("\n=== Тестирование новых расчетов реферальных выплат ===")
    
    # Создаем генератор с новыми параметрами
    generator = RevSharePoolGenerator(
        pool_size=35000,
        stable_ratio=0.6,
        growth_ratio=0.4,
        target_ggr_multiplier=3.0,
        referral_ratio=0.1,  # 10% пользователей пришли по рефералам
        avg_monthly_turnover_eur=150000,  # Средний оборот 150k EUR
        turnover_volatility=0.3,
        seed=42
    )
    
    # Тестируем расчет реферальных выплат
    monthly_stable = 5000  # $5000 выплата по Stable
    monthly_growth = 8000  # $8000 выплата по Growth
    monthly_turnover = 200000  # 200k EUR оборот
    
    investment_bonus, profit_bonus, turnover_commission = generator._calculate_new_referral_costs(
        monthly_stable, monthly_growth, monthly_turnover
    )
    
    print(f"Месячные выплаты: Stable ${monthly_stable:,}, Growth ${monthly_growth:,}")
    print(f"Месячный оборот рефералов: {monthly_turnover:,} EUR")
    print(f"Результат:")
    print(f"  Бонус с инвестиций: ${investment_bonus:.2f}")
    print(f"  Бонус с прибыли: ${profit_bonus:.2f}")
    print(f"  Комиссия с оборота: ${turnover_commission:.2f}")
    print(f"  Общие реферальные выплаты: ${investment_bonus + profit_bonus + turnover_commission:.2f}")

def test_monthly_data_generation():
    """Тестирует генерацию месячных данных с новой логикой"""
    print("\n=== Тестирование генерации данных ===")
    
    generator = RevSharePoolGenerator(
        pool_size=35000,
        stable_ratio=0.6,
        growth_ratio=0.4,
        target_ggr_multiplier=3.0,
        referral_ratio=0.15,  # 15% пользователей пришли по рефералам
        avg_monthly_turnover_eur=100000,
        seed=42
    )
    
    # Генерируем данные
    daily_df = generator.generate_daily_data()
    monthly_df = generator.get_monthly_summary(daily_df)
    
    print(f"Сгенерировано {len(daily_df)} дней данных")
    print(f"Сгенерировано {len(monthly_df)} месяцев данных")
    
    # Показываем первые несколько месяцев
    print("\nПервые 3 месяца:")
    for _, month in monthly_df.head(3).iterrows():
        referral_cost = month.get('monthly_referral_cost', 0)
        print(f"  {month['year']}-{month['month']:02d}: "
              f"GGR ${month['monthly_ggr']:,.0f}, "
              f"Stable ${month['stable_payout']:,.0f}, "
              f"Growth ${month['growth_payout']:,.0f}, "
              f"Referral ${referral_cost:,.0f}")
    
    # Проверяем итоговые метрики
    final_ggr = daily_df['cumulative_ggr'].iloc[-1]
    final_stable = daily_df['cumulative_stable'].iloc[-1]
    final_growth = daily_df['cumulative_growth'].iloc[-1]
    final_referral = daily_df['cumulative_referral_cost'].iloc[-1]
    
    print(f"\nИтоговые результаты:")
    print(f"  Общий GGR: ${final_ggr:,.0f}")
    print(f"  GGR множитель: {final_ggr / generator.pool_size:.2f}x")
    print(f"  Выплаты Stable: ${final_stable:,.0f}")
    print(f"  Выплаты Growth: ${final_growth:,.0f}")
    print(f"  Реферальные выплаты: ${final_referral:,.0f}")
    print(f"  Общие выплаты: ${final_stable + final_growth + final_referral:,.0f}")

if __name__ == "__main__":
    test_partner_status_system()
    test_turnover_tiers()
    test_new_referral_calculations()
    test_monthly_data_generation()
    print("\n✅ Все тесты завершены!")