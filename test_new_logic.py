#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправленной логики выплат и новых параметров
"""

from revshare_pool import RevSharePoolGenerator
import pandas as pd

def test_high_watermark_logic():
    """Тестирует логику high watermark - выплаты только при росте GGR"""
    print("=== Тест логики High Watermark ===")
    
    # Создаем генератор с абсолютными значениями токенов
    generator = RevSharePoolGenerator(
        pool_size=50000,  # $50,000 USD
        znx_amount=50000,  # 50,000 ZNX токенов
        znx_rate=1.0,      # $1 за ZNX
        stable_znx_amount=30000,  # 30,000 ZNX в Stable пуле
        growth_znx_amount=20000,  # 20,000 ZNX в Growth пуле
        target_ggr_multiplier=3.0,
        ggr_volatility=0.15,
        start_date="2025-11-01",
        seed=12345  # Фиксированный seed для воспроизводимости
    )
    
    print(f"Stable ratio: {generator.stable_ratio:.3f}")
    print(f"Growth ratio: {generator.growth_ratio:.3f}")
    print(f"Stable ZNX amount: {generator.stable_znx_amount:,.0f}")
    print(f"Growth ZNX amount: {generator.growth_znx_amount:,.0f}")
    
    # Генерируем данные
    daily_data = generator.generate_daily_data()
    
    # Проверяем первые несколько дней на наличие выплат
    print("\n=== Первые 10 дней ===")
    first_days = daily_data.head(10)[['date', 'cumulative_ggr', 'stable_payout', 'growth_payout']]
    print(first_days.to_string(index=False))
    
    # Проверяем дни с отрицательным GGR
    negative_ggr_days = daily_data[daily_data['daily_ggr'] < 0]
    print(f"\n=== Дни с отрицательным GGR: {len(negative_ggr_days)} ===")
    if len(negative_ggr_days) > 0:
        print(negative_ggr_days[['date', 'daily_ggr', 'cumulative_ggr', 'stable_payout', 'growth_payout']].head().to_string(index=False))
    
    # Проверяем месячные данные
    monthly_data = generator.get_monthly_summary(daily_data)
    print("\n=== Месячные данные ===")
    print("Доступные колонки:", list(monthly_data.columns))
    print(monthly_data.to_string(index=False))
    
    # Проверяем, что выплаты происходят только при росте high watermark
    print("\n=== Проверка High Watermark логики ===")
    for _, row in monthly_data.iterrows():
        stable_payout = row.get('stable_payout', 0)
        growth_payout = row.get('growth_payout', 0)
        if stable_payout > 0 or growth_payout > 0:
            print(f"Месяц {row.get('month', 'N/A')}: Stable={stable_payout:,.0f}, Growth={growth_payout:,.0f}")

def test_absolute_token_amounts():
    """Тестирует работу с абсолютными количествами токенов"""
    print("\n\n=== Тест абсолютных количеств токенов ===")
    
    # Тест 1: Стандартные значения
    gen1 = RevSharePoolGenerator(
        znx_amount=100000,
        stable_znx_amount=60000,
        growth_znx_amount=40000,
        znx_rate=1.5
    )
    
    print(f"Тест 1 - ZNX: 100,000, Stable: 60,000, Growth: 40,000, Rate: $1.5")
    print(f"  Pool size: ${gen1.pool_size:,.0f}")
    print(f"  Stable ratio: {gen1.stable_ratio:.3f}")
    print(f"  Growth ratio: {gen1.growth_ratio:.3f}")
    
    # Тест 2: Неполное распределение
    gen2 = RevSharePoolGenerator(
        znx_amount=100000,
        stable_znx_amount=50000,
        growth_znx_amount=30000,  # Остается 20,000 нераспределенных
        znx_rate=2.0
    )
    
    print(f"\nТест 2 - ZNX: 100,000, Stable: 50,000, Growth: 30,000, Rate: $2.0")
    print(f"  Pool size: ${gen2.pool_size:,.0f}")
    print(f"  Stable ratio: {gen2.stable_ratio:.3f}")
    print(f"  Growth ratio: {gen2.growth_ratio:.3f}")
    print(f"  Нераспределено: {100000 - 50000 - 30000:,} ZNX ({(100000 - 50000 - 30000)/100000:.1%})")
    
    # Тест 3: Проверка ошибки при превышении лимита
    try:
        gen3 = RevSharePoolGenerator(
            znx_amount=100000,
            stable_znx_amount=70000,
            growth_znx_amount=50000,  # Сумма 120,000 > 100,000
            znx_rate=1.0
        )
        print("\nТест 3 - ОШИБКА: должна была возникнуть ошибка валидации!")
    except ValueError as e:
        print(f"\nТест 3 - Корректно поймана ошибка: {e}")

if __name__ == "__main__":
    test_high_watermark_logic()
    test_absolute_token_amounts()
    print("\n=== Все тесты завершены ===")