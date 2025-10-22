# Полный анализ проекта Zenex RevShare Pool Calculator

## 1. Общее описание проекта

Проект представляет собой калькулятор доходности для инвестиционных пулов Zenex с двумя типами пулов:
- **Stable Pool** (стабильный пул) - гарантированная доходность
- **Growth Pool** (ростовой пул) - высокорисковая доходность

Система моделирует работу казино/гемблинг платформы с инвесторами, где:
- Инвесторы вкладывают деньги в пулы
- Платформа тратит деньги на привлечение трафика
- Игроки делают депозиты и играют
- Генерируется GGR (Gross Gaming Revenue)
- Прибыль распределяется между инвесторами

## 2. Структура проекта

```
Zenex Calc/
├── dashboard_app.py          # Основной дашборд Streamlit
├── revshare_pool.py         # Класс генератора данных
├── readme.md                # Документация
├── run.py                   # Скрипт запуска генерации
├── pool1_nov2025_daily.csv      # Ежедневные данные
├── pool1_nov2025_monthly.csv    # Месячные данные
└── pool1_nov2025_monthly_tiers_znx.csv  # Данные по тирам
```

## 3. Основные параметры системы

### 3.1 Параметры пулов
- **Размер пула по умолчанию**: $50,000
- **Stable пул**: 60% от общего пула ($30,000)
- **Growth пул**: 40% от общего пула ($20,000)

### 3.2 Тиры инвесторов
Каждый пул разделен на 3 тира с разным распределением капитала:

**Stable Pool тиры:**
- Basic (Bronze): 34% доходность, 30% капитала
- Advanced (Silver): 38.25% доходность, 40% капитала  
- Premium (Gold): 42.5% доходность, 30% капитала

**Growth Pool тиры:**
- Basic (Bronze): 8.5% доходность, 30% капитала
- Advanced (Silver): 10.625% доходность, 40% капитала
- Premium (Gold): 12.75% доходность, 30% капитала

### 3.3 Параметры трафика
- **CPA диапазон**: $50-$150 (стоимость привлечения одного игрока)
- **Целевой GGR множитель**: 3.2x
- **Волатильность GGR**: 15% (стандартное отклонение)

## 4. Ключевые формулы и расчеты

### 4.1 Основные формулы доходности

**Stable Pool (только денежные выплаты):**
```
payout = investment × GGR_multiplier × tier_rate
```

**Growth Pool (денежные выплаты + возврат токенов):**
```
cash_payout = investment × GGR_multiplier × tier_rate
total_return = cash_payout + investment
```

### 4.2 Расчет возврата на $1 инвестиций

**Stable Pool:**
```
return_per_dollar = GGR_multiplier × tier_rate
```

**Growth Pool:**
```
return_per_dollar = (GGR_multiplier × tier_rate) + 1.00
```

### 4.3 Формулы генерации данных

**Ежедневный GGR:**
```python
base_ggr = traffic_budget * ggr_margin * (1 + seasonal_multiplier)
daily_ggr = base_ggr * (1 + random_variance)
```

**Накопительный GGR:**
```python
cumulative_ggr = sum(daily_ggr for all days)
```

**GGR множитель:**
```python
ggr_multiplier = cumulative_ggr / pool_size
```

### 4.4 Расчет выплат (HIGH WATERMARK LOGIC)

**High Watermark система защищает инвесторов от потерь:**
- Выплаты происходят только когда cumulative_ggr превышает предыдущий максимум
- При достижении нового максимума, high_watermark обновляется
- Если cumulative_ggr падает ниже watermark, выплаты = 0

**Логика выплат:**
```python
if month_end_cumulative_ggr > high_watermark:
    # Выплачиваем только с суммы превышения
    excess_ggr = month_end_cumulative_ggr - high_watermark
    stable_payout = excess_ggr * stable_weighted_rate
    growth_payout = excess_ggr * growth_weighted_rate
    
    # Обновляем watermark
    high_watermark = month_end_cumulative_ggr
    watermark_exceeded = True
else:
    # Нет выплат, если не превышен watermark
    stable_payout = 0.0
    growth_payout = 0.0
    watermark_exceeded = False
```

### 4.5 Взвешенные ставки тиров

**Расчет взвешенной ставки:**
```python
weighted_rate = (
    basic_rate * 0.3 +      # 30% капитала
    advanced_rate * 0.4 +   # 40% капитала
    premium_rate * 0.3      # 30% капитала
)
```

**Stable Pool взвешенная ставка:**
```
0.34 * 0.3 + 0.3825 * 0.4 + 0.425 * 0.3 = 0.3808 (38.08%)
```

**Growth Pool взвешенная ставка:**
```
0.085 * 0.3 + 0.10625 * 0.4 + 0.1275 * 0.3 = 0.1069 (10.69%)
```

## 5. Метрики безубыточности

### 5.1 Основные пороги
- **Минимальный GGR/Spent**: 295% для безубыточности
- **Минимальная доходность Stable**: 34%
- **Гарантированный возврат Stable**: 100% (если выплаты меньше)
- **Отображение Returns Per $1 Invested**: Показывает доходность каждого тира
- **High Watermark защита**: Выплаты только при превышении предыдущих максимумов

### 5.2 Формулы проверки

**Проверка безубыточности:**
```python
is_breakeven = (cumulative_ggr / total_spent) >= 2.95
```

**Проверка минимума Stable:**
```python
stable_return_pct = (total_stable_payout / stable_investment) * 100
meets_minimum = stable_return_pct >= 34.0
```

**Корректировка Stable до 100%:**
```python
stable_correction = max(0, stable_investment - total_stable_payout)
```

## 6. Модель привлечения трафика

### 6.1 Параметры игроков
- **Retention модель**: Ежедневное снижение активности
- **Средний депозит**: Растет с возрастом когорты
- **Сезонность**: Множители для разных периодов
- **FTD расчет**: На основе CPA и бюджета

### 6.2 Формулы трафика

**Количество новых FTD в день:**
```python
daily_ftds = daily_traffic_spend / random_cpa
```

**Активные игроки:**
```python
active_players = sum(cohort_size * retention_rate for all cohorts)
```

**Общие депозиты:**
```python
total_deposits = sum(cohort_deposits * avg_deposit for all cohorts)
```

## 7. Реферальная система

### 7.1 Параметры
- **Доля рефералов**: 0-50% инвесторов
- **Единовременные бонусы**: 3% от реферального капитала
- **Постоянные выплаты**: 4% от Stable, 15% от Growth выплат

### 7.2 Формулы

**Единовременный бонус:**
```python
upfront_bonus = referral_capital * bonus_rate
```

**Постоянные выплаты:**
```python
ongoing_referral = pool_payout * ongoing_share_rate
```

## 8. Структура данных

### 8.1 Ежедневные данные (daily.csv)
- `date`: Дата
- `new_ftds`: Новые игроки
- `active_players`: Активные игроки
- `total_deposits`: Общие депозиты
- `daily_ggr`: Дневной GGR
- `cumulative_ggr`: Накопительный GGR
- `ggr_multiplier`: GGR множитель
- `traffic_spend`: Расходы на трафик
- `cumulative_traffic`: Накопительные расходы
- `stable_payout`: Выплаты Stable
- `growth_payout`: Выплаты Growth
- `stable_return_pct`: Процент возврата Stable
- `growth_return_pct`: Процент возврата Growth

### 8.2 Месячные данные (monthly.csv)
- `year`, `month`: Период
- `monthly_ggr`: Месячный GGR
- `stable_payout`: Месячные выплаты Stable
- `growth_payout`: Месячные выплаты Growth
- `traffic_cost`: Месячные расходы на трафик
- `monthly_referral_cost`: Реферальные выплаты

### 8.3 Данные по тирам (monthly_tiers_znx.csv)
- `year`, `month`: Период
- `pool`: Тип пула (stable/growth)
- `tier`: Тир (basic/advanced/premium)
- `per_znx_cash_usd`: Денежная выплата за 1 ZNX
- `per_znx_total_usd`: Общая выплата за 1 ZNX

## 9. Логика дашборда

### 9.1 Основные метрики
1. **Совокупные показатели**: Размер пула, выплаты, GGR множитель, корректировки
2. **Ключевые показатели**: Raised, Spent, FTD, CPA, Referral
3. **Метрики безубыточности**: GGR/Spent, Total GGR, статус, гарантии

### 9.2 Визуализация
- График динамики GGR
- Столбчатые диаграммы месячных выплат
- Таблицы ежедневных показателей
- Итоговая доходность по тирам

### 9.3 Расчет итоговой доходности

**Пример для GGR множителя 3.2:**

Stable Pool:
- Basic: $1 → $1.09 (3.2 × 0.34)
- Advanced: $1 → $1.22 (3.2 × 0.3825)
- Premium: $1 → $1.36 (3.2 × 0.425)

Growth Pool:
- Basic: $1 → $1.27 (3.2 × 0.085 + 1.00)
- Advanced: $1 → $1.34 (3.2 × 0.10625 + 1.00)
- Premium: $1 → $1.41 (3.2 × 0.1275 + 1.00)

## 10. Ключевые особенности системы

### 10.1 Принципы работы
1. **Stable Pool**: Только денежные выплаты, гарантия 100% возврата
2. **Growth Pool**: Денежные выплаты + возврат токенов
3. **High Watermark**: Выплаты не могут превышать накопленный GGR
4. **Tier System**: Разные уровни доходности для разных инвесторов

### 10.2 Риски и ограничения
1. **Минимальные пороги**: 295% GGR/Spent, 34% для Stable
2. **Волатильность**: 15% стандартное отклонение GGR
3. **Зависимость от трафика**: Эффективность CPA влияет на результат
4. **Сезонность**: Влияет на доходность в разные периоды

### 10.3 Валидация результатов
- Проверка диапазона GGR множителя
- Монотонность накопительного GGR
- Неотрицательность активных игроков
- Выплаты не превышают накопленный GGR
- Проверка прибыльности тиров

## 11. Заключение

Система представляет собой комплексную модель инвестиционных пулов для гемблинг платформы с детальным моделированием:
- Привлечения и удержания игроков
- Генерации доходов (GGR)
- Распределения прибыли между инвесторами
- Различных уровней риска и доходности
- Реферальной системы
- Метрик безубыточности

Все расчеты основаны на реальных данных и включают механизмы защиты инвесторов (гарантии возврата для Stable Pool) и валидации результатов.