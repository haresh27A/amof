"""
Publication Figure Generator for AMORA Research Paper
Component Tag: [A. Evaluation Framework - Figure Generator]

Generates 3 publication-grade vector graphics (PDF & 300 DPI PNG):
  - Figure 1: Scalability & Pre-filtering Efficiency (Routing Latency vs Catalog Size N)
  - Figure 2: Gating Efficiency & Prompt Token Compaction across Baselines
  - Figure 3: Functional Ablation & Retrieval Trade-off Frontier
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set publication styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_figure1_scalability():
    """Figure 1: Scalability Analysis - Constant Sub-5ms Routing Latency."""
    catalog_sizes = [100, 500, 1000, 5000, 10000]
    routing_latency = [4.14, 3.88, 3.29, 3.27, 3.26]  # Exact measured ms
    naive_scan_proj = [4.14, 18.5, 36.2, 178.0, 355.0] # O(N*D) unindexed baseline

    fig, ax1 = plt.subplots(figsize=(6.5, 4.0), dpi=300)

    ax1.plot(catalog_sizes, routing_latency, marker='o', color='#1f77b4', lw=2.2, label='AMORA (2-Stage Pre-filter)')
    ax1.plot(catalog_sizes, naive_scan_proj, marker='s', color='#d62728', lw=1.8, ls='--', label='Naive Full Scan (Projected $O(N \cdot D)$)')

    ax1.set_xscale('log')
    ax1.set_xlabel('Catalog Size ($N$ Endpoints)', fontweight='bold')
    ax1.set_ylabel('Routing Latency (ms)', fontweight='bold', color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.set_ylim(0, 30)

    # Highlight AMORA constant zone
    ax1.axhspan(3.0, 4.5, color='#1f77b4', alpha=0.12, label='AMORA Sub-5ms Bound')

    ax1.set_title('Figure 1: Catalog Scalability & Routing Latency', fontweight='bold', pad=12)
    ax1.grid(True)
    ax1.legend(loc='upper left', framealpha=0.9)

    fig.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig1_scalability.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig1_scalability.png")
    fig.savefig(pdf_path)
    fig.savefig(png_path)
    plt.close(fig)
    print(f"Generated Figure 1: {png_path}")

def generate_figure2_efficiency_tradeoffs():
    """Figure 2: Dual panel showing Gating Bypass Rate and Context Token Compaction."""
    baselines = ['Std RAG', 'INKER', 'Sim-Only', 'Fixed-Wt', 'AMORA']
    retr_rates = [100.0, 65.0, 100.0, 100.0, 65.0]      # Retrieval %
    tokens = [509, 806, 1073, 1043, 786]                 # Prompt tokens

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.0), dpi=300)

    # Panel A: Retrieval Gating Trigger Rate
    colors_retr = ['#7f7f7f', '#2ca02c', '#7f7f7f', '#7f7f7f', '#2ca02c']
    bars1 = ax1.bar(baselines, retr_rates, color=colors_retr, width=0.55, edgecolor='black', lw=0.8)
    ax1.set_ylabel('Retrieval Trigger Rate (%)', fontweight='bold')
    ax1.set_ylim(0, 120)
    ax1.axhline(65.0, color='#2ca02c', ls=':', lw=1.5)
    ax1.set_title('(a) Gating Bypass Efficiency\n(35% Skipped via IE-KRT)', fontweight='bold')
    ax1.grid(axis='y')

    for bar, val in zip(bars1, retr_rates):
        ax1.text(bar.get_x() + bar.get_width()/2.0, val + 2.5, f"{val:.0f}%", ha='center', fontsize=9, fontweight='bold')

    # Panel B: Context Token Compaction
    colors_tok = ['#aec7e8', '#aec7e8', '#d62728', '#aec7e8', '#1f77b4']
    bars2 = ax2.bar(baselines, tokens, color=colors_tok, width=0.55, edgecolor='black', lw=0.8)
    ax2.set_ylabel('Average Prompt Tokens', fontweight='bold')
    ax2.set_ylim(0, 1300)
    ax2.set_title('(b) Evidence Fusion Compaction\n(26.7% Token Reduction vs Sim-Only)', fontweight='bold')
    ax2.grid(axis='y')

    for bar, val in zip(bars2, tokens):
        ax2.text(bar.get_x() + bar.get_width()/2.0, val + 25, f"{val}", ha='center', fontsize=9, fontweight='bold')

    fig.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig2_efficiency_tradeoffs.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig2_efficiency_tradeoffs.png")
    fig.savefig(pdf_path)
    fig.savefig(png_path)
    plt.close(fig)
    print(f"Generated Figure 2: {png_path}")

def generate_figure3_recall_vs_tokens():
    """Figure 3: Pareto Tradeoff: Recall@5 vs Context Token Overhead."""
    methods = [
        ('Random', 0.350, 542, '#7f7f7f'),
        ('Std RAG', 0.625, 509, '#9467bd'),
        ('AMORA (Ours)', 0.850, 786, '#1f77b4'),
        ('INKER', 0.900, 806, '#2ca02c'),
        ('Fixed-Wt', 0.950, 1043, '#ff7f0e'),
        ('Sim-Only', 1.000, 1073, '#d62728'),
    ]

    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=300)

    for name, r5, tok, col in methods:
        size = 130 if 'AMORA' in name else 85
        ax.scatter(tok, r5, color=col, s=size, edgecolors='black', lw=1.0, zorder=4)
        offset_x = 18 if 'AMORA' not in name else -120
        offset_y = 0.015 if 'AMORA' in name else -0.025
        ax.annotate(name, (tok, r5), xytext=(tok + offset_x, r5 + offset_y),
                    fontsize=9, fontweight='bold' if 'AMORA' in name else 'normal')

    # Draw Pareto boundary
    ax.plot([509, 786, 806, 1043, 1073], [0.625, 0.850, 0.900, 0.950, 1.000],
            color='#1f77b4', ls='--', lw=1.2, alpha=0.7, label='Empirical Tradeoff Frontier')

    ax.set_xlabel('Prompt Token Overhead (Tokens per Query)', fontweight='bold')
    ax.set_ylabel('Routing Recall@5', fontweight='bold')
    ax.set_xlim(450, 1200)
    ax.set_ylim(0.25, 1.08)
    ax.set_title('Figure 3: Retrieval Quality vs Token Footprint', fontweight='bold', pad=12)
    ax.grid(True)
    ax.legend(loc='lower right')

    fig.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig3_pareto_tradeoff.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig3_pareto_tradeoff.png")
    fig.savefig(pdf_path)
    fig.savefig(png_path)
    plt.close(fig)
    print(f"Generated Figure 3: {png_path}")

if __name__ == '__main__':
    generate_figure1_scalability()
    generate_figure2_efficiency_tradeoffs()
    generate_figure3_recall_vs_tokens()
    print("All 3 publication figures generated successfully.")
