from revshare_pool import RevSharePoolGenerator

if __name__ == "__main__":
    gen = RevSharePoolGenerator(
        pool_size=50000,
        stable_ratio=0.6,
        growth_ratio=0.4,
        traffic_budget=50000,
        start_date="2025-11-01",
        cpa_range=(50, 60),
        target_ggr_multiplier=3.0,
        ggr_volatility=0.15,
        seed=42,
    )

    gen.calibrate_to_target_ggr(tolerance=0.1)
    daily_df = gen.generate_daily_data()
    monthly_df = gen.get_monthly_summary(daily_df)
    tier_returns = gen.calculate_tier_returns(daily_df)

    # Monthly per-ZNX payouts for 6 scenarios (2 pools x 3 tiers)
    monthly_tiers_znx = gen.get_monthly_tier_payouts_per_znx(daily_df)

    validation = gen.validate_results(daily_df)
    if not validation["passed"]:
        raise RuntimeError(f"Validation failed: {validation['errors']}")
    
    # Display warnings if any
    if validation.get("warnings"):
        print("\n⚠️ Warnings:")
        for warning in validation["warnings"]:
            print(f"  {warning}")
        print("  💡 Losses possible with low GGR. Adjust parameters to improve returns.")

    gen.export_to_csv(daily_df, monthly_df, prefix="pool1_nov2025")
    gen.export_monthly_tier_znx(monthly_tiers_znx, prefix="pool1_nov2025")

    total_ggr = float(daily_df["cumulative_ggr"].iloc[-1])
    multiplier = total_ggr / gen.pool_size

    print(f"Final GGR: ${total_ggr:,.0f}")
    print(f"Multiplier: {multiplier:,.2f}x")
    print("\nStable Pool Returns ($ per $1 invested):")
    for tier, data in tier_returns['stable'].items():
        return_pct = (data['per_dollar'] - 1) * 100
        print(f"  {tier}: {return_pct:.1f}% (${data['per_dollar']:.2f} per $1)")
    print("\nGrowth Pool Returns: 100% tokens + cash ($ per $1 invested)")
    for tier, data in tier_returns['growth'].items():
        cash_return_pct = (data['per_dollar_cash']) * 100
        print(f"  {tier}: {cash_return_pct:.1f}% cash + tokens (${data['per_dollar_cash']:.2f} per $1)")