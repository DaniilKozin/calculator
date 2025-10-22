import os
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

DAILY_CSV = "pool1_nov2025_daily.csv"
MONTHLY_CSV = "pool1_nov2025_monthly.csv"
MONTHLY_TIERS_ZNX_CSV = "pool1_nov2025_monthly_tiers_znx.csv"

# Default values (will be overridden by sidebar)
DEFAULT_POOL_SIZE = 50000
DEFAULT_STABLE_RATIO = 0.6
DEFAULT_GROWTH_RATIO = 0.4

st.set_page_config(page_title="RevShare Pool Dashboard", layout="wide")

# Sidebar for data generation
st.sidebar.title("🔧 Генерация данных")
st.sidebar.info("ℹ️ Параметры ниже используются только для генерации новых данных. Дашборд отображает реальные данные из CSV файлов.")
st.sidebar.markdown("### Параметры пула")

# Pool parameters (only for data generation)
pool_size = st.sidebar.number_input("💰 Размер пула ($)", min_value=10000, max_value=1000000, value=50000, step=5000, help="Используется только для генерации новых данных")
stable_ratio = st.sidebar.slider("🔵 Stable пул (%)", min_value=0.1, max_value=0.9, value=0.5, step=0.05, help="Используется только для генерации новых данных")
growth_ratio = 1.0 - stable_ratio

# Date and target parameters
from datetime import datetime, date
start_date = st.sidebar.date_input("📅 Дата старта", value=date(2025, 11, 1), help="Используется только для генерации новых данных")
target_ggr = st.sidebar.slider("🎯 Целевой GGR множитель", min_value=2.0, max_value=5.0, value=3.2, step=0.1, help="Используется только для генерации новых данных")
ggr_volatility = st.sidebar.slider("📊 Волатильность GGR", min_value=0.05, max_value=0.30, value=0.15, step=0.01, help="Стандартное отклонение для ежедневных колебаний GGR. Используется только для генерации новых данных")

# Referral parameters
st.sidebar.markdown("### Реферальная программа")
referral_ratio = st.sidebar.slider("🤝 Доля рефералов (%)", min_value=0.0, max_value=50.0, value=0.0, step=5.0, help="Процент инвесторов, пришедших по реферальным ссылкам. Используется только для генерации новых данных")

st.sidebar.markdown("#### Единовременные бонусы")
upfront_bonus_stable = st.sidebar.slider("💰 Stable бонус (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.5, help="Процент от реферального капитала в Stable пуле, выплачиваемый единовременно")
upfront_bonus_growth = st.sidebar.slider("💰 Growth бонус (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.5, help="Процент от реферального капитала в Growth пуле, выплачиваемый единовременно")

st.sidebar.markdown("#### Постоянные выплаты")
ongoing_share_stable = st.sidebar.slider("📈 Stable доля (%)", min_value=0.0, max_value=20.0, value=4.0, step=1.0, help="Процент от выплат Stable инвесторам, выплачиваемый рефералам")
ongoing_share_growth = st.sidebar.slider("📈 Growth доля (%)", min_value=0.0, max_value=30.0, value=15.0, step=1.0, help="Процент от выплат Growth инвесторам, выплачиваемый рефералам")


# Traffic parameters
st.sidebar.markdown("### Трафик")
cpa_min = st.sidebar.number_input("💸 CPA мин ($)", min_value=10, max_value=500, value=50, step=5, help="Базовая стоимость привлечения клиента (без учета реферальных расходов)")
cpa_max = st.sidebar.number_input("💸 CPA макс ($)", min_value=cpa_min, max_value=1000, value=150, step=5, help="Максимальная стоимость привлечения клиента (без учета реферальных расходов)")

# Calculate effective CPA ranges including referral costs
if referral_ratio > 0:
    # Referral costs reduce available traffic budget
    referral_cost_factor = 1 + (referral_ratio / 100) * 0.1  # 10% additional cost per referral
    effective_cpa_min = cpa_min * referral_cost_factor
    effective_cpa_max = cpa_max * referral_cost_factor
    
    st.sidebar.markdown(f"**Эффективный CPA с рефералкой:**")
    st.sidebar.markdown(f"• Мин: ${effective_cpa_min:.1f} (+{((referral_cost_factor-1)*100):.1f}%)")
    st.sidebar.markdown(f"• Макс: ${effective_cpa_max:.1f} (+{((referral_cost_factor-1)*100):.1f}%)")
else:
    effective_cpa_min = cpa_min
    effective_cpa_max = cpa_max

# Data loading function (defined before generation logic)
@st.cache_data(show_spinner=False)
def load_data():
    daily = pd.read_csv(DAILY_CSV, parse_dates=["date"]) if os.path.exists(DAILY_CSV) else None
    monthly = pd.read_csv(MONTHLY_CSV) if os.path.exists(MONTHLY_CSV) else None
    tiers = pd.read_csv(MONTHLY_TIERS_ZNX_CSV) if os.path.exists(MONTHLY_TIERS_ZNX_CSV) else None
    return daily, monthly, tiers

generate_button = st.sidebar.button("🚀 Генерировать данные", type="primary")

# Generate data if button is clicked
if generate_button:
    with st.spinner("Генерирую данные..."):
        from revshare_pool import RevSharePoolGenerator
        import os
        import random
        import time
        
        # Generate random seed based on current time and parameters
        seed = int(time.time() * 1000) % 1000000 + hash(str(pool_size) + str(stable_ratio) + str(target_ggr)) % 1000
        random.seed(seed)
        np.random.seed(seed)
        
        # Create generator with custom parameters
        generator = RevSharePoolGenerator(
            pool_size=pool_size,
            stable_ratio=stable_ratio,
            growth_ratio=growth_ratio,
            cpa_range=(effective_cpa_min, effective_cpa_max),
            target_ggr_multiplier=target_ggr,
            ggr_volatility=ggr_volatility,
            referral_ratio=referral_ratio / 100.0,  # Convert percentage to decimal
            upfront_bonus_stable=upfront_bonus_stable / 100.0,
            upfront_bonus_growth=upfront_bonus_growth / 100.0,
            ongoing_share_stable=ongoing_share_stable / 100.0,
            ongoing_share_growth=ongoing_share_growth / 100.0,
            start_date=start_date.strftime("%Y-%m-%d")
        )
        
        # Calibrate to target GGR multiplier
        generator.calibrate_to_target_ggr(tolerance=0.1)
        
        # Generate data
        daily_data = generator.generate_daily_data()
        monthly_data = generator.get_monthly_summary(daily_data)
        monthly_tiers_data = generator.get_monthly_tier_payouts_per_znx(daily_data)
        
        # Save to CSV files
        daily_data.to_csv(DAILY_CSV, index=False)
        monthly_data.to_csv(MONTHLY_CSV, index=False)
        monthly_tiers_data.to_csv(MONTHLY_TIERS_ZNX_CSV, index=False)
        
        # Clear cache to force data reload
        load_data.clear()
        
        st.sidebar.success("✅ Данные сгенерированы!")
        st.rerun()

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-metric {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    .warning-metric {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
    }
    .info-metric {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Load data using the function defined earlier
daily_df, monthly_df, tiers_df = load_data()

if daily_df is None or monthly_df is None:
    st.warning("CSV файлы не найдены. Запустите run.py для генерации данных.")
    st.stop()

def display_tier_returns(ggr_multiplier):
    """Show per-dollar returns for each tier"""
    
    st.subheader("💰 Returns Per $1 Invested")
    
    cols = st.columns(2)
    
    with cols[0]:
        st.markdown("**Stable Pool** (no tokens back)")
        for tier, rate in [('Basic', 0.34), ('Advanced', 0.3825), ('Premium', 0.425)]:
            per_dollar = ggr_multiplier * rate
            profit_pct = (per_dollar - 1) * 100
            
            color = "🟢" if per_dollar >= 1.0 else "🔴"
            st.metric(
                f"{color} {tier} ({rate*100:.2f}%)",
                f"${per_dollar:.3f}",
                f"{profit_pct:+.1f}%"
            )
    
    with cols[1]:
        st.markdown("**Growth Pool** (+ 100% tokens)")
        for tier, rate in [('Basic', 0.085), ('Advanced', 0.10625), ('Premium', 0.1275)]:
            cash_per_dollar = ggr_multiplier * rate
            total_per_dollar = cash_per_dollar + 1.0
            
            st.metric(
                f"🟢 {tier} ({rate*100:.2f}%)",
                f"${total_per_dollar:.3f}",
                f"${cash_per_dollar:.3f} cash"
            )

# Calculate real pool size and ratios from data first
final_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
ggr_multiplier = float(daily_df["ggr_multiplier"].iloc[-1])
real_pool_size = final_ggr / ggr_multiplier if ggr_multiplier > 0 else DEFAULT_POOL_SIZE

# Get real stable ratio from data - use standard 60/40 split
# Since we don't have investment columns, use the standard ratio
real_stable_ratio = 0.6  # 60% Stable
real_growth_ratio = 0.4  # 40% Growth

st.title("💰 RevShare Pool Dashboard")
st.markdown(f"### Анализ доходности пулов Zenex с размером ${real_pool_size:,.0f}")
st.markdown(f"**🔵 Stable:** {real_stable_ratio:.0%} | **🟢 Growth:** {real_growth_ratio:.0%}")

# Cumulative summary metrics at the top
st.subheader("💼 Совокупные показатели")
total_collected = real_pool_size

# Calculate actual cash payouts from real data only (no artificial corrections)
total_stable_payout = float(monthly_df["stable_payout"].sum())
total_growth_payout = float(monthly_df["growth_payout"].sum())

# Total cash paid = only real payouts from CSV data
total_cash_paid = total_stable_payout + total_growth_payout
final_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
ggr_multiplier = final_ggr / total_collected if total_collected > 0 else 0

col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)
with col_summary1:
    st.metric("💰 Собрано", f"${total_collected:,.0f}", delta="Общий размер пула")
with col_summary2:
    st.metric("💸 Cash выплаты", f"${total_cash_paid:,.0f}", delta="Только денежные выплаты")
with col_summary3:
    color_indicator = "🟢" if ggr_multiplier >= 3.0 else "🟡" if ggr_multiplier >= 2.5 else "🔴"
    st.metric(f"{color_indicator} GGR множитель", f"{ggr_multiplier:.2f}x", delta="Эффективность пула")
with col_summary4:
    if stable_correction_needed > 0:
        st.metric("🔧 Корректировка", f"${stable_correction_needed:,.0f}", delta="Доплата до $1 за Stable")
    else:
        st.metric("✅ Корректировка", "$0", delta="Доплата не требуется")

st.markdown("---")

# Key metrics
st.subheader("📊 Ключевые показатели")

# First row - main metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Raised", f"${real_pool_size:,.0f}", delta=None)
with col2:
    spent = float(daily_df["cumulative_traffic"].iloc[-1])
    efficiency = (spent / real_pool_size) * 100
    st.metric("📈 Spent (Traffic)", f"${spent:,.0f}", delta=f"{efficiency:.1f}% от пула")
with col3:
    ftds = int(daily_df["new_ftds"].sum())
    st.metric("👥 FTD", f"{ftds}", delta="First-Time Depositors")

# Second row - additional metrics
col4, col5, col6 = st.columns(3)
with col4:
    avg_cpa = spent / max(1, ftds)
    st.metric("💸 CPA", f"${avg_cpa:,.2f}", delta="Cost per FTD")
with col5:
    # Use the correct column name from the new referral system implementation
    if "monthly_referral_cost" in monthly_df.columns:
        referral_total = float(monthly_df["monthly_referral_cost"].sum())
    elif "referral_paid_usd" in monthly_df.columns:
        referral_total = float(monthly_df["referral_paid_usd"].sum())
    else:
        referral_total = 0.0
    st.metric("🤝 Referral", f"${referral_total:,.0f}", delta="Payouts")
with col6:
    # Пустая колонка для баланса
    st.write("")

# Display tier returns
display_tier_returns(ggr_multiplier)

# Breakeven metrics
st.subheader("⚖️ Метрики безубыточности")
col1, col2, col3 = st.columns(3)

# Calculate GGR multiplier and breakeven metrics
min_ggr_multiplier_for_basic = 1 / 0.34  # = 2.94x for Stable Basic breakeven
is_breakeven = ggr_multiplier >= min_ggr_multiplier_for_basic

with col1:
    color = "🟢" if is_breakeven else "🔴"
    st.metric(f"{color} Min GGR for Stable Basic Breakeven", f"{min_ggr_multiplier_for_basic:.2f}x", 
              delta=f"Текущий: {ggr_multiplier:.2f}x", 
              help="Stable Basic (34% rate) needs 2.94x GGR to return 100% capital")
with col2:
    color = "🟢" if final_ggr >= real_pool_size * 2.5 else "🔴"
    st.metric(f"{color} Total GGR", f"${final_ggr:,.0f}", 
              delta=f"{ggr_multiplier:.2f}x множитель")
with col3:
    status = "✅ Безубыточность" if is_breakeven else "❌ Убыток"
    st.metric("📊 Статус", status, delta=None)

st.divider()

# GGR chart and total
left, right = st.columns([2, 1])
with left:
    st.subheader("📈 Динамика GGR")
    # Create a more sophisticated chart with gradient
    ggr_chart = alt.Chart(daily_df).mark_area(
        line={'color': '#1f77b4'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='#e1f5fe', offset=0),
                   alt.GradientStop(color='#1f77b4', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X("date:T", axis=alt.Axis(title="Дата", labelAngle=-45)),
        y=alt.Y("cumulative_ggr:Q", axis=alt.Axis(title="Накопительный GGR (USD)"))
    ).properties(height=300)
    st.altair_chart(ggr_chart, use_container_width=True)

with right:
    st.subheader("💎 Total GGR")
    total_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
    multiplier = total_ggr / pool_size
    st.metric("💰 GGR", f"${total_ggr:,.0f}", delta=f"{multiplier:.2f}x множитель")
    
    # ROI indicator
    if multiplier >= 3.0:
        st.success(f"🎯 Цель достигнута! {multiplier:.2f}x")
    elif multiplier >= 2.0:
        st.warning(f"⚠️ Близко к цели: {multiplier:.2f}x")
    else:
        st.error(f"❌ Ниже цели: {multiplier:.2f}x")



st.divider()

# Monthly payouts per pool (bar chart)
st.subheader("📊 Ежемесячные выплаты по пулам")
monthly_df_display = monthly_df.copy()
monthly_df_display["date"] = pd.to_datetime(monthly_df_display[["year", "month"]].assign(day=1))
payouts_melt = monthly_df_display[["date", "stable_payout", "growth_payout"]].melt("date", var_name="pool", value_name="payout")
payouts_melt["payout"] = payouts_melt["payout"].clip(lower=0)

# Rename pools for better display
payouts_melt["pool"] = payouts_melt["pool"].map({
    "stable_payout": "🔵 Stable",
    "growth_payout": "🟢 Growth"
})

monthly_chart = alt.Chart(payouts_melt).mark_bar().encode(
    x=alt.X("pool:N", axis=alt.Axis(title="Пул")),
    y=alt.Y("payout:Q", axis=alt.Axis(title="Выплата (USD)")),
    color=alt.Color("pool:N", 
                   scale=alt.Scale(range=["#2196F3", "#4CAF50"]),
                   legend=alt.Legend(title="Пул")),
    column=alt.Column("date:T", header=alt.Header(labelAngle=-45, title="Месяц"))
).properties(
    width=120,
    height=200
).resolve_scale(
    x='independent'
)
st.altair_chart(monthly_chart, use_container_width=False)

st.divider()

# Daily table with key metrics
st.subheader("📅 Ежедневные ключевые показатели")
daily_cols = [
    "date",
    "new_ftds",
    "active_players", 
    "total_deposits",
    "daily_ggr",
    "ggr_multiplier",
    "traffic_spend",
    "cumulative_ggr",
]

# Format the dataframe for better display
daily_display = daily_df[daily_cols].copy()
daily_display.columns = [
    "📅 Дата",
    "👥 Новые FTD", 
    "🎮 Активные игроки",
    "💰 Общие депозиты",
    "📈 Дневной GGR",
    "🎯 GGR множитель",
    "📊 Трафик расходы",
    "📊 Накопительный GGR"
]

st.dataframe(daily_display, use_container_width=True, hide_index=True)

st.divider()

# Monthly per-ZNX table
st.subheader("Ежемесячные выплаты на 1 ZNX (6 сценариев: 2 пула × 3 тира)")

# Explanation of the table
st.info("""
**Объяснение таблицы:**
- **cash_usd** - денежная выплата в долларах за 1 ZNX токен
- **total_usd** - общая стоимость выплаты за 1 ZNX (только cash выплаты, без учета возврата токенов)
- **Stable пул**: выплачивает только деньги (% от GGR). Важно покрыть стоимость тела к USD при изменении цены токена
- **Growth пул**: выплачивает только cash (% от GGR). Возврат токенов не учитывается в расчетах
- **Тиры**: Bronze (basic), Silver (advanced), Gold (premium) - разные уровни доходности
- **Минимальный порог**: 295% GGR/Spent для выхода в ноль, 34% минимум для Stable пула
""")

if tiers_df is None:
    st.info("Запустите run.py, чтобы сгенерировать таблицу выплат по ZNX: pool1_nov2025_monthly_tiers_znx.csv")
else:
    tiers_df_display = tiers_df.copy()
    tiers_df_display["date"] = pd.to_datetime(tiers_df_display[["year", "month"]].assign(day=1))
    st.dataframe(
        tiers_df_display[["date", "pool", "tier", "per_znx_cash_usd", "per_znx_total_usd"]],
        use_container_width=True,
        hide_index=True,
    )

    # Chart for per-ZNX payouts
    tiers_df_display["pool_display"] = tiers_df_display["pool"].map({
        "stable": "🔵 Stable",
        "growth": "🟢 Growth"
    })
    
    znx_chart = alt.Chart(tiers_df_display).mark_bar().encode(
        x=alt.X("pool_display:N", axis=alt.Axis(title="Пул")),
        y=alt.Y("per_znx_total_usd:Q", axis=alt.Axis(title="USD за 1 ZNX (total)")),
        color=alt.Color("pool_display:N", 
                       scale=alt.Scale(range=["#2196F3", "#4CAF50"]),
                       legend=alt.Legend(title="Пул")),
        column=alt.Column("tier:N", header=alt.Header(title="Тир"))
    ).properties(
        width=120,
        height=200
    ).resolve_scale(
        x='independent'
    )
    st.altair_chart(znx_chart, use_container_width=False)

# Add summary table for return per dollar invested
st.divider()
st.subheader("💰 Итоговая доходность: возврат на каждый вложенный доллар")

# Use CORRECT values from CSV data that includes proper tier calculations
if daily_df is not None and monthly_df is not None and tiers_df is not None:
    # Get final values from CSV
    final_ggr = daily_df["cumulative_ggr"].iloc[-1]
    ggr_multiplier = final_ggr / real_pool_size
    
    # Pool allocations (capital shares)
    stable_basic_invested = real_pool_size * real_stable_ratio * 0.5
    stable_advanced_invested = real_pool_size * real_stable_ratio * 0.3
    stable_premium_invested = real_pool_size * real_stable_ratio * 0.2
    
    growth_basic_invested = real_pool_size * real_growth_ratio * 0.5
    growth_advanced_invested = real_pool_size * real_growth_ratio * 0.3
    growth_premium_invested = real_pool_size * real_growth_ratio * 0.2
    
    # NEW FORMULAS - Stable Pool (NO tokens returned)
    # Stable: payout = investment × GGR_multiplier × tier_rate
    stable_basic_received = stable_basic_invested * ggr_multiplier * 0.34
    stable_advanced_received = stable_advanced_invested * ggr_multiplier * 0.3825
    stable_premium_received = stable_premium_invested * ggr_multiplier * 0.425
    
    # NEW FORMULAS - Growth Pool (100% tokens RETURNED)
    # Growth: total = (investment × GGR_multiplier × tier_rate) + investment
    growth_basic_cash = growth_basic_invested * ggr_multiplier * 0.085
    growth_advanced_cash = growth_advanced_invested * ggr_multiplier * 0.10625
    growth_premium_cash = growth_premium_invested * ggr_multiplier * 0.1275
    
    growth_basic_total = growth_basic_cash + growth_basic_invested  # cash + tokens
    growth_advanced_total = growth_advanced_cash + growth_advanced_invested  # cash + tokens
    growth_premium_total = growth_premium_cash + growth_premium_invested  # cash + tokens
    
    # Per dollar calculations
    stable_basic_per_dollar = ggr_multiplier * 0.34
    stable_advanced_per_dollar = ggr_multiplier * 0.3825
    stable_premium_per_dollar = ggr_multiplier * 0.425
    
    growth_basic_per_dollar = (ggr_multiplier * 0.085) + 1.00
    growth_advanced_per_dollar = (ggr_multiplier * 0.10625) + 1.00
    growth_premium_per_dollar = (ggr_multiplier * 0.1275) + 1.00
    
    # Create summary table
    summary_data = {
        "Пул": [
            "🔵 Stable Basic (34%)", "🔵 Stable Advanced (38.25%)", "🔵 Stable Premium (42.5%)",
            "🟢 Growth Basic (8.5%)", "🟢 Growth Advanced (10.625%)", "🟢 Growth Premium (12.75%)"
        ],
        "Вложено ($)": [
            f"${stable_basic_invested:,.0f}",
            f"${stable_advanced_invested:,.0f}",
            f"${stable_premium_invested:,.0f}",
            f"${growth_basic_invested:,.0f}",
            f"${growth_advanced_invested:,.0f}",
            f"${growth_premium_invested:,.0f}"
        ],
        "Получено ($)": [
            f"${stable_basic_received:,.0f}",
            f"${stable_advanced_received:,.0f}",
            f"${stable_premium_received:,.0f}",
            f"${growth_basic_total:,.0f}",
            f"${growth_advanced_total:,.0f}",
            f"${growth_premium_total:,.0f}"
        ],
        "На $1 получаешь": [
            f"${stable_basic_per_dollar:.2f}",
            f"${stable_advanced_per_dollar:.2f}",
            f"${stable_premium_per_dollar:.2f}",
            f"${growth_basic_per_dollar:.2f}",
            f"${growth_advanced_per_dollar:.2f}",
            f"${growth_premium_per_dollar:.2f}"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Add explanation
    st.info("""
    **📊 Правильная формула расчетов:**
    - **Stable пул**: `payout = investment × GGR_multiplier × tier_rate`
    - **Growth пул**: `total = (investment × GGR_multiplier × tier_rate) + investment`
    - **Stable тиры**: Basic (34%), Advanced (38.25%), Premium (42.5%)
    - **Growth тиры**: Basic (8.5%), Advanced (10.625%), Premium (12.75%)
    - **Распределение капитала**: Basic 30%, Advanced 40%, Premium 30%
    - **Возврат на $1 (Stable)**: `GGR_множитель × tier_rate`
    - **Возврат на $1 (Growth)**: `(GGR_множитель × tier_rate) + 1.00`
    """)
else:
    st.warning("Сгенерируйте данные для просмотра итоговой доходности")

st.caption("Built with Streamlit + Altair")