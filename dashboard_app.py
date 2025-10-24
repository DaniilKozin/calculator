import os
import json
import shutil
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from datetime import datetime, date
import zipfile
import io

# File paths
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

def create_export_zip():
    """Create a ZIP file with all current data for export"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add CSV files if they exist
        for csv_file in [DAILY_CSV, MONTHLY_CSV, MONTHLY_TIERS_ZNX_CSV]:
            if os.path.exists(csv_file):
                zip_file.write(csv_file, csv_file)
        
        # Add parameters file if it exists in current directory
        if os.path.exists("current_params.json"):
            zip_file.write("current_params.json", "generation_params.json")
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

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

# Simplified pool parameters - only 3 fields
stable_znx_amount = st.sidebar.number_input("🔵 Токены в Stable пуле", min_value=0.0, max_value=10000000.0, value=30000.0, step=1000.0, help="Количество ZNX токенов в Stable пуле")
growth_znx_amount = st.sidebar.number_input("🟢 Токены в Growth пуле", min_value=0.0, max_value=10000000.0, value=20000.0, step=1000.0, help="Количество ZNX токенов в Growth пуле")
znx_rate = st.sidebar.number_input("💱 Курс ZNX", min_value=0.00000001, max_value=100.0, value=1.0, step=0.00000001, format="%.8f", help="Курс ZNX к доллару")

# Calculate derived values for backward compatibility
znx_amount = stable_znx_amount + growth_znx_amount
pool_size = znx_amount * znx_rate
stable_ratio = stable_znx_amount / znx_amount if znx_amount > 0 else 0.0
growth_ratio = growth_znx_amount / znx_amount if znx_amount > 0 else 0.0

# Display summary
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Итого:**")
st.sidebar.markdown(f"• Всего токенов: {znx_amount:,.0f} ZNX")
st.sidebar.markdown(f"• Размер пула: ${pool_size:,.2f}")
st.sidebar.markdown("---")

# Date and target parameters
start_date = st.sidebar.date_input("📅 Дата старта", value=date(2025, 11, 1), help="Используется только для генерации новых данных")
target_ggr = st.sidebar.slider("🎯 Целевой GGR множитель", min_value=2.0, max_value=5.0, value=3.2, step=0.1, help="Используется только для генерации новых данных")
ggr_volatility = st.sidebar.slider("📊 Волатильность GGR", min_value=0.05, max_value=0.30, value=0.15, step=0.01, help="Стандартное отклонение для ежедневных колебаний GGR. Используется только для генерации новых данных")

# Referral parameters
st.sidebar.markdown("### 🤝 Реферальная программа")
referral_ratio = st.sidebar.slider("👥 Доля реферальных денег в пуле (%)", min_value=0.0, max_value=50.0, value=15.0, step=5.0, help="Процент инвесторов, пришедших по реферальным ссылкам")

# Simplified bonus parameters
st.sidebar.markdown("#### 🎁 Бонусы")
upfront_bonus_stable = st.sidebar.slider("💰 Моментальный бонус (%)", min_value=1.0, max_value=5.0, value=3.0, step=0.5, help="Моментальный бонус от инвестиции")
ongoing_share_stable = st.sidebar.slider("📈 Постоянный бонус Stable (%)", min_value=2.0, max_value=6.0, value=4.0, step=1.0, help="Постоянный бонус от месячной прибыли Stable пула")
ongoing_share_growth = st.sidebar.select_slider("📈 Постоянный бонус Growth (%)", options=[10, 12, 15, 18, 20], value=15, help="Постоянный бонус от месячной прибыли Growth пула")

# Set growth upfront bonus same as stable for compatibility
upfront_bonus_growth = upfront_bonus_stable


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
    /* Основные стили для дашборда - компактная версия */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Улучшенные карточки метрик - компактные */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.3rem 0;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.15);
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
    
    /* Стили для метрик Streamlit - компактные */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 0.8rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
    }
    
    .stMetric:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-1px);
    }

    /* Улучшенные заголовки - компактные */
    h1, h2, h3 {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 0.5rem;
        margin-top: 0.5rem;
    }

    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }

    h2 {
        border-left: 4px solid #667eea;
        padding-left: 1rem;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }
    
    h3 {
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    /* Стили для кнопок */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Стили для разделителей - компактные */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 1rem 0;
    }

    /* Стили для таблиц - компактные */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    /* Стили для экспорта - компактные */
    .export-section {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Компактные отступы для секций */
    .stMarkdown {
        margin-bottom: 0.5rem;
    }
    
    /* Компактные отступы для колонок */
    .stColumn {
        padding: 0.2rem;
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stMetric, .metric-card {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Load data using the function defined earlier
daily_df, monthly_df, tiers_df = load_data()

if daily_df is None or monthly_df is None:
    st.warning("CSV файлы не найдены. Запустите run.py для генерации данных.")
    st.stop()

# Calculate key metrics from data (consolidated calculations)
final_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
ggr_multiplier = float(daily_df["ggr_multiplier"].iloc[-1])
real_pool_size = final_ggr / ggr_multiplier if ggr_multiplier > 0 else DEFAULT_POOL_SIZE
real_stable_ratio = stable_ratio  # Use calculated ratio from user input
real_growth_ratio = growth_ratio  # Use calculated ratio from user input

# Main Dashboard Header
st.title("🎯 RevShare Pool Dashboard")
st.markdown(f"""
<div style="text-align: center; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
     padding: 0.8rem; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid #e2e8f0;">
    <h3 style="margin: 0; color: #1f2937;">
        📊 Пул: <span style="color: #667eea;">${real_pool_size:,.0f}</span> | 
        🎯 GGR: <span style="color: #667eea;">{ggr_multiplier:.1f}x</span> | 
        🔵 Stable: <span style="color: #2196F3;">{real_stable_ratio:.0%}</span> | 
        🟢 Growth: <span style="color: #4CAF50;">{real_growth_ratio:.0%}</span>
    </h3>
</div>
""", unsafe_allow_html=True)

# Action buttons at the top
col_action1, col_action2, col_action3 = st.columns([2, 2, 1])

with col_action1:
    if st.button("📤 Экспорт данных", help="Скачать все CSV файлы в ZIP архиве", type="secondary"):
        try:
            zip_data = create_export_zip()
            st.download_button(
                label="💾 Скачать ZIP",
                data=zip_data,
                file_name=f"zenex_data_export_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                mime="application/zip",
                help="Скачать архив с CSV файлами и параметрами"
            )
        except Exception as e:
            st.error(f"❌ Ошибка экспорта: {str(e)}")

with col_action2:
    if "show_save_favorite" not in st.session_state:
        st.session_state.show_save_favorite = False
    
    if st.button("⭐ Сохранить в избранное", help="Сохранить текущую конфигурацию", type="secondary"):
        st.session_state.show_save_favorite = True
    
    if st.session_state.show_save_favorite:
        favorite_name = st.text_input("📝 Название конфигурации", 
                                     value=f"Конфигурация_{datetime.now().strftime('%Y%m%d_%H%M')}", 
                                     key="favorite_name_input")
        
        col_save1, col_save2 = st.columns(2)
        with col_save1:
            if st.button("💾 Сохранить", key="save_favorite_btn"):
                if favorite_name.strip():
                    try:
                        current_params = {
                            'znx_amount': stable_znx_amount + growth_znx_amount,
                            'znx_rate': znx_rate,
                            'pool_size': (stable_znx_amount + growth_znx_amount) * znx_rate,
                            'stable_znx_amount': stable_znx_amount,
                            'growth_znx_amount': growth_znx_amount,
                            'stable_ratio': stable_znx_amount / (stable_znx_amount + growth_znx_amount) if (stable_znx_amount + growth_znx_amount) > 0 else 0.0,
                            'growth_ratio': growth_znx_amount / (stable_znx_amount + growth_znx_amount) if (stable_znx_amount + growth_znx_amount) > 0 else 0.0,
                            'start_date': start_date.strftime("%Y-%m-%d"),
                            'target_ggr': target_ggr,
                            'ggr_volatility': ggr_volatility,
                            'referral_ratio': referral_ratio,
                            'upfront_bonus_stable': upfront_bonus_stable,
                            'upfront_bonus_growth': upfront_bonus_stable,
                            'ongoing_share_stable': ongoing_share_stable,
                            'ongoing_share_growth': ongoing_share_growth,
                            'cpa_min': cpa_min,
                            'cpa_max': cpa_max,
                            'generation_timestamp': datetime.now().isoformat(),
                            'is_favorite': True
                        }
                        
                        save_generation_result(current_params, favorite_name.strip())
                        st.success(f"⭐ Конфигурация '{favorite_name.strip()}' сохранена в избранное!")
                        st.session_state.show_save_favorite = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка сохранения: {str(e)}")
                else:
                    st.error("❌ Введите название конфигурации")
        
        with col_save2:
            if st.button("❌ Отмена", key="cancel_favorite_btn"):
                st.session_state.show_save_favorite = False
                st.rerun()

# Removed duplicate calculations and title - using consolidated values from above

def display_tier_returns(ggr_multiplier):
    """Отображение доходности по тирам"""
    st.subheader("💰 Доходность на $1 инвестиции")
    
    cols = st.columns(2)
    
    with cols[0]:
        st.markdown("**🔵 Stable Pool** (только cash)")
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
        st.markdown("**🟢 Growth Pool** (cash + 100% токенов)")
        for tier, rate in [('Basic', 0.085), ('Advanced', 0.10625), ('Premium', 0.1275)]:
            cash_per_dollar = ggr_multiplier * rate
            total_per_dollar = cash_per_dollar + 1.0
            
            st.metric(
                f"🟢 {tier} ({rate*100:.2f}%)",
                f"${total_per_dollar:.3f}",
                f"${cash_per_dollar:.3f} cash"
            )

# Дублированная секция экспорта удалена - используется объединенная версия ниже

# Consolidated metrics section
st.subheader("📊 Ключевые показатели и анализ")

# Calculate all metrics once
total_collected = real_pool_size
total_stable_payout = float(monthly_df["stable_payout"].sum())
total_growth_payout = float(monthly_df["growth_payout"].sum())
total_cash_paid = total_stable_payout + total_growth_payout
final_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
ggr_multiplier = final_ggr / total_collected if total_collected > 0 else 0
total_referral_cost = float(monthly_df["monthly_referral_cost"].sum()) if "monthly_referral_cost" in monthly_df.columns else 0
total_payments = total_cash_paid + total_referral_cost
cost_of_capital = (total_payments / total_collected) * 100 if total_collected > 0 else 0
spent = float(daily_df["cumulative_traffic"].iloc[-1])
ftds = int(daily_df["new_ftds"].sum())
avg_cpa = spent / max(1, ftds)

# Main metrics in compact layout
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("💰 Собрано", f"${total_collected:,.0f}", help="Общая сумма средств, собранных в пуле")
with col2:
    color_indicator = "🟢" if ggr_multiplier >= 3.0 else "🟡" if ggr_multiplier >= 2.5 else "🔴"
    st.metric(f"{color_indicator} GGR", f"{ggr_multiplier:.2f}x", help="Отношение валового игрового дохода к потраченным средствам")
with col3:
    st.metric("📈 Потрачено", f"${spent:,.0f}", delta=f"{(spent/real_pool_size)*100:.1f}%", help="Общие затраты на трафик")
with col4:
    st.metric("👥 FTD", f"{ftds}", delta=f"CPA: ${avg_cpa:.0f}", help="Количество первых депозитов и стоимость привлечения")
with col5:
    cost_color = "🟢" if cost_of_capital <= 50 else "🟡" if cost_of_capital <= 75 else "🔴"
    st.metric(f"{cost_color} Капитал", f"{cost_of_capital:.1f}%", help="Стоимость капитала (все выплаты/сбор)")

# Financial breakdown in second row
col6, col7, col8, col9, col10 = st.columns(5)
with col6:
    st.metric("💸 Cash выплаты", f"${total_cash_paid:,.0f}", help="Денежные выплаты инвесторам")
with col7:
    st.metric("🤝 Реферальные", f"${total_referral_cost:,.0f}", help="Расходы на реферальную программу")
with col8:
    investment_ratio = (total_cash_paid / total_collected) * 100 if total_collected > 0 else 0
    st.metric("📊 Инвест. %", f"{investment_ratio:.1f}%", help="Процент инвестиционных выплат")
with col9:
    referral_ratio = (total_referral_cost / total_collected) * 100 if total_collected > 0 else 0
    st.metric("🎁 Рефер. %", f"{referral_ratio:.1f}%", help="Процент реферальных расходов")
with col10:
    # Use the correct column name from the new referral system implementation
    if "monthly_referral_cost" in monthly_df.columns:
        referral_total = float(monthly_df["monthly_referral_cost"].sum())
    elif "referral_paid_usd" in monthly_df.columns:
        referral_total = float(monthly_df["referral_paid_usd"].sum())
    else:
        referral_total = 0.0
    st.metric("🤝 Referral", f"${referral_total:,.0f}", delta="Payouts", help="Общие выплаты по реферальной программе. Включает моментальные и постоянные бонусы рефералам")
with col6:
    # Пустая колонка для баланса
    st.write("")

# Display tier returns
display_tier_returns(ggr_multiplier)

# Combined breakeven metrics and export section
st.subheader("⚖️ Метрики безубыточности и экспорт")

# Breakeven metrics in first row
col1, col2, col3 = st.columns(3)

# Calculate GGR multiplier and breakeven metrics
min_ggr_multiplier_for_basic = 1 / 0.34  # = 2.94x for Stable Basic breakeven
is_breakeven = ggr_multiplier >= min_ggr_multiplier_for_basic

with col1:
    color = "🟢" if is_breakeven else "🔴"
    st.metric(f"{color} Min GGR for Stable Basic Breakeven", f"{min_ggr_multiplier_for_basic:.2f}x", 
              delta=f"Текущий: {ggr_multiplier:.2f}x", 
              help="Минимальный GGR множитель для безубыточности Stable Basic тира (34% ставка). При 2.94x GGR инвесторы получают 100% возврат капитала.")
with col2:
    color = "🟢" if final_ggr >= real_pool_size * 2.5 else "🔴"
    st.metric(f"{color} Total GGR", f"${final_ggr:,.0f}", 
              delta=f"{ggr_multiplier:.2f}x множитель",
              help="Общий валовой игровой доход (GGR) за весь период. Зеленый цвет означает достижение целевого уровня 2.5x от размера пула.")
with col3:
    status = "✅ Безубыточность" if is_breakeven else "❌ Убыток"
    st.metric("📊 Статус", status, delta=None,
              help="Статус безубыточности пула. Зеленый - пул прибыльный, красный - убыточный. Основан на минимальном GGR для Stable Basic.")

# Export and favorites section in second row
st.markdown("##### 📤 Экспорт и избранное")
col1, col2 = st.columns(2)

with col1:
    if st.button("📦 Скачать ZIP архив", help="Скачать все CSV файлы и параметры в ZIP архиве", use_container_width=True):
        with st.spinner("📦 Создаю ZIP архив..."):
            zip_buffer = create_export_zip()
            if zip_buffer:
                st.download_button(
                    label="⬇️ Скачать архив",
                    data=zip_buffer,
                    file_name=f"revshare_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

with col2:
    save_name = st.text_input("💾 Название конфигурации", 
                             value=f"Конфиг_{datetime.now().strftime('%Y%m%d_%H%M')}", 
                             help="Введите название для сохранения текущей конфигурации")
    
    if st.button("💾 Сохранить в избранное", help="Сохранить текущие параметры как избранную конфигурацию", use_container_width=True):
        if save_name.strip():
            with st.spinner("💾 Сохраняю конфигурацию..."):
                try:
                    # Consolidated values are used here
                    generation_params = {
                        'znx_amount': znx_amount,
                        'znx_rate': znx_rate,
                        'pool_size': pool_size,
                        'stable_znx_amount': stable_znx_amount,
                        'growth_znx_amount': growth_znx_amount,
                        'stable_ratio': stable_ratio,
                        'growth_ratio': growth_ratio,
                        'generation_timestamp': datetime.now().isoformat()
                    }
                    save_generation_result(generation_params, save_name.strip())
                    st.success(f"✅ Конфигурация '{save_name.strip()}' сохранена!")
                except Exception as e:
                    st.error(f"❌ Ошибка сохранения: {str(e)}")
        else:
            st.warning("⚠️ Введите название конфигурации")

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
# Add one month offset for payout dates (payouts happen at the end of the month, so display next month)
monthly_df_display["date"] = pd.to_datetime(monthly_df_display[["year", "month"]].assign(day=1)) + pd.DateOffset(months=1)
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
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("💰 Ежемесячные выплаты на 1 ZNX")
with col2:
    with st.expander("ℹ️ Справка"):
        st.markdown("""
        **Объяснение таблицы:**
        - **cash_usd** - денежная выплата в $ за 1 ZNX
        - **total_usd** - общая стоимость выплаты за 1 ZNX
        - **Stable пул**: только деньги (% от GGR)
        - **Growth пул**: только cash (% от GGR)
        - **Тиры**: Basic/Advanced/Premium
        - **Минимум**: 295% GGR/Spent для безубытка
        """)

if tiers_df is None:
    st.info("Запустите run.py, чтобы сгенерировать таблицу выплат по ZNX: pool1_nov2025_monthly_tiers_znx.csv")
else:
    tiers_df_display = tiers_df.copy()
    # Add one month offset for payout dates (payouts happen at the end of the month, so display next month)
    tiers_df_display["date"] = pd.to_datetime(tiers_df_display[["year", "month"]].assign(day=1)) + pd.DateOffset(months=1)
    st.dataframe(
        tiers_df_display[["date", "pool", "tier", "per_znx_cash_usd", "per_znx_total_usd"]],
        use_container_width=True,
        hide_index=True,
    )

    # Диаграмма удалена - таблицы достаточно

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
    
    # Add interactive explanation
    with st.expander("🧮 Формулы расчетов"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **💰 Stable пул:**
            - Формула: `investment × GGR × tier_rate`
            - Basic: 34% | Advanced: 38.25% | Premium: 42.5%
            - Возврат на $1: `GGR × tier_rate`
            """)
        with col2:
            st.markdown("""
            **🚀 Growth пул:**
            - Формула: `(investment × GGR × tier_rate) + investment`
            - Basic: 8.5% | Advanced: 10.625% | Premium: 12.75%
            - Возврат на $1: `(GGR × tier_rate) + 1.00`
            """)
        st.markdown("**📊 Распределение капитала:** Basic 30% | Advanced 40% | Premium 30%")
else:
    st.warning("Сгенерируйте данные для просмотра итоговой доходности")

st.caption("Built with Streamlit + Altair")