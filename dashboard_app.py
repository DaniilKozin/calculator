import os
import json
import shutil
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from datetime import datetime, date

DAILY_CSV = "pool1_nov2025_daily.csv"
MONTHLY_CSV = "pool1_nov2025_monthly.csv"
MONTHLY_TIERS_ZNX_CSV = "pool1_nov2025_monthly_tiers_znx.csv"
SAVED_RESULTS_DIR = "saved_results"
SAVED_PARAMS_FILE = "generation_params.json"

# Default values (will be overridden by sidebar)
DEFAULT_POOL_SIZE = 50000
DEFAULT_STABLE_RATIO = 0.6
DEFAULT_GROWTH_RATIO = 0.4

# Functions for saving and loading generation results
def save_generation_result(params, name):
    """Сохранить результат генерации с параметрами"""
    if not os.path.exists(SAVED_RESULTS_DIR):
        os.makedirs(SAVED_RESULTS_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(SAVED_RESULTS_DIR, f"{timestamp}_{name}")
    os.makedirs(result_dir, exist_ok=True)
    
    # Сохранить параметры
    params_file = os.path.join(result_dir, SAVED_PARAMS_FILE)
    with open(params_file, 'w', encoding='utf-8') as f:
        json.dump(params, f, ensure_ascii=False, indent=2, default=str)
    
    # Скопировать CSV файлы
    import shutil
    if os.path.exists(DAILY_CSV):
        shutil.copy2(DAILY_CSV, os.path.join(result_dir, DAILY_CSV))
    if os.path.exists(MONTHLY_CSV):
        shutil.copy2(MONTHLY_CSV, os.path.join(result_dir, MONTHLY_CSV))
    if os.path.exists(MONTHLY_TIERS_ZNX_CSV):
        shutil.copy2(MONTHLY_TIERS_ZNX_CSV, os.path.join(result_dir, MONTHLY_TIERS_ZNX_CSV))
    
    return result_dir

def get_saved_results():
    """Получить список сохраненных результатов"""
    if not os.path.exists(SAVED_RESULTS_DIR):
        return []
    
    results = []
    for item in os.listdir(SAVED_RESULTS_DIR):
        result_path = os.path.join(SAVED_RESULTS_DIR, item)
        if os.path.isdir(result_path):
            params_file = os.path.join(result_path, SAVED_PARAMS_FILE)
            if os.path.exists(params_file):
                try:
                    with open(params_file, 'r', encoding='utf-8') as f:
                        params = json.load(f)
                    results.append({
                        'name': item,
                        'path': result_path,
                        'params': params,
                        'timestamp': params.get('timestamp', 'Unknown')
                    })
                except:
                    continue
    
    return sorted(results, key=lambda x: x['name'], reverse=True)

def load_saved_result(result_path):
    """Загрузить сохраненный результат"""
    import shutil
    
    # Загрузить CSV файлы
    saved_daily = os.path.join(result_path, DAILY_CSV)
    saved_monthly = os.path.join(result_path, MONTHLY_CSV)
    saved_tiers = os.path.join(result_path, MONTHLY_TIERS_ZNX_CSV)
    
    if os.path.exists(saved_daily):
        shutil.copy2(saved_daily, DAILY_CSV)
    if os.path.exists(saved_monthly):
        shutil.copy2(saved_monthly, MONTHLY_CSV)
    if os.path.exists(saved_tiers):
        shutil.copy2(saved_tiers, MONTHLY_TIERS_ZNX_CSV)

st.set_page_config(page_title="RevShare Pool Dashboard", layout="wide")

# Sidebar for data generation
st.sidebar.title("🔧 Генерация данных")
st.sidebar.info("ℹ️ Параметры ниже используются только для генерации новых данных. Дашборд отображает реальные данные из CSV файлов.")

# Load saved results section
st.sidebar.markdown("### 📂 Загрузить сохраненный результат")
saved_results = get_saved_results()

if saved_results:
    result_names = [f"{result['name']} ({result['timestamp']})" for result in saved_results]
    selected_result = st.sidebar.selectbox(
        "🗂️ Выберите результат", 
        options=["Не выбрано"] + result_names,
        help="Выберите сохраненный результат для загрузки"
    )
    
    if selected_result != "Не выбрано":
        selected_index = result_names.index(selected_result)
        selected_result_data = saved_results[selected_index]
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("📥 Загрузить", help="Загрузить выбранный результат"):
                try:
                    load_saved_result(selected_result_data['path'])
                    load_data.clear()  # Clear cache to reload data
                    st.sidebar.success(f"✅ Результат '{selected_result_data['name']}' загружен!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"❌ Ошибка загрузки: {str(e)}")
        
        with col2:
            if st.button("🗑️ Удалить", help="Удалить выбранный результат"):
                try:
                    import shutil
                    shutil.rmtree(selected_result_data['path'])
                    st.sidebar.success(f"✅ Результат '{selected_result_data['name']}' удален!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"❌ Ошибка удаления: {str(e)}")
        
        # Show result info
        if os.path.exists(os.path.join(selected_result_data['path'], SAVED_PARAMS_FILE)):
            with open(os.path.join(selected_result_data['path'], SAVED_PARAMS_FILE), 'r', encoding='utf-8') as f:
                params = json.load(f)
            
            st.sidebar.markdown("**📋 Параметры результата:**")
            st.sidebar.markdown(f"• ZNX: {params.get('znx_amount', 'N/A'):,.0f}")
            st.sidebar.markdown(f"• Курс: ${params.get('znx_rate', 'N/A'):.8f}")
            st.sidebar.markdown(f"• Пул: ${params.get('pool_size', 'N/A'):,.2f}")
            if 'stable_znx_amount' in params and 'growth_znx_amount' in params:
                st.sidebar.markdown(f"• Stable: {params.get('stable_znx_amount', 'N/A'):,.0f} ZNX")
                st.sidebar.markdown(f"• Growth: {params.get('growth_znx_amount', 'N/A'):,.0f} ZNX")
            else:
                st.sidebar.markdown(f"• Stable: {params.get('stable_ratio', 'N/A'):.1%}")
            st.sidebar.markdown(f"• GGR: {params.get('target_ggr', 'N/A'):.1f}x")
else:
    st.sidebar.info("📭 Нет сохраненных результатов")

st.sidebar.markdown("---")
st.sidebar.markdown("### Параметры пула")

# Pool parameters (only for data generation)
znx_amount = st.sidebar.number_input("🪙 Количество собранных ZNX", min_value=1000.0, max_value=10000000.0, value=50000.0, step=1000.0, help="Количество ZNX токенов, собранных в пуле")
znx_rate = st.sidebar.number_input("💱 Курс ZNX к USD", min_value=0.00000001, max_value=100.0, value=1.0, step=0.00000001, format="%.8f", help="Курс ZNX к доллару на момент окончания сбора (до 8 знаков после запятой)")

# Calculate pool size in USD
pool_size = znx_amount * znx_rate

# Display pool size calculation
st.sidebar.markdown("---")
st.sidebar.markdown("**💰 Расчет размера пула:**")
st.sidebar.markdown(f"• {znx_amount:,.0f} ZNX × ${znx_rate:.8f} = **${pool_size:,.2f}**")
st.sidebar.markdown("---")

# Ввод абсолютных количеств токенов для каждого пула
stable_znx_amount = st.sidebar.number_input("🔵 Stable пул (ZNX)", min_value=0.0, max_value=znx_amount, value=znx_amount * 0.6, step=1000.0, help="Количество ZNX токенов в Stable пуле")
growth_znx_amount = st.sidebar.number_input("🟢 Growth пул (ZNX)", min_value=0.0, max_value=znx_amount, value=znx_amount * 0.4, step=1000.0, help="Количество ZNX токенов в Growth пуле")

# Проверка, что сумма не превышает общее количество
total_allocated = stable_znx_amount + growth_znx_amount
if total_allocated > znx_amount:
    st.sidebar.error(f"⚠️ Сумма пулов ({total_allocated:,.0f}) превышает общее количество ZNX ({znx_amount:,.0f})")
    st.sidebar.stop()

# Расчет соотношений для совместимости с существующим кодом
stable_ratio = stable_znx_amount / znx_amount if znx_amount > 0 else 0.0
growth_ratio = growth_znx_amount / znx_amount if znx_amount > 0 else 0.0

# Отображение информации о распределении
st.sidebar.markdown("**📊 Распределение токенов:**")
st.sidebar.markdown(f"• Stable: {stable_znx_amount:,.0f} ZNX ({stable_ratio:.1%})")
st.sidebar.markdown(f"• Growth: {growth_znx_amount:,.0f} ZNX ({growth_ratio:.1%})")
if total_allocated < znx_amount:
    remaining = znx_amount - total_allocated
    st.sidebar.markdown(f"• Остаток: {remaining:,.0f} ZNX ({remaining/znx_amount:.1%})")
st.sidebar.markdown("---")

# Date and target parameters
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
        seed = int(time.time() * 1000) % 1000000 + hash(str(znx_amount) + str(znx_rate) + str(stable_ratio) + str(target_ggr)) % 1000
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
            znx_price=znx_rate,
            znx_amount=znx_amount,
            znx_rate=znx_rate,
            stable_znx_amount=stable_znx_amount,
            growth_znx_amount=growth_znx_amount,
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
        
        # Add save functionality
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💾 Сохранить результат")
        save_name = st.sidebar.text_input("📝 Название результата", value=f"Результат_{datetime.now().strftime('%Y%m%d_%H%M')}", help="Введите название для сохранения результата")
        
        if st.sidebar.button("💾 Сохранить результат", help="Сохранить параметры генерации и CSV файлы"):
            if save_name.strip():
                # Prepare parameters for saving
                generation_params = {
                    'znx_amount': znx_amount,
                    'znx_rate': znx_rate,
                    'pool_size': pool_size,
                    'stable_znx_amount': stable_znx_amount,
                    'growth_znx_amount': growth_znx_amount,
                    'stable_ratio': stable_ratio,
                    'growth_ratio': growth_ratio,
                    'start_date': start_date.strftime("%Y-%m-%d"),
                    'target_ggr': target_ggr,
                    'ggr_volatility': ggr_volatility,
                    'referral_ratio': referral_ratio,
                    'upfront_bonus_stable': upfront_bonus_stable,
                    'upfront_bonus_growth': upfront_bonus_growth,
                    'ongoing_share_stable': ongoing_share_stable,
                    'ongoing_share_growth': ongoing_share_growth,
                    'cpa_min': cpa_min,
                    'cpa_max': cpa_max,
                    'effective_cpa_min': effective_cpa_min,
                    'effective_cpa_max': effective_cpa_max,
                    'seed': seed,
                    'generation_timestamp': datetime.now().isoformat()
                }
                
                try:
                    save_generation_result(generation_params, save_name.strip())
                    st.sidebar.success(f"✅ Результат '{save_name.strip()}' сохранен!")
                except Exception as e:
                    st.sidebar.error(f"❌ Ошибка сохранения: {str(e)}")
            else:
                st.sidebar.error("❌ Введите название для сохранения")
        
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

# Export functionality
st.sidebar.markdown("---")
st.sidebar.markdown("### 📤 Экспорт данных")

if st.sidebar.button("📊 Скачать CSV файлы", help="Скачать все CSV файлы в ZIP архиве"):
    import zipfile
    import io
    
    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add CSV files if they exist
        if os.path.exists(DAILY_CSV):
            zip_file.write(DAILY_CSV, DAILY_CSV)
        if os.path.exists(MONTHLY_CSV):
            zip_file.write(MONTHLY_CSV, MONTHLY_CSV)
        if os.path.exists(MONTHLY_TIERS_ZNX_CSV):
            zip_file.write(MONTHLY_TIERS_ZNX_CSV, MONTHLY_TIERS_ZNX_CSV)
    
    zip_buffer.seek(0)
    
    st.sidebar.download_button(
        label="💾 Скачать ZIP архив",
        data=zip_buffer.getvalue(),
        file_name=f"revshare_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
        mime="application/zip",
        help="Скачать все CSV файлы в ZIP архиве"
    )

# Individual file downloads
if os.path.exists(DAILY_CSV):
    with open(DAILY_CSV, 'rb') as f:
        st.sidebar.download_button(
            label="📈 Скачать Daily CSV",
            data=f.read(),
            file_name=DAILY_CSV,
            mime="text/csv"
        )

if os.path.exists(MONTHLY_CSV):
    with open(MONTHLY_CSV, 'rb') as f:
        st.sidebar.download_button(
            label="📅 Скачать Monthly CSV",
            data=f.read(),
            file_name=MONTHLY_CSV,
            mime="text/csv"
        )

if os.path.exists(MONTHLY_TIERS_ZNX_CSV):
    with open(MONTHLY_TIERS_ZNX_CSV, 'rb') as f:
        st.sidebar.download_button(
            label="🎯 Скачать Tiers CSV",
            data=f.read(),
            file_name=MONTHLY_TIERS_ZNX_CSV,
            mime="text/csv"
        )

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

# Calculate referral costs
total_referral_cost = float(monthly_df["monthly_referral_cost"].sum()) if "monthly_referral_cost" in monthly_df.columns else 0

# Calculate total payments (investments + referrals)
total_payments = total_cash_paid + total_referral_cost

# Calculate cost of capital
cost_of_capital = (total_payments / total_collected) * 100 if total_collected > 0 else 0

col_summary1, col_summary2, col_summary3, col_summary4, col_summary5 = st.columns(5)
with col_summary1:
    st.metric("💰 Собрано", f"${total_collected:,.0f}", delta="Общий размер пула")
with col_summary2:
    st.metric("💸 Cash выплаты", f"${total_cash_paid:,.0f}", delta="Только денежные выплаты")
with col_summary3:
    st.metric("🤝 Реферальные", f"${total_referral_cost:,.0f}", delta="Реферальные расходы")
with col_summary4:
    color_indicator = "🟢" if ggr_multiplier >= 3.0 else "🟡" if ggr_multiplier >= 2.5 else "🔴"
    st.metric(f"{color_indicator} GGR множитель", f"{ggr_multiplier:.2f}x", delta="Эффективность пула")
with col_summary5:
    cost_color = "🟢" if cost_of_capital <= 50 else "🟡" if cost_of_capital <= 75 else "🔴"
    st.metric(f"{cost_color} Стоимость капитала", f"{cost_of_capital:.1f}%", delta="Общие выплаты/Сбор")

# Cost of Capital breakdown
st.subheader("💹 Анализ стоимости капитала")
col_cost1, col_cost2, col_cost3 = st.columns(3)

with col_cost1:
    investment_ratio = (total_cash_paid / total_collected) * 100 if total_collected > 0 else 0
    st.metric("📊 Инвестиционные выплаты", f"{investment_ratio:.1f}%", delta=f"${total_cash_paid:,.0f}")

with col_cost2:
    referral_ratio = (total_referral_cost / total_collected) * 100 if total_collected > 0 else 0
    st.metric("🤝 Реферальные расходы", f"{referral_ratio:.1f}%", delta=f"${total_referral_cost:,.0f}")

with col_cost3:
    total_ratio = (total_payments / total_collected) * 100 if total_collected > 0 else 0
    st.metric("💰 Общая стоимость", f"{total_ratio:.1f}%", delta=f"${total_payments:,.0f}")

# Cost of capital explanation
st.info(f"""
**📈 Стоимость капитала: {cost_of_capital:.1f}%**

Это показатель того, сколько процентов от собранных средств составляют все выплаты:
- **Инвестиционные выплаты**: {investment_ratio:.1f}% (${total_cash_paid:,.0f})
- **Реферальные расходы**: {referral_ratio:.1f}% (${total_referral_cost:,.0f})
- **Общие выплаты**: {total_ratio:.1f}% (${total_payments:,.0f})

Формула: (Общие выплаты / Собранные средства) × 100%
""")

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