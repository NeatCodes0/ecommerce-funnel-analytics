"""
src/generate_visuals.py
Generates polished, executive-ready analytical charts and saves them to dashboards/assets/.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10

ASSETS_DIR = "dashboards/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def generate_funnel_chart():
    # 1. Macro Funnel Drop-off Chart
    stages = ['1. Product Views', '2. Add to Cart', '3. Purchases']
    counts = [1862164, 1232385, 245624]
    pcts = [100.0, 66.18, 13.19]  # Relative to initial views

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    bars = ax.barh(stages[::-1], counts[::-1], color=['#2b5c8f', '#4a90e2', '#7cb5ec'], edgecolor='black', height=0.55)

    # Add data labels
    for bar, pct in zip(bars, pcts[::-1]):
        width = bar.get_width()
        ax.text(width + 25000, bar.get_y() + bar.get_height()/2, 
                f"{width:,.0f} ({pct:.1f}%)", 
                va='center', ha='left', fontsize=9, fontweight='bold', color='#222222')

    ax.set_title("E-Commerce Macro Conversion Funnel (Oct 2019)", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Total Event Volume", fontsize=10, fontweight='bold')
    ax.set_xlim(0, 2200000)
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "funnel_waterfall.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[✓] Saved: {out_path}")

def generate_duration_chart():
    # 2. Duration Bracket vs Conversion Rate
    df = pd.read_csv("data/processed/dim_duration_loyalty.csv")
    agg_df = df.groupby("duration_bracket").agg({
        "total_sessions": "sum",
        "purchases": "sum",
        "carts": "sum",
        "abandoned_carts": "sum"
    }).reset_index()
    
    agg_df['cvr_pct'] = (agg_df['purchases'] / agg_df['total_sessions']) * 100
    agg_df['abandon_pct'] = (agg_df['abandoned_carts'] / agg_df['carts']) * 100

    order = ['< 1 min (Bounce/Skim)', '1 - 5 mins (Quick Browse)', '5 - 15 mins (Engaged)', '> 15 mins (Deep Dive)']
    agg_df['duration_bracket'] = pd.Categorical(agg_df['duration_bracket'], categories=order, ordered=True)
    agg_df = agg_df.sort_values('duration_bracket')

    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=300)
    color = '#2b5c8f'
    ax1.set_xlabel('Session Duration Bracket', fontweight='bold', fontsize=10)
    ax1.set_ylabel('Session Conversion Rate (%)', color=color, fontweight='bold', fontsize=10)
    bars = ax1.bar(agg_df['duration_bracket'], agg_df['cvr_pct'], color=color, alpha=0.85, width=0.45)
    ax1.tick_params(axis='y', labelcolor=color)

    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                 f"{height:.2f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_title("Session Engagement Duration vs. Conversion Rate", fontsize=13, fontweight='bold', pad=15)
    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "duration_conversion_curve.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[✓] Saved: {out_path}")

def generate_revenue_time_series():
    # 3. Daily Revenue vs Lost Cart Value
    df = pd.read_csv("data/processed/fact_daily_funnel.csv")
    daily = df.groupby("event_date").agg({
        "total_revenue": "sum",
        "abandoned_cart_value": "sum"
    }).reset_index()
    daily['event_date'] = pd.to_datetime(daily['event_date'])

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.plot(daily['event_date'], daily['abandoned_cart_value'], label='Abandoned Cart Value ($)', color='#d9534f', linewidth=2, linestyle='--')
    ax.plot(daily['event_date'], daily['total_revenue'], label='Realized Revenue ($)', color='#2b5c8f', linewidth=2.5)

    ax.fill_between(daily['event_date'], daily['abandoned_cart_value'], color='#d9534f', alpha=0.1)
    ax.fill_between(daily['event_date'], daily['total_revenue'], color='#2b5c8f', alpha=0.15)

    ax.set_title("October 2019: Realized Revenue vs. Abandoned Cart Value", fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel("USD ($)", fontweight='bold', fontsize=10)
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.legend(frameon=True, loc='upper left')
    plt.xticks(rotation=30)
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "daily_revenue_vs_abandoned.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[✓] Saved: {out_path}")

if __name__ == "__main__":
    generate_funnel_chart()
    generate_duration_chart()
    generate_revenue_time_series()
    print("\n[✓] All visual assets generated.")