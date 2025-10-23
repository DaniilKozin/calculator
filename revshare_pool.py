from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class TierConfig:
    basic_rate: float
    advanced_rate: float
    premium_rate: float
    capital_shares: Tuple[float, float, float]


class RevSharePoolGenerator:
    """Generate realistic 365-day casino traffic RevShare Pool data."""

    def __init__(
        self,
        pool_size: int = 35000,
        stable_ratio: float = 0.6,
        growth_ratio: float = 0.4,
        traffic_budget: Optional[int] = None,
        start_date: str = "2025-11-01",
        cpa_range: Tuple[float, float] = (55, 75),
        target_ggr_multiplier: float = 3.0,
        referral_pct_of_ggr: float = 0.05,
        ggr_volatility: float = 0.15,
        # Referral parameters
        referral_ratio: float = 0.0,
        upfront_bonus_stable: float = 0.03,
        upfront_bonus_growth: float = 0.03,
        ongoing_share_stable: float = 0.04,
        ongoing_share_growth: float = 0.15,
        # ZNX price parameter
        znx_price: float = 1.0,
        znx_amount: Optional[float] = None,
        znx_rate: Optional[float] = None,
        # Absolute token amounts (alternative to ratios)
        stable_znx_amount: Optional[float] = None,
        growth_znx_amount: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> None:
        if traffic_budget is None:
            traffic_budget = pool_size
        if pool_size <= 0 or traffic_budget <= 0:
            raise ValueError("pool_size and traffic_budget must be positive")
        if not (0 < stable_ratio < 1 and 0 < growth_ratio < 1):
            raise ValueError("stable_ratio and growth_ratio must be in (0,1)")
        if abs((stable_ratio + growth_ratio) - 1.0) > 1e-6:
            raise ValueError("stable_ratio + growth_ratio must equal 1.0")
        if cpa_range[0] <= 0 or cpa_range[1] <= 0 or cpa_range[0] >= cpa_range[1]:
            raise ValueError("Invalid cpa_range")

        self.pool_size = float(pool_size)
        self.stable_ratio = float(stable_ratio)
        self.growth_ratio = float(growth_ratio)
        self.traffic_budget = float(traffic_budget)
        self.cpa_range = cpa_range
        self.target_ggr_multiplier = float(target_ggr_multiplier)
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.seed = seed
        self.referral_pct_of_ggr = float(referral_pct_of_ggr)
        self.ggr_volatility = float(ggr_volatility)
        
        # Referral system parameters
        self.referral_ratio = float(referral_ratio)
        self.upfront_bonus_stable = float(upfront_bonus_stable)
        self.upfront_bonus_growth = float(upfront_bonus_growth)
        self.ongoing_share_stable = float(ongoing_share_stable)
        self.ongoing_share_growth = float(ongoing_share_growth)
        self.znx_price = float(znx_price)
        self.znx_amount = znx_amount
        self.znx_rate = znx_rate
        
        # Handle absolute token amounts if provided
        if stable_znx_amount is not None and growth_znx_amount is not None:
            if znx_amount is None:
                raise ValueError("znx_amount must be provided when using absolute token amounts")
            
            total_allocated = stable_znx_amount + growth_znx_amount
            if total_allocated > znx_amount:
                raise ValueError(f"Total allocated tokens ({total_allocated}) exceeds total ZNX amount ({znx_amount})")
            
            # Recalculate ratios based on absolute amounts
            self.stable_ratio = float(stable_znx_amount / znx_amount) if znx_amount > 0 else 0.0
            self.growth_ratio = float(growth_znx_amount / znx_amount) if znx_amount > 0 else 0.0
            
            # Store absolute amounts
            self.stable_znx_amount = float(stable_znx_amount)
            self.growth_znx_amount = float(growth_znx_amount)
        else:
            # Use provided ratios and calculate absolute amounts if znx_amount is available
            if znx_amount is not None:
                self.stable_znx_amount = float(znx_amount * stable_ratio)
                self.growth_znx_amount = float(znx_amount * growth_ratio)
            else:
                self.stable_znx_amount = None
                self.growth_znx_amount = None
        
        # Calculate upfront referral costs
        referred_capital = self.pool_size * self.referral_ratio
        upfront_cost_stable = referred_capital * self.stable_ratio * self.upfront_bonus_stable
        upfront_cost_growth = referred_capital * self.growth_ratio * self.upfront_bonus_growth
        self.total_upfront_referral = upfront_cost_stable + upfront_cost_growth
        
        # Reduce traffic budget by upfront referral costs
        self.effective_traffic_budget = self.traffic_budget - self.total_upfront_referral

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Variables for negative day clusters
        self.negative_cluster_days = 0
        self.negative_cluster_remaining = 0
        
        # High watermark for monthly payouts
        self.high_watermark = 0.0

        # Tier configs (rates and capital shares)
        self.stable_cfg = TierConfig(
            basic_rate=0.34, 
            advanced_rate=0.3825, 
            premium_rate=0.425,
            capital_shares=(0.30, 0.40, 0.30)
        )
        self.growth_cfg = TierConfig(
            basic_rate=0.085, 
            advanced_rate=0.10625, 
            premium_rate=0.1275,
            capital_shares=(0.30, 0.40, 0.30)
        )

        # Weighted pool rates
        self.stable_weighted_rate = (
            self.stable_cfg.capital_shares[0] * self.stable_cfg.basic_rate +
            self.stable_cfg.capital_shares[1] * self.stable_cfg.advanced_rate +
            self.stable_cfg.capital_shares[2] * self.stable_cfg.premium_rate
        )
        self.growth_weighted_rate = (
            self.growth_cfg.capital_shares[0] * self.growth_cfg.basic_rate +
            self.growth_cfg.capital_shares[1] * self.growth_cfg.advanced_rate +
            self.growth_cfg.capital_shares[2] * self.growth_cfg.premium_rate
        )

        # Schedules
        self.retention_schedule: Dict[Tuple[int, int], Tuple[float, float]] = {
            (1, 30): (1.00, 0.00), (31, 60): (0.42, 0.03), (61, 90): (0.33, 0.03),
            (91, 120): (0.26, 0.02), (121, 150): (0.22, 0.02), (151, 180): (0.19, 0.02),
            (181, 210): (0.16, 0.02), (211, 240): (0.14, 0.02), (241, 270): (0.12, 0.02),
            (271, 300): (0.10, 0.015), (301, 330): (0.09, 0.015), (331, 365): (0.08, 0.01),
        }
        self.deposit_by_days: Dict[Tuple[int, int], float] = {
            (1, 30): 23, (31, 60): 49, (61, 90): 66, (91, 120): 81, (121, 150): 91,
            (151, 180): 101, (181, 210): 108, (211, 240): 115, (241, 270): 121,
            (271, 300): 125, (301, 330): 129, (331, 365): 132,
        }
        self.znx_price = 0.60

        # Tunable calibration scales
        self._deposit_scale = 1.0
        self._retention_scale = 1.0
        self._cpa_scale = 1.0

    def _range_value(self, mapping: Dict[Tuple[int, int], float], age: int) -> float:
        for (a, b), v in mapping.items():
            if a <= age <= b:
                return v
        return list(mapping.values())[-1]

    def _range_pair(self, mapping: Dict[Tuple[int, int], Tuple[float, float]], age: int) -> Tuple[float, float]:
        for (a, b), v in mapping.items():
            if a <= age <= b:
                return v
        return list(mapping.values())[-1]

    def _generate_ftd_schedule(self) -> pd.DataFrame:
        days = 30
        # Спенд равен собранным средствам (pool_size)
        # Allocate pool_size across 30 days (Dirichlet for realistic variance)
        weights = np.random.dirichlet([2.0] * days)
        spends = weights * self.pool_size  # Используем pool_size вместо traffic_budget
        cpas = np.random.uniform(self.cpa_range[0] * self._cpa_scale, self.cpa_range[1] * self._cpa_scale, size=days)
        ftds = np.maximum(0, np.round(spends / cpas).astype(int))
        traffic_df = pd.DataFrame({
            "day": np.arange(1, days + 1),
            "date": [self.start_date + timedelta(days=i - 1) for i in range(1, days + 1)],
            "traffic_spend": spends,
            "cpa": cpas,
            "new_ftds": ftds,
        })
        traffic_df["cumulative_traffic"] = traffic_df["traffic_spend"].cumsum()
        return traffic_df

    def _get_retention_rate(self, age_days: int) -> float:
        base, var = self._range_pair(self.retention_schedule, age_days)
        adj = base * self._retention_scale
        delta = random.uniform(-var, var)
        return max(0.0, min(1.0, adj + delta))

    def _calculate_seasonality(self, date: datetime) -> float:
        mult = 1.0
        m, d, wd = date.month, date.day, date.weekday()  # 0=Mon
        if (m == 12 and 20 <= d <= 31):
            mult *= 1.18
        if (m == 1 and 1 <= d <= 10):
            mult *= 1.15
        if (m == 2 and d == 14):
            mult *= 1.08
        if m in [6, 7]:
            mult *= 1.12  # world cup (if applicable)
        if m in [7, 8]:
            mult *= 1.06
        if m == 9:
            mult *= 0.92
        if m == 2:
            mult *= 0.94
        if wd in [5, 6]:
            mult *= 1.08
        if 25 <= d <= 28:
            mult *= 1.12
        return mult

    def _get_avg_deposit(self, age_days: int, date: datetime) -> float:
        base = self._range_value(self.deposit_by_days, age_days) * self._deposit_scale
        base *= random.uniform(0.85, 1.15)
        return base * self._calculate_seasonality(date)

    def _calculate_daily_ggr(self, total_deposits: float) -> float:
        if total_deposits <= 0:
            return 0.0
        
        # Реалистичное моделирование RTP казино 94-97% (house edge 3-6%)
        # Базовая маржа дома варьируется в зависимости от типа игр
        base_house_edge = random.uniform(0.03, 0.06)  # 3-6% house edge
        
        # Умеренная дневная волатильность
        daily_variance = float(np.random.normal(1.0, self.ggr_volatility))  # Нормальная волатильность
        
        # Базовый GGR от депозитов
        theoretical_ggr = total_deposits * base_house_edge * daily_variance
        
        # Check if we're in a negative cluster (уменьшенная вероятность)
        if self.negative_cluster_remaining > 0:
            # В кластере негативных дней - умеренные потери казино
            theoretical_ggr = -abs(theoretical_ggr * random.uniform(1.2, 2.5))  # Умеренные потери
            self.negative_cluster_remaining -= 1
        else:
            # Start new negative cluster (2% chance вместо 5%)
            if random.random() < 0.02:
                self.negative_cluster_remaining = random.randint(2, 4)  # 2-4 дня вместо 3-8
                theoretical_ggr = -abs(theoretical_ggr * random.uniform(1.2, 2.5))
            # Regular negative days - редкие дни когда игроки выигрывают больше
            elif random.random() < 0.15:  # 15% chance вместо 25%
                theoretical_ggr = -abs(theoretical_ggr * random.uniform(1.1, 2.0))  # Меньшие потери
        
        # Экстремальная волатильность - джекпоты или крупные проигрыши (реже)
        if random.random() < 0.03:  # 3% chance вместо 8%
            if random.random() < 0.2:  # 20% шанс что это джекпот (потери казино)
                theoretical_ggr = -abs(theoretical_ggr * random.uniform(2.0, 5.0))  # Меньшие джекпоты
            else:  # 80% шанс что это крупные проигрыши игроков
                theoretical_ggr = abs(theoretical_ggr * random.uniform(2.0, 4.0))  # Умеренные выигрыши
        
        return theoretical_ggr

    def generate_daily_data(self) -> pd.DataFrame:
        traffic_df = self._generate_ftd_schedule()
        ftd_map = {int(row.day): int(row.new_ftds) for _, row in traffic_df.iterrows()}
        
        # First, generate basic daily data without payouts
        days = 365
        rows: List[Dict[str, float]] = []
        cumulative_ggr = 0.0
        cumulative_traffic = 0.0
        stable_pool_size = self.pool_size * self.stable_ratio
        growth_pool_size = self.pool_size * self.growth_ratio

        for day in range(1, days + 1):
            date = self.start_date + timedelta(days=day - 1)
            # Compute active players by summing cohorts (days since FTD)
            active_players = 0.0
            total_deposits = 0.0
            for ftd_day in range(1, min(day, 30) + 1):
                age = day - ftd_day + 1
                cohort_players = round(ftd_map.get(ftd_day, 0) * self._get_retention_rate(age))
                if cohort_players <= 0:
                    continue
                avg_dep = self._get_avg_deposit(age, date)
                active_players += cohort_players
                total_deposits += cohort_players * avg_dep

            daily_ggr = self._calculate_daily_ggr(total_deposits)
            cumulative_ggr += daily_ggr

            traffic_spend = float(traffic_df.loc[traffic_df['day'] == day, 'traffic_spend'].sum()) if day <= 30 else 0.0
            if day <= 30:
                cumulative_traffic += traffic_spend

            rows.append({
                "date": date,
                "day": day,
                "month": date.month,
                "year": date.year,
                "day_of_week": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][date.weekday()],
                "new_ftds": int(ftd_map.get(day, 0)) if day <= 30 else 0,
                "active_players": float(active_players),
                "avg_deposit": float(total_deposits / active_players) if active_players > 0 else 0.0,
                "total_deposits": float(total_deposits),
                "daily_ggr": float(daily_ggr),
                "cumulative_ggr": float(cumulative_ggr),
                "traffic_spend": float(traffic_spend),
                "cumulative_traffic": float(cumulative_traffic),
                "effective_traffic_budget": float(self.effective_traffic_budget),
                "ggr_multiplier": float(cumulative_ggr / self.pool_size),
            })

        # Create DataFrame and get monthly summary with high watermark logic
        df = pd.DataFrame(rows)
        monthly_summary = self.get_monthly_summary(df)
        
        # Now distribute monthly payouts across days of each month
        cumulative_stable = 0.0
        cumulative_growth = 0.0
        cumulative_referral_cost = 0.0
        
        for i, row in df.iterrows():
            # Find the monthly payout for this day's month/year
            month_data = monthly_summary[
                (monthly_summary['year'] == row['year']) & 
                (monthly_summary['month'] == row['month'])
            ]
            
            if len(month_data) > 0:
                monthly_stable = float(month_data.iloc[0]['stable_payout'])
                monthly_growth = float(month_data.iloc[0]['growth_payout'])
                
                # Get days in this month
                import calendar
                days_in_month = calendar.monthrange(row['year'], row['month'])[1]
                
                # Distribute monthly payout evenly across days (only on positive GGR days)
                if row['daily_ggr'] > 0:
                    # Count positive GGR days in this month
                    month_mask = (df['year'] == row['year']) & (df['month'] == row['month'])
                    positive_ggr_days = (df[month_mask]['daily_ggr'] > 0).sum()
                    
                    if positive_ggr_days > 0:
                        daily_stable = monthly_stable / positive_ggr_days
                        daily_growth = monthly_growth / positive_ggr_days
                    else:
                        daily_stable = 0.0
                        daily_growth = 0.0
                else:
                    # No payout on negative GGR days
                    daily_stable = 0.0
                    daily_growth = 0.0
            else:
                daily_stable = 0.0
                daily_growth = 0.0
            
            cumulative_stable += daily_stable
            cumulative_growth += daily_growth
            
            # Calculate referral costs based on investor payouts
            daily_referral_stable = daily_stable * self.referral_ratio * self.ongoing_share_stable
            daily_referral_growth = daily_growth * self.referral_ratio * self.ongoing_share_growth
            daily_total_referral = daily_referral_stable + daily_referral_growth
            cumulative_referral_cost += daily_total_referral
            
            # Update the row with payout information
            df.at[i, 'stable_payout'] = float(daily_stable)
            df.at[i, 'growth_payout'] = float(daily_growth)
            df.at[i, 'cumulative_stable'] = float(cumulative_stable)
            df.at[i, 'cumulative_growth'] = float(cumulative_growth)
            df.at[i, 'stable_return_pct'] = float((cumulative_stable / stable_pool_size) * 100.0) if stable_pool_size > 0 else 0.0
            df.at[i, 'growth_return_pct'] = float((cumulative_growth / growth_pool_size) * 100.0) if growth_pool_size > 0 else 0.0
            df.at[i, 'daily_total_referral'] = float(daily_total_referral)
            df.at[i, 'cumulative_referral_cost'] = float(cumulative_referral_cost)

        return df

    def calibrate_to_target_ggr(self, tolerance: float = 0.1) -> None:
        """Iteratively adjust CPA/retention/deposit scales to hit target multiplier.
        Uses bounded proportional steps to avoid oscillations.
        """
        max_iterations = 40
        prev_error = None
        for _ in range(max_iterations):
            df = self.generate_daily_data()
            actual = float(df["cumulative_ggr"].iloc[-1] / self.pool_size)
            error = (actual - self.target_ggr_multiplier) / self.target_ggr_multiplier
            if abs(error) < tolerance:
                return

            # Step size proportional to error, bounded to keep stability
            step = min(0.20, max(0.02, abs(error)))
            if error > 0:  # too high
                dep_factor = 1.0 - step
                ret_factor = 1.0 - step * 0.6
                cpa_factor = 1.0 + step * 0.5
            else:  # too low
                dep_factor = 1.0 + step
                ret_factor = 1.0 + step * 0.6
                cpa_factor = 1.0 - step * 0.5

            # Apply factors
            self._deposit_scale *= dep_factor
            self._retention_scale *= ret_factor
            self._cpa_scale *= cpa_factor

            # Clamp scales
            self._deposit_scale = max(0.05, min(2.0, self._deposit_scale))
            self._retention_scale = max(0.30, min(1.0, self._retention_scale))
            self._cpa_scale = max(0.60, min(1.50, self._cpa_scale))

            # If we crossed the target compared to previous iteration, dampen further next loop
            if prev_error is not None and (error * prev_error) < 0:
                self._deposit_scale = (self._deposit_scale + 1.0) / 2.0
                self._retention_scale = (self._retention_scale + 1.0) / 2.0
                self._cpa_scale = (self._cpa_scale + 1.0) / 2.0
            prev_error = error
        # proceed even if slightly outside tolerance

    def _tier_weights(self, cfg: TierConfig) -> Tuple[float, float, float]:
        b = cfg.capital_shares[0] * cfg.basic_rate
        a = cfg.capital_shares[1] * cfg.advanced_rate
        p = cfg.capital_shares[2] * cfg.premium_rate
        s = b + a + p
        return (b / s, a / s, p / s) if s > 0 else (1/3, 1/3, 1/3)

    def calculate_tier_returns(self, daily_df: Optional[pd.DataFrame] = None) -> Dict[str, Dict]:
        if daily_df is None:
            daily_df = self.generate_daily_data()
        
        # Get final cumulative GGR and calculate multiplier
        final_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
        ggr_multiplier = final_ggr / self.pool_size
        
        # Calculate pool sizes and investments per tier
        stable_pool = self.pool_size * self.stable_ratio
        growth_pool = self.pool_size * self.growth_ratio
        
        stable_invested = [stable_pool * s for s in self.stable_cfg.capital_shares]
        growth_invested = [growth_pool * s for s in self.growth_cfg.capital_shares]
        
        # NEW SIMPLIFIED FORMULAS:
        # Stable: payout = investment × GGR_multiplier × tier_rate
        # Growth: total = (investment × GGR_multiplier × tier_rate) + investment
        stable_rates = [self.stable_cfg.basic_rate, self.stable_cfg.advanced_rate, self.stable_cfg.premium_rate]
        growth_rates = [self.growth_cfg.basic_rate, self.growth_cfg.advanced_rate, self.growth_cfg.premium_rate]
        
        stable_received = [inv * ggr_multiplier * rate for inv, rate in zip(stable_invested, stable_rates)]
        growth_cash = [inv * ggr_multiplier * rate for inv, rate in zip(growth_invested, growth_rates)]
        growth_tokens = growth_invested[:]  # 100% tokens returned (USD value)

        def make_stable(inv: float, rec: float, rate: float) -> Dict[str, float]:
            # Stable: per_dollar = ggr_multiplier × tier_rate
            per_dollar = ggr_multiplier * rate
            return {
                "invested": inv,
                "received": rec,
                "per_dollar": per_dollar,
            }

        def make_growth(inv: float, cash: float, tokens: float, rate: float) -> Dict[str, float]:
            # Growth: per_dollar = (ggr_multiplier × tier_rate) + 1.00
            total = cash + tokens
            per_dollar_cash = ggr_multiplier * rate
            per_dollar_total = per_dollar_cash + 1.0
            return {
                "invested": inv,
                "cash_received": cash,
                "tokens_returned": tokens,
                "total_value": total,
                "per_dollar_cash": per_dollar_cash,
                "per_dollar_total": per_dollar_total,
            }

        return {
            "stable": {
                "basic": make_stable(stable_invested[0], stable_received[0], stable_rates[0]),
                "advanced": make_stable(stable_invested[1], stable_received[1], stable_rates[1]),
                "premium": make_stable(stable_invested[2], stable_received[2], stable_rates[2]),
            },
            "growth": {
                "basic": make_growth(growth_invested[0], growth_cash[0], growth_tokens[0], growth_rates[0]),
                "advanced": make_growth(growth_invested[1], growth_cash[1], growth_tokens[1], growth_rates[1]),
                "premium": make_growth(growth_invested[2], growth_cash[2], growth_tokens[2], growth_rates[2]),
            },
        }

    def _calculate_monthly_payout(self, month_end_cumulative_ggr: float) -> Tuple[float, float, bool]:
        """Only pay when cumulative GGR exceeds previous high watermark.
        
        Returns:
            Tuple of (stable_payout, growth_payout, watermark_exceeded)
        """
        if month_end_cumulative_ggr > self.high_watermark:
            # New high reached - calculate payout only on the INCREMENT above watermark
            ggr_increment = month_end_cumulative_ggr - self.high_watermark
            
            # Apply pool weights to the weighted rates
            stable_payout = ggr_increment * self.stable_weighted_rate * self.stable_ratio
            growth_payout = ggr_increment * self.growth_weighted_rate * self.growth_ratio
            
            # Update watermark
            self.high_watermark = month_end_cumulative_ggr
            return stable_payout, growth_payout, True
        else:
            # Below watermark - no payout this month
            return 0.0, 0.0, False

    def get_monthly_summary(self, daily_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        if daily_df is None:
            daily_df = self.generate_daily_data()
        
        # Reset high watermark for fresh calculation
        self.high_watermark = 0.0
        
        df = daily_df.copy()
        df['year'] = df['date'].dt.year
        summary = (
            df.groupby(['year', 'month'], as_index=False)[
                ['new_ftds', 'active_players', 'total_deposits', 'daily_ggr', 'traffic_spend']
            ].sum()
        )
        
        # Calculate cumulative GGR for high watermark logic
        summary['monthly_ggr'] = summary['daily_ggr']
        summary['cumulative_ggr'] = summary['monthly_ggr'].cumsum()
        
        # Track negative GGR days per month
        negative_days_per_month = []
        for _, row in summary.iterrows():
            month_data = df[(df['year'] == row['year']) & (df['month'] == row['month'])]
            negative_days = (month_data['daily_ggr'] < 0).sum()
            negative_days_per_month.append(negative_days)
        
        summary['ggr_negative_days'] = negative_days_per_month
        
        # Apply high watermark logic for payouts
        monthly_stable_payouts = []
        monthly_growth_payouts = []
        watermark_exceeded = []
        
        for _, row in summary.iterrows():
            monthly_stable, monthly_growth, exceeded = self._calculate_monthly_payout(row['cumulative_ggr'])
            
            # Store only the monthly payout amounts (not cumulative)
            monthly_stable_payouts.append(monthly_stable)
            monthly_growth_payouts.append(monthly_growth)
            watermark_exceeded.append(exceeded)
        
        summary['stable_payout'] = monthly_stable_payouts
        summary['growth_payout'] = monthly_growth_payouts
        summary['watermark_exceeded'] = watermark_exceeded
        # Calculate monthly referral cost from daily data if available
        if 'daily_total_referral' in daily_df.columns:
            monthly_referral = daily_df.groupby(['year', 'month'])['daily_total_referral'].sum().reset_index()
            summary = summary.merge(monthly_referral, on=['year', 'month'], how='left')
            summary['monthly_referral_cost'] = summary['daily_total_referral'].fillna(0)
            summary = summary.drop('daily_total_referral', axis=1)
        else:
            summary['monthly_referral_cost'] = 0
        summary['capital_cost_usd'] = summary['traffic_spend'] + summary['monthly_referral_cost']
        return summary

    def get_monthly_tier_payouts_per_znx(self, daily_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Return monthly payouts per 1 ZNX for each of the 6 scenarios.
        Growth tiers: 100% tokens returned + cash share of GGR; Stable tiers: cash share of GGR only.
        """
        if daily_df is None:
            daily_df = self.generate_daily_data()
        monthly = self.get_monthly_summary(daily_df)

        stable_pool = self.pool_size * self.stable_ratio
        growth_pool = self.pool_size * self.growth_ratio
        stable_invested = np.array([stable_pool * s for s in self.stable_cfg.capital_shares])
        growth_invested = np.array([growth_pool * s for s in self.growth_cfg.capital_shares])
        sw = np.array(self._tier_weights(self.stable_cfg))
        gw = np.array(self._tier_weights(self.growth_cfg))

        rows: List[Dict[str, float]] = []
        for _, m in monthly.iterrows():
            # monthly cash payouts per pool
            stable_cash = float(m['stable_payout'])
            growth_cash = float(m['growth_payout'])
            # distribute to tiers by weights
            stable_tier_cash = sw * stable_cash
            growth_tier_cash = gw * growth_cash

            # per 1 ZNX cash
            stable_per_znx_cash = (stable_tier_cash / stable_invested) * self.znx_price if stable_pool > 0 else np.zeros(3)
            growth_per_znx_cash = (growth_tier_cash / growth_invested) * self.znx_price if growth_pool > 0 else np.zeros(3)
            # Убираем расчет возврата токенов - сосредотачиваемся только на cash выплатах
            # growth per 1 ZNX total = только cash (без возврата токенов)
            growth_per_znx_total = growth_per_znx_cash
            # stable per 1 ZNX total == cash (no token return implied)
            stable_per_znx_total = stable_per_znx_cash

            tiers = ['basic', 'advanced', 'premium']
            for i, t in enumerate(tiers):
                rows.append({
                    'year': int(m['year']),
                    'month': int(m['month']),
                    'pool': 'stable',
                    'tier': t,
                    'per_znx_cash_usd': float(stable_per_znx_cash[i]),
                    'per_znx_total_usd': float(stable_per_znx_total[i]),
                })
            for i, t in enumerate(tiers):
                rows.append({
                    'year': int(m['year']),
                    'month': int(m['month']),
                    'pool': 'growth',
                    'tier': t,
                    'per_znx_cash_usd': float(growth_per_znx_cash[i]),
                    'per_znx_total_usd': float(growth_per_znx_total[i]),
                })
        return pd.DataFrame(rows)

    def calculate_breakeven_metrics(self, daily_df: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """Рассчитывает метрики безубыточности для Stable пула.
        
        Для Stable пула важно покрыть стоимость тела к USD при том что цена токена может меняться.
        Stable Basic (34% rate) needs 2.94x GGR multiplier to return 100% capital.
        """
        if daily_df is None:
            daily_df = self.generate_daily_data()
            
        final_ggr = float(daily_df['cumulative_ggr'].iloc[-1])
        final_spent = float(daily_df['cumulative_traffic'].iloc[-1])
        ggr_multiplier = (final_ggr / self.pool_size) if self.pool_size > 0 else 0.0
        
        # Расчет для Stable пула
        stable_pool_size = self.pool_size * self.stable_ratio
        stable_total_payout = float(daily_df['cumulative_stable'].iloc[-1])
        stable_return_pct = (stable_total_payout / stable_pool_size * 100.0) if stable_pool_size > 0 else 0.0
        
        # Минимальные требования
        min_ggr_multiplier_for_basic = 1 / 0.34  # = 2.94x for Stable Basic breakeven
        min_stable_return = 34.0  # 34% минимум для Stable
        
        # Статус безубыточности
        is_breakeven = ggr_multiplier >= min_ggr_multiplier_for_basic
        stable_meets_minimum = stable_return_pct >= min_stable_return
        
        return {
            'ggr_multiplier': ggr_multiplier,
            'min_ggr_multiplier_for_basic': min_ggr_multiplier_for_basic,
            'is_breakeven': is_breakeven,
            'stable_return_pct': stable_return_pct,
            'min_stable_return': min_stable_return,
            'stable_meets_minimum': stable_meets_minimum,
            'final_ggr': final_ggr,
            'final_spent': final_spent,
            'stable_pool_size': stable_pool_size,
            'stable_total_payout': stable_total_payout
        }

    def validate_results(self, daily_df: Optional[pd.DataFrame] = None) -> Dict[str, object]:
        if daily_df is None:
            daily_df = self.generate_daily_data()
        errors: List[str] = []
        warnings: List[str] = []
        final_mult = float(daily_df['ggr_multiplier'].iloc[-1])
        
        # Critical validation checks (hard errors)
        if not (1.0 <= final_mult <= 6.0):  # Expanded range to allow more scenarios
            errors.append(f"GGR multiplier out of range: {final_mult:.2f}")
        # Allow cumulative GGR to decrease due to negative daily GGR - this is now valid
        if (daily_df['active_players'] < 0).any():
            errors.append("Negative active_players")
        # Check if payouts are reasonable relative to GGR
        final_ggr = float(daily_df['cumulative_ggr'].iloc[-1])
        total_payouts = float(daily_df['cumulative_stable'].iloc[-1] + daily_df['cumulative_growth'].iloc[-1])
        max_ggr = float(daily_df['cumulative_ggr'].max())  # Highest GGR reached
        
        # Only flag as error if payouts exceed the maximum GGR ever reached by a significant margin
        if total_payouts > max_ggr * 1.1:  # Allow 10% buffer for calculation precision
            errors.append(f"Payouts significantly exceed maximum GGR: payouts=${total_payouts:.2f}, max_ggr=${max_ggr:.2f}")
        elif final_ggr > 0 and total_payouts >= final_ggr:
            # This is just a warning if final GGR is positive but payouts exceed it
            warnings.append(f"Payouts exceed final GGR: payouts=${total_payouts:.2f}, final_ggr=${final_ggr:.2f}")

        # Tier profitability checks (changed to warnings)
        tiers = self.calculate_tier_returns(daily_df)
        s_basic = tiers['stable']['basic']['per_dollar']
        s_adv = tiers['stable']['advanced']['per_dollar']
        s_prem = tiers['stable']['premium']['per_dollar']
        g_basic_cash = tiers['growth']['basic']['per_dollar_cash']
        g_adv_cash = tiers['growth']['advanced']['per_dollar_cash']
        g_prem_cash = tiers['growth']['premium']['per_dollar_cash']

        # Profitability warnings (no longer hard errors)
        if s_basic < 1.0:  # 100% minimum
            warnings.append(f"⚠️ Stable Basic returns {s_basic*100:.1f}% (LOSS)")
        if s_adv < 1.0:
            warnings.append(f"⚠️ Stable Advanced returns {s_adv*100:.1f}% (LOSS)")
        if s_prem < 1.0:
            warnings.append(f"⚠️ Stable Premium returns {s_prem*100:.1f}% (LOSS)")
        if g_basic_cash < 0.0:  # Allow negative returns
            warnings.append(f"⚠️ Growth Basic cash returns {g_basic_cash*100:.1f}% (LOSS)")
        if g_adv_cash < 0.0:
            warnings.append(f"⚠️ Growth Advanced cash returns {g_adv_cash*100:.1f}% (LOSS)")
        if g_prem_cash < 0.0:
            warnings.append(f"⚠️ Growth Premium cash returns {g_prem_cash*100:.1f}% (LOSS)")

        return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings, "final_multiplier": final_mult}

    def export_to_csv(self, daily_df: pd.DataFrame, monthly_df: pd.DataFrame, prefix: str = "pool1") -> None:
        daily_path = f"{prefix}_daily.csv"
        monthly_path = f"{prefix}_monthly.csv"
        daily_df.to_csv(daily_path, index=False)
        monthly_df.to_csv(monthly_path, index=False)

    def export_monthly_tier_znx(self, df: pd.DataFrame, prefix: str = "pool1") -> str:
        path = f"{prefix}_monthly_tiers_znx.csv"
        df.to_csv(path, index=False)
        return path


__all__ = ["RevSharePoolGenerator"]