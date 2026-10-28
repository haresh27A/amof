"""Render the AMORA architecture diagram (PDF + PNG) in the banded, example-driven
style of the INKER base paper: Query -> IE-KRT -> IE-KQF -> AMORA Routing ->
Evidence Fusion -> Local LLM generation (with iteration loop)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans",
                     "svg.fonttype": "none"})  # keep SVG text editable

fig, ax = plt.subplots(figsize=(16, 13.2))
ax.set_xlim(0, 16)
ax.set_ylim(-0.2, 14.0)
ax.axis("off")

INK = "#263238"
GREY = "#78909C"
C = {
    "krt": ("#FBE9E7", "#D84315"),
    "kqf": ("#E3F2FD", "#1565C0"),
    "route": ("#EDE7F6", "#4527A0"),
    "fuse": ("#E8F5E9", "#2E7D32"),
    "gen": ("#FFF8E1", "#EF6C00"),
    "neutral": ("#FFFFFF", "#546E7A"),
    "query": ("#FFFFFF", "#7CB342"),
}


def box(cx, cy, w, h, title, lines, kind, dashed=False, fs=9.6, title_fs=10.2,
        align="center"):
    fc, ec = C[kind]
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.14",
                                fc=fc, ec=ec, lw=1.9, ls="--" if dashed else "-"))
    y = cy + h / 2 - 0.24
    if title:
        ax.text(cx, y, title, ha="center", va="center", fontsize=title_fs,
                fontweight="bold", color=ec)
        y -= 0.34
    xs = cx if align == "center" else cx - w / 2 + 0.15
    for ln in lines:
        ax.text(xs, y, ln, ha=align, va="center", fontsize=fs, color=INK)
        y -= 0.29


def arrow(p, q, color=INK, ls="-", lw=1.7):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=15,
                                 lw=lw, color=color, linestyle=ls,
                                 shrinkA=0, shrinkB=0))


def line(xs, ys, color=INK, ls="-", lw=1.7):
    ax.plot(xs, ys, color=color, ls=ls, lw=lw, solid_capstyle="butt")


def tag(x, y, text, kind):
    fc, ec = C[kind]
    ax.text(x, y, text, ha="left", va="center", fontsize=11.5, fontweight="bold",
            color=ec, bbox=dict(boxstyle="round,pad=0.3", fc=fc, ec=ec, lw=1.2))


def sep(y):
    line([0.2, 15.8], [y, y], color="#9E9E9E", ls=(0, (6, 4)), lw=1.6)


def note(x, y, s, color=GREY, fs=9.2, **kw):
    ax.text(x, y, s, ha="center", va="center", fontsize=fs, color=color,
            fontweight="bold", **kw)


# ---------------------------------------------------------------- Query ----
ax.add_patch(FancyBboxPatch((1.0, 13.12), 14.6, 0.62,
                            boxstyle="round,pad=0.02,rounding_size=0.14",
                            fc="white", ec=C["query"][1], lw=1.8, ls="--"))
ax.text(1.2, 13.43, "Query:", fontsize=10.5, fontweight="bold", va="center", color=INK)
ax.text(2.15, 13.43, "What is the current stock of SKU-1042 in the Chennai warehouse, "
        "and does it match the Q3 inventory report?", fontsize=10.3, va="center",
        color=INK)
sep(12.8)

X_TRUNK = 1.7
line([X_TRUNK, X_TRUNK], [13.12, 8.4])

# --------------------------------------------------------------- IE-KRT ----
tag(2.0, 12.45, "IE-KRT", "krt")
box(3.75, 11.7, 2.9, 1.05, "Evaluator", [r"Complexity  $E = 0.72$",
                                         r"Sensitivity  $S_i = 0.76$"], "krt")
box(3.75, 10.55, 2.9, 0.85, "LLM Self-Assessment", [r"Confidence  $m_i = 0.18$"], "krt")
arrow((X_TRUNK, 11.65), (2.3, 11.65))
arrow((X_TRUNK, 10.55), (2.3, 10.55))

box(8.0, 11.1, 3.5, 1.0, "Activation Score",
    [r"$K(t_i) = (E - m_i)\cdot S_i = 0.41$"], "neutral")
arrow((5.2, 11.65), (6.25, 11.25))
arrow((5.2, 10.55), (6.25, 10.95))

box(13.4, 11.1, 3.4, 1.0, "Parametric Response",
    ["Direct LLM answer, 0 ms retrieval", "(35.0% of queries bypassed)"],
    "neutral", dashed=True, fs=9.0)
arrow((9.75, 11.1), (11.7, 11.1))
note(10.72, 11.38, r"$K < \theta$", INK)
note(10.72, 10.82, "No Need Retrieval", INK, fs=8.6)
sep(9.9)

# --------------------------------------------------------------- IE-KQF ----
tag(2.0, 9.6, "IE-KQF", "kqf")
arrow((8.0, 10.6), (8.0, 9.05))
note(9.3, 9.5, r"$K \geq \theta = 0.25$", INK)
note(9.3, 9.22, "Need Retrieval", INK, fs=8.6)

box(3.95, 8.4, 3.3, 1.3, "Internal Phrases (LLM)",
    ["SKU-1042, Chennai warehouse,", "Q3 inventory report"], "kqf")
arrow((X_TRUNK, 8.4), (2.3, 8.4))
box(8.0, 8.4, 3.3, 1.3, "Intent Tokens",
    ["live stock lookup +", "cross-source verification"], "kqf")
box(13.1, 8.4, 4.0, 1.3, "Reformulated Query  $q^{+}$",
    ["current stock SKU-1042 Chennai", "warehouse | compare Q3 inventory report"],
    "kqf", fs=9.2)
arrow((5.6, 8.4), (6.35, 8.4))
arrow((9.65, 8.4), (11.1, 8.4))
note(10.38, 8.68, "concat", GREY, fs=8.6)
sep(7.1)

# -------------------------------------------------------- AMORA routing ----
tag(2.0, 6.8, "AMORA Routing", "route")
box(13.1, 5.6, 4.0, 1.3, "Two-Stage FAISS Funnel",
    [r"$N = 10{,}000 \rightarrow M = 55$ candidates",
     "3.26 ms  |  SRR = 99.45%"], "route")
box(8.0, 5.6, 3.3, 1.3, "6-D Multi-Objective Scoring",
    [r"$R, L, F, C, H, K$", r"$\Sigma_j W_j = 1$ (Pareto-optimal)"], "route")
box(3.95, 5.6, 3.3, 1.3, "Top-K Selected Tools",
    ["inventory_db (SQL)", "stock_api (REST), q3_report (DOC)"], "route", fs=9.0)
arrow((13.1, 7.75), (13.1, 6.25))
note(13.75, 7.0, "Retrieval", GREY, fs=8.6,
     bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
arrow((11.1, 5.6), (9.65, 5.6))
arrow((6.35, 5.6), (5.6, 5.6))
sep(4.4)

# ------------------------------------------------------ Evidence fusion ----
tag(2.0, 4.1, "Evidence Fusion", "fuse")
box(3.95, 2.9, 3.3, 1.3, "Tool Outputs",
    ["SQL: 150 units (2 h ago)", "REST: 150 units (live)", "DOC: 90 units (Q3 snapshot)"],
    "fuse", fs=8.9)
box(8.0, 2.9, 3.3, 1.3, "Fusion Engine",
    ["Hash-window dedup: 3 → 2 facts", r"$O(E^2)$ conflict graph: 150 vs 90",
     "Prompt tokens −26.7%"], "fuse", fs=8.9)
box(13.1, 2.9, 4.0, 1.3, "Fused Evidence Context",
    ["[FACT] stock = 150  (fresh, reliable)", "[CONFLICT] Q3 report = 90  (stale)",
     "provenance tags attached"], "fuse", fs=8.9)
arrow((3.95, 4.95), (3.95, 3.55))
arrow((5.6, 2.9), (6.35, 2.9))
arrow((9.65, 2.9), (11.1, 2.9))
sep(1.85)

# ----------------------------------------------------------- Generation ----
box(13.1, 0.6, 3.0, 1.05, "Local LLM", ["Qwen 2.5 7B (Q4_K_M)", "zero data egress"],
    "gen", fs=9.0)
arrow((13.1, 2.25), (13.1, 1.13))
box(6.25, 0.6, 7.7, 1.05, None,
    ["SKU-1042 currently has 150 units in the Chennai warehouse [inventory_db,",
     "updated 2 h ago]. Note: the Q3 report lists 90 units; the gap reflects",
     "post-Q3 restocking, so the live ledger value is authoritative."],
    "query", fs=9.0, align="left")
note(6.25, -0.1, "LLM Continual Generation based on Fused Evidence", GREY, fs=9.4)
arrow((11.6, 0.6), (10.1, 0.6))

# Iteration loop (dashed) back to IE-KRT
line([2.4, 0.7], [0.6, 0.6], ls=(0, (5, 3)))
line([0.7, 0.7], [0.6, 12.2], ls=(0, (5, 3)))
arrow((0.7, 12.2), (X_TRUNK, 12.2), ls=(0, (5, 3)))
ax.text(0.42, 6.3, "Iteration", rotation=90, ha="center", va="center",
        fontsize=10, fontweight="bold", color=C["kqf"][1])
ax.text(0.42, 7.75, "↻", ha="center", va="center", fontsize=18, color=C["kqf"][1])

plt.tight_layout()
for ext in ("pdf", "png", "svg"):
    fig.savefig(os.path.join(OUT_DIR, f"amora_architecture.{ext}"),
                dpi=300, bbox_inches="tight")
print("Saved amora_architecture.pdf/.png to", OUT_DIR)
