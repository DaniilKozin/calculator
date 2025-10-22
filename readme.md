# 🚀 Zenex RevShare Pool Calculator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

Интерактивный дашборд для анализа доходности пулов Zenex с возможностью генерации данных для разных периодов и расчета выплат инвесторам.

## ✨ Основные функции

- 📊 **Анализ доходности** Stable и Growth пулов
- 💰 **Расчет выплат** per-ZNX для разных тиров инвесторов
- 📈 **Метрики безубыточности** (295% GGR/Spent, 34% минимум Stable)
- 🎛️ **Настройка параметров** через интуитивный UI
- 📅 **Генерация данных** для разных месяцев
- 🔒 **High Watermark система** защиты капитала инвесторов
- 📋 **Экспорт данных** в CSV формате

## 🏃‍♂️ Быстрый старт

### Локальный запуск

```bash
# Клонируйте репозиторий
git clone https://github.com/DaniilKozin/calculator.git
cd calculator

# Установите зависимости
pip install -r requirements.txt

# Запустите приложение
streamlit run dashboard_app.py
```

Приложение будет доступно по адресу: http://localhost:8501

## Деплой на Streamlit Community Cloud (БЕСПЛАТНО)

### Шаг 1: Подготовка GitHub репозитория

1. Создайте новый репозиторий на [GitHub](https://github.com)
2. Загрузите все файлы проекта (кроме `.venv/` и `__pycache__/`)
3. Убедитесь что включены файлы:
   - `dashboard_app.py`
   - `revshare_pool.py`
   - `requirements.txt`
   - `readme.md`
   - `.gitignore`
   - CSV файлы с данными

### Шаг 2: Деплой на Streamlit Cloud

1. Перейдите на [share.streamlit.io](https://share.streamlit.io)
2. Войдите через GitHub аккаунт
3. Нажмите "New app"
4. Выберите ваш репозиторий
5. Укажите:
   - **Main file path**: `dashboard_app.py`
   - **Python version**: 3.9+ (рекомендуется)
6. Нажмите "Deploy!"

### Шаг 3: Настройка (опционально)

- Приложение будет доступно по URL: `https://your-app-name.streamlit.app`
- Автоматические обновления при изменениях в GitHub
- Бесплатный хостинг с ограничениями:
  - 1 GB RAM
  - 1 CPU core
  - Засыпает после неактивности

### Альтернативные платформы (бесплатные)

- **Railway**: [railway.app](https://railway.app) - 500 часов/месяц
- **Render**: [render.com](https://render.com) - бесплатный тир
- **Heroku**: [heroku.com](https://heroku.com) - ограниченный бесплатный тир

## Структура файлов

- `dashboard_app.py` - главный файл дашборда
- `revshare_pool.py` - логика генерации данных
- `run.py` - скрипт для генерации тестовых данных
- `requirements.txt` - зависимости Python
- CSV файлы - сгенерированные данные

## Использование

1. Настройте параметры в боковой панели
2. Нажмите "Генерировать данные"
3. Анализируйте результаты в дашборде

## Objective
Create a Python class that generates realistic 365-day casino traffic RevShare Pool data with daily granularity, ensuring all investor tiers achieve positive returns.

## Core Parameters

### Pool Configuration
```python
pool_size: int = 35000  # USD
stable_ratio: float = 0.6  # 60% of pool
growth_ratio: float = 0.4  # 40% of pool
start_date: datetime = "2025-11-01"
duration_days: int = 365
znx_price: float = 0.60  # USD per token
```

### GGR Rates (from generated GGR)
**Stable Pool** (no token return - must return 100%+ capital):
- basic: 34% (100-4,999 ZNX invested)
- advanced: 38.25% (5,000-9,999 ZNX)
- premium: 42.5% (10,000+ ZNX) [CORRECTED from 42%]

**Growth Pool** (100% tokens returned + cash on top):
- basic: 8.5%
- advanced: 10.625%
- premium: 12.75%

### Investor Distribution (apply Pareto principle)
**Use 80/20 rule for realistic distribution:**

Stable Pool:
- basic (34%): 60% of investors, 30% of capital
- advanced (38.25%): 30% of investors, 40% of capital  
- premium (42.5%): 10% of investors, 30% of capital

Growth Pool:
- basic (8.5%): 60% of investors, 30% of capital
- advanced (10.625%): 30% of investors, 40% of capital
- premium (12.75%): 10% of investors, 30% of capital

## Traffic Acquisition (Month 1 Only)

### Traffic Spend Window
- Days 1-30: All traffic budget spent
- Days 31-365: $0 new spend, pure retention

### CPA Parameters
```python
cpa_range: tuple = (55, 75)  # USD, based on real data
# Historical reference: Aug=$54.53, Oct=$69.12, Current=$72.54
# Generate random CPA within range for each cohort
```

### FTD Calculation
```python
total_ftds = traffic_budget / random_cpa
# where random_cpa is uniformly distributed in [55, 75]
# Add daily variance: some days acquire more FTDs than others
```

### First Deposit
```python
first_deposit_range = (20, 28)  # USD
variance = 0.2  # ±20% daily variance
```

## Retention Model

### Daily Retention Rates (from FTD date)
```python
retention_schedule = {
    (1, 30): 1.00,      # 100% during first month
    (31, 60): 0.42,     # Month 2: 42% ±3%
    (61, 90): 0.33,     # Month 3: 33% ±3%
    (91, 120): 0.26,    # Month 4: 26% ±2%
    (121, 150): 0.22,   # Month 5: 22% ±2%
    (151, 180): 0.19,   # Month 6: 19% ±2%
    (181, 210): 0.16,   # Month 7: 16% ±2%
    (211, 240): 0.14,   # Month 8: 14% ±2%
    (241, 270): 0.12,   # Month 9: 12% ±2%
    (271, 300): 0.10,   # Month 10: 10% ±1.5%
    (301, 330): 0.09,   # Month 11: 9% ±1.5%
    (331, 365): 0.08,   # Month 12: 8% ±1%
}
# Apply random variance each day within specified ranges
```

## Average Deposit Growth Model

### Base Deposits by Cohort Age
```python
deposit_by_days = {
    (1, 30): 23,        # First deposits
    (31, 60): 49,       # Early retention
    (61, 90): 66,       # Growing engagement
    (91, 120): 81,      # Established players
    (121, 150): 91,     # Loyal cohort
    (151, 180): 101,    # High value
    (181, 210): 108,    # Whales emerging
    (211, 240): 115,    # Premium players
    (241, 270): 121,    # Top tier
    (271, 300): 125,    # Mature whales
    (301, 330): 129,    # Long-term high rollers
    (331, 365): 132,    # Peak value
}
# Apply variance: base * (0.85 + random(0.30))
```

### Seasonality Multipliers
```python
seasonality = {
    'christmas': {'dates': ['12-20' to '12-31'], 'mult': 1.18},
    'new_year': {'dates': ['01-01' to '01-10'], 'mult': 1.15},
    'valentines': {'date': '02-14', 'mult': 1.08},
    'world_cup': {'months': [6, 7], 'mult': 1.12},  # if applicable
    'summer_peak': {'months': [7, 8], 'mult': 1.06},
    'back_to_school': {'month': 9, 'mult': 0.92},
    'february_slump': {'month': 2, 'mult': 0.94},
    'weekends': {'days': ['Sat', 'Sun'], 'mult': 1.08},
    'paydays': {'dates': ['monthly 25-28'], 'mult': 1.12},
}
```

## GGR Calculation (Critical)

### Daily GGR Formula
```python
daily_deposits = active_players * avg_deposit_for_cohort_age
daily_ggr = daily_deposits * ggr_margin * daily_variance

ggr_margin = 0.88  # 88% house edge (constant)
daily_variance = normal_distribution(mean=1.0, std=0.05)  # ±5% daily volatility

# GGR can be NEGATIVE on some days (players win)
# But ensure cumulative GGR trends positive
```

### Target GGR Constraint
```python
# Year-end target: cumulative_ggr ≈ pool_size × 3.0
# Allow variance: actual multiplier between 2.7x - 3.3x
target_ggr_range = (pool_size * 2.7, pool_size * 3.3)

# Use calibration loop to adjust parameters if needed:
# - Tune retention rates
# - Tune deposit growth curve  
# - Tune CPA to get optimal FTD count
```

## Payout Calculations

### Daily Payouts by Pool
```python
# Weighted average rates (based on capital distribution)
stable_weighted_rate = (
    0.30 * 0.34 +      # 30% capital in basic
    0.40 * 0.3825 +    # 40% capital in advanced
    0.30 * 0.425       # 30% capital in premium
) = 0.3808  # ~38.08%

growth_weighted_rate = (
    0.30 * 0.085 +     # 30% capital in basic
    0.40 * 0.10625 +   # 40% capital in advanced
    0.30 * 0.1275      # 30% capital in premium
) = 0.1069  # ~10.69%

daily_stable_payout = max(0, daily_ggr * stable_weighted_rate)
daily_growth_payout = max(0, daily_ggr * growth_weighted_rate)

# Note: If daily_ggr is negative, payouts = 0 for that day
```

### Cumulative Tracking
```python
cumulative_ggr = sum(daily_ggr for all days)
cumulative_stable = sum(daily_stable_payout)
cumulative_growth = sum(daily_growth_payout)

stable_return_pct = (cumulative_stable / stable_pool_size) * 100
growth_return_pct = (cumulative_growth / growth_pool_size) * 100
```

## Output Requirements

### Daily DataFrame Columns
```python
columns = [
    'date',                    # datetime
    'day',                     # 1-365
    'month',                   # 1-12
    'day_of_week',            # Mon-Sun
    'new_ftds',               # int (only Days 1-30)
    'active_players',         # int
    'avg_deposit',            # float
    'total_deposits',         # float
    'daily_ggr',              # float (can be negative!)
    'cumulative_ggr',         # float
    'stable_payout',          # float
    'growth_payout',          # float
    'cumulative_stable',      # float
    'cumulative_growth',      # float
    'stable_return_pct',      # float
    'growth_return_pct',      # float (cash only)
    'traffic_spend',          # float (only Days 1-30)
    'cumulative_traffic',     # float
    'ggr_multiplier',         # cumulative_ggr / pool_size
]
```

### Tier-Level Returns Output
```python
# Must show per-dollar returns for each tier
tier_returns = {
    'stable': {
        'basic': {
            'invested': float,
            'received': float,
            'return_pct': float,  # Must be >100% (includes capital)
            'profit_pct': float,   # Return - 100%
            'per_dollar': float,   # received / invested
        },
        'advanced': {...},
        'premium': {...},
    },
    'growth': {
        'basic': {
            'invested': float,
            'cash_received': float,
            'tokens_returned': float,  # 100% of invested ZNX
            'cash_return_pct': float,
            'total_return_pct': float,  # if ZNX price stays same
            'per_dollar_cash': float,
            'per_dollar_total': float,  # including token value
        },
        'advanced': {...},
        'premium': {...},
    }
}

# VALIDATION: Every tier must show positive returns
# Stable basic (34%): must achieve >100% return
# All others: must show meaningful profit
```

## Class Structure

```python
class RevSharePoolGenerator:
    def __init__(
        self,
        pool_size: int = 35000,
        stable_ratio: float = 0.6,
        growth_ratio: float = 0.4,
        traffic_budget: int = 35000,
        start_date: str = "2025-11-01",
        cpa_range: tuple = (55, 75),
        target_ggr_multiplier: float = 3.0,
        seed: int = None  # for reproducibility
    ):
        """Initialize pool generator with configuration"""
        
    def _calculate_investor_distribution(self) -> dict:
        """Apply Pareto distribution to investor tiers"""
        
    def _generate_ftd_schedule(self) -> pd.DataFrame:
        """Generate FTD acquisition for Days 1-30"""
        
    def _get_retention_rate(self, days_since_ftd: int) -> float:
        """Get retention rate with variance for specific day"""
        
    def _get_avg_deposit(self, days_since_ftd: int, date: datetime) -> float:
        """Calculate average deposit with cohort age and seasonality"""
        
    def _calculate_seasonality(self, date: datetime) -> float:
        """Return seasonality multiplier for given date"""
        
    def _calculate_daily_ggr(self, active_players: int, avg_deposit: float) -> float:
        """Calculate daily GGR with house edge and variance"""
        
    def generate_daily_data(self) -> pd.DataFrame:
        """
        Main generation method - produces 365 days of data
        Returns DataFrame with all required columns
        """
        
    def calibrate_to_target_ggr(self, tolerance: float = 0.1) -> None:
        """
        Iteratively adjust parameters to hit target GGR multiplier
        Tolerance: acceptable deviation from target (e.g., 0.1 = ±10%)
        """
        
    def calculate_tier_returns(self) -> dict:
        """
        Calculate final returns for each investor tier
        Ensures all tiers show positive returns
        """
        
    def get_monthly_summary(self) -> pd.DataFrame:
        """Aggregate daily data into monthly view"""
        
    def validate_results(self) -> dict:
        """
        Validate generated data:
        - GGR multiplier in target range
        - All tiers profitable
        - Monotonic cumulative metrics
        - No impossible values
        """
        
    def export_to_csv(self, prefix: str = "pool1") -> None:
        """Export daily data and summaries to CSV files"""
        
    def plot_dashboard(self, save_path: str = None) -> None:
        """
        Create visualization dashboard:
        - Daily GGR over time
        - Active players decay
        - Cumulative returns by pool
        - Tier comparison
        """
```

## Calibration Algorithm

```python
def calibrate_to_target_ggr(self, tolerance=0.1):
    """
    Iterative calibration to achieve target GGR multiplier
    
    Steps:
    1. Generate initial data with default parameters
    2. Check cumulative GGR vs target
    3. If too low: increase retention OR deposits OR FTDs
    4. If too high: decrease retention OR deposits OR FTDs
    5. Repeat until within tolerance
    
    Priority adjustments (in order):
    - FTD count (adjust CPA to control acquisition)
    - Retention rates (boost/reduce by ±5%)
    - Deposit growth curve (scale up/down by ±10%)
    """
    max_iterations = 20
    for iteration in range(max_iterations):
        daily_data = self.generate_daily_data()
        actual_multiplier = daily_data['cumulative_ggr'].iloc[-1] / self.pool_size
        
        if abs(actual_multiplier - self.target_ggr_multiplier) < tolerance:
            break
            
        # Adjust parameters based on deviation
        # ...
```

## Validation Rules

### Must-Pass Checks
1. **GGR Multiplier**: 2.7x ≤ final_ggr/pool_size ≤ 3.3x
2. **Stable Returns**: All tiers > 100% (basic must clear 100%+ minimum)
3. **Growth Returns**: All tiers show positive cash + tokens
4. **Monotonic Cumulative**: cumulative_ggr never decreases
5. **Active Players**: Only decrease after Day 30 (no new acquisition)
6. **No Negatives**: No negative active_players or cumulative values
7. **Payout Ratio**: total_payouts < cumulative_ggr (can't pay more than earned)

### Per-Tier Profitability
```python
# Minimum acceptable returns:
stable_basic_min = 1.15      # 115% (100% capital + 15% profit)
stable_advanced_min = 1.22   # 122%
stable_premium_min = 1.30    # 130%

growth_basic_min = 0.15      # 15% cash (plus 100% tokens)
growth_advanced_min = 0.20   # 20% cash
growth_premium_min = 0.27    # 27% cash
```

## Usage Example

```python
# Initialize generator
gen = RevSharePoolGenerator(
    pool_size=35000,
    traffic_budget=35000,
    start_date="2025-11-01",
    cpa_range=(55, 75),
    target_ggr_multiplier=2.9,
    seed=42
)

# Auto-calibrate
gen.calibrate_to_target_ggr(tolerance=0.1)

# Generate data
daily_df = gen.generate_daily_data()
monthly_df = gen.get_monthly_summary()
tier_returns = gen.calculate_tier_returns()

# Validate
validation = gen.validate_results()
assert validation['passed'], f"Validation failed: {validation['errors']}"

# Export
gen.export_to_csv(prefix="pool1_nov2025")

# Print summary
print(f"Final GGR: ${daily_df['cumulative_ggr'].iloc[-1]:,.0f}")
print(f"Multiplier: {daily_df['ggr_multiplier'].iloc[-1]:.2f}x")
print("\nStable Pool Returns:")
for tier, data in tier_returns['stable'].items():
    print(f"  {tier}: {data['return_pct']:.1f}% (${data['per_dollar']:.2f} per $1)")
print("\nGrowth Pool Returns (cash):")
for tier, data in tier_returns['growth'].items():
    print(f"  {tier}: {data['cash_return_pct']:.1f}% + tokens (${data['per_dollar_cash']:.2f} per $1)")
```

## Additional Features

### Scenario Comparison
```python
def compare_scenarios(configs: List[dict]) -> pd.DataFrame:
    """Compare multiple pool configurations side-by-side"""
```

### Sensitivity Analysis
```python
def sensitivity_analysis(parameter: str, range: tuple) -> dict:
    """Test impact of parameter changes on final returns"""
```

### Referral Costs (Optional)
```python
referral_config = {
    'percentage': 0.30,  # 30% of investors via referral
    'upfront_bonus': 0.03,  # 3% of investment
    'monthly_share_stable': 0.04,  # 4% of monthly payout
    'monthly_share_growth': 0.15,  # 15% of monthly payout
}
# Subtract referral costs from business margin
```

---

## 🔒 Безопасность

Проект настроен с учетом лучших практик безопасности:

- ✅ Все чувствительные данные исключены из репозитория
- ✅ Настроен `.gitignore` для защиты конфиденциальной информации
- ✅ Конфигурация Streamlit оптимизирована для продакшена
- ✅ Отключена сбор статистики использования

## 📁 Структура проекта

```
calculator/
├── dashboard_app.py          # Основное приложение Streamlit
├── revshare_pool.py         # Логика расчетов пулов
├── requirements.txt         # Зависимости Python
├── readme.md               # Документация
├── .gitignore              # Исключения Git
├── .streamlit/             # Конфигурация Streamlit
│   ├── config.toml         # Настройки приложения
│   └── secrets.toml        # Секретные данные (не в Git)
├── project_analysis.md     # Техническая документация
└── *.csv                   # Примеры данных
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Поддержка

Если у вас есть вопросы или предложения, создайте [Issue](https://github.com/DaniilKozin/calculator/issues) в репозитории.

---

## Key Requirements Summary

1. ✅ 365 daily rows with all metrics
2. ✅ GGR can be negative on individual days
3. ✅ Cumulative GGR ~3x pool size (±10%)
4. ✅ CPA random in [55, 75] range
5. ✅ Traffic only in Days 1-30
6. ✅ Pareto distribution for investor tiers
7. ✅ All tiers must be profitable
8. ✅ Stable basic (34%) must return >100%
9. ✅ Per-dollar returns for each tier
10. ✅ Auto-calibration to hit target GGR
11. ✅ CSV export capability
12. ✅ Validation checks

Build this class with proper type hints, docstrings, and error handling!