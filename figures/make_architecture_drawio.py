"""Generate an editable draw.io (diagrams.net) version of the AMORA architecture.

Open `amora_architecture.drawio` at https://app.diagrams.net or with the VS Code
"Draw.io Integration" extension, edit, then File > Export as > PDF for LaTeX.
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "amora_architecture.drawio")
S = 70          # px per layout unit
TOP = 14.0      # layout y of the top edge

C = {
    "krt": ("#FBE9E7", "#D84315"),
    "kqf": ("#E3F2FD", "#1565C0"),
    "route": ("#EDE7F6", "#4527A0"),
    "fuse": ("#E8F5E9", "#2E7D32"),
    "gen": ("#FFF8E1", "#EF6C00"),
    "neutral": ("#FFFFFF", "#546E7A"),
    "query": ("#FFFFFF", "#7CB342"),
}
cells = []


def px(x, y):
    return round(x * S), round((TOP - y) * S)


def add_box(cid, cx, cy, w, h, title, lines, kind, dashed=False, align="center", fs=12):
    fc, ec = C[kind]
    x, y = px(cx - w / 2, cy + h / 2)
    html = ""
    if title:
        html += f'<b><font style="font-size:{fs + 1}px" color="{ec}">{escape(title)}</font></b><br>'
    html += "<br>".join(escape(l) for l in lines)
    style = (f"rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={ec};"
             f"strokeWidth=2;fontSize={fs};fontColor=#263238;align={align};spacingLeft=8;"
             f"fontFamily=Helvetica;" + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="{cid}" value="{escape(html, {chr(34): "&quot;"})}" style="{style}" '
                 f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{round(w*S)}" '
                 f'height="{round(h*S)}" as="geometry"/></mxCell>')


def add_tag(cid, x, y, text, kind):
    fc, ec = C[kind]
    w = 0.16 * len(text) + 0.4
    gx, gy = px(x, y + 0.2)
    cells.append(f'<mxCell id="{cid}" value="{escape(text)}" style="rounded=1;whiteSpace=wrap;'
                 f'html=1;fillColor={fc};strokeColor={ec};fontColor={ec};fontStyle=1;fontSize=15;" '
                 f'vertex="1" parent="1"><mxGeometry x="{gx}" y="{gy}" width="{round(w*S)}" '
                 f'height="28" as="geometry"/></mxCell>')


def add_text(cid, x, y, text, color="#78909C", fs=12, w=4.0, bold=True):
    gx, gy = px(x - w / 2, y + 0.2)
    cells.append(f'<mxCell id="{cid}" value="{escape(text)}" style="text;html=1;align=center;'
                 f'verticalAlign=middle;fontSize={fs};fontColor={color};'
                 f'fontStyle={1 if bold else 0};" vertex="1" parent="1"><mxGeometry x="{gx}" '
                 f'y="{gy}" width="{round(w*S)}" height="28" as="geometry"/></mxCell>')


_eid = [0]


def add_edge(src, tgt, label="", dashed=False, extra="", points=(), arrow=True, color="#263238"):
    _eid[0] += 1
    style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;strokeColor={color};"
             f"fontSize=11;fontStyle=1;endArrow={'block' if arrow else 'none'};endFill=1;"
             + ("dashed=1;" if dashed else "") + extra)
    pts = ""
    if points:
        pts = "<Array as=\"points\">" + "".join(
            f'<mxPoint x="{px(*p)[0]}" y="{px(*p)[1]}"/>' for p in points) + "</Array>"
    cells.append(f'<mxCell id="e{_eid[0]}" value="{escape(escape(label).replace(chr(10), "<br>"))}" style="{style}" edge="1" '
                 f'parent="1" source="{src}" target="{tgt}"><mxGeometry relative="1" '
                 f'as="geometry">{pts}</mxGeometry></mxCell>')


def add_sep(cid, y):
    x0, yy = px(0.2, y)
    x1, _ = px(15.8, y)
    cells.append(f'<mxCell id="{cid}" style="endArrow=none;html=1;dashed=1;strokeColor=#9E9E9E;'
                 f'strokeWidth=2;" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="{x0}" y="{yy}" as="sourcePoint"/><mxPoint x="{x1}" y="{yy}" '
                 f'as="targetPoint"/></mxGeometry></mxCell>')


# ------------------------------------------------------------------ boxes ---
add_box("query", 8.3, 13.43, 14.6, 0.62, None,
        ["Query:  What is the current stock of SKU-1042 in the Chennai warehouse, "
         "and does it match the Q3 inventory report?"], "query", dashed=True, align="left", fs=13)
add_sep("s1", 12.8)
add_tag("t1", 2.0, 12.45, "IE-KRT", "krt")
add_box("eval", 3.75, 11.7, 2.9, 1.05, "Evaluator",
        ["Complexity  E = 0.72", "Sensitivity  Sᵢ = 0.76"], "krt")
add_box("selfa", 3.75, 10.55, 2.9, 0.85, "LLM Self-Assessment", ["Confidence  mᵢ = 0.18"], "krt")
add_box("kscore", 8.0, 11.1, 3.5, 1.0, "Activation Score",
        ["K(tᵢ) = (E − mᵢ) · Sᵢ = 0.41"], "neutral")
add_box("presp", 13.4, 11.1, 3.4, 1.0, "Parametric Response",
        ["Direct LLM answer, 0 ms retrieval", "(35.0% of queries bypassed)"], "neutral", dashed=True)
add_sep("s2", 9.9)
add_tag("t2", 2.0, 9.6, "IE-KQF", "kqf")
add_box("phr", 3.95, 8.4, 3.3, 1.3, "Internal Phrases (LLM)",
        ["SKU-1042, Chennai warehouse,", "Q3 inventory report"], "kqf")
add_box("intent", 8.0, 8.4, 3.3, 1.3, "Intent Tokens",
        ["live stock lookup +", "cross-source verification"], "kqf")
add_box("qplus", 13.1, 8.4, 4.0, 1.3, "Reformulated Query q⁺",
        ["current stock SKU-1042 Chennai", "warehouse | compare Q3 inventory report"], "kqf")
add_sep("s3", 7.1)
add_tag("t3", 2.0, 6.8, "AMORA Routing", "route")
add_box("funnel", 13.1, 5.6, 4.0, 1.3, "Two-Stage FAISS Funnel",
        ["N = 10,000 → M = 55 candidates", "3.26 ms  |  SRR = 99.45%"], "route")
add_box("moo", 8.0, 5.6, 3.3, 1.3, "6-D Multi-Objective Scoring",
        ["R, L, F, C, H, K", "Σⱼ Wⱼ = 1 (Pareto-optimal)"], "route")
add_box("topk", 3.95, 5.6, 3.3, 1.3, "Top-K Selected Tools",
        ["inventory_db (SQL)", "stock_api (REST), q3_report (DOC)"], "route")
add_sep("s4", 4.4)
add_tag("t4", 2.0, 4.1, "Evidence Fusion", "fuse")
add_box("outs", 3.95, 2.9, 3.3, 1.3, "Tool Outputs",
        ["SQL: 150 units (2 h ago)", "REST: 150 units (live)", "DOC: 90 units (Q3 snapshot)"], "fuse")
add_box("engine", 8.0, 2.9, 3.3, 1.3, "Fusion Engine",
        ["Hash-window dedup: 3 → 2 facts", "O(E²) conflict graph: 150 vs 90",
         "Prompt tokens −26.7%"], "fuse")
add_box("fused", 13.1, 2.9, 4.0, 1.3, "Fused Evidence Context",
        ["[FACT] stock = 150 (fresh, reliable)", "[CONFLICT] Q3 report = 90 (stale)",
         "provenance tags attached"], "fuse")
add_sep("s5", 1.85)
add_box("llm", 13.1, 0.6, 3.0, 1.05, "Local LLM", ["Qwen 2.5 7B (Q4_K_M)", "zero data egress"], "gen")
add_box("answer", 6.25, 0.6, 7.7, 1.05, None,
        ["SKU-1042 currently has 150 units in the Chennai warehouse [inventory_db,",
         "updated 2 h ago]. Note: the Q3 report lists 90 units; the gap reflects",
         "post-Q3 restocking, so the live ledger value is authoritative."],
        "query", align="left")
add_text("cap", 6.25, -0.1, "LLM Continual Generation based on Fused Evidence", w=6.0)
add_text("iter", 0.35, 6.3, "↻ Iteration", color="#1565C0", fs=13, w=1.6)

# ------------------------------------------------------------------ edges ---
trunk = "exitX=0.03;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
add_edge("query", "eval", extra=trunk)
add_edge("query", "selfa", extra=trunk)
add_edge("query", "phr", extra=trunk)
add_edge("eval", "kscore", extra="edgeStyle=none;")
add_edge("selfa", "kscore", extra="edgeStyle=none;")
add_edge("kscore", "presp", label="K < θ\nNo Need Retrieval")
add_edge("kscore", "intent", label="K ≥ θ = 0.25\nNeed Retrieval")
add_edge("phr", "intent")
add_edge("intent", "qplus", label="concat")
add_edge("qplus", "funnel", label="Retrieval")
add_edge("funnel", "moo")
add_edge("moo", "topk")
add_edge("topk", "outs")
add_edge("outs", "engine")
add_edge("engine", "fused")
add_edge("fused", "llm")
add_edge("llm", "answer")
add_edge("answer", "eval", dashed=True,
         extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.1;entryDx=0;entryDy=0;",
         points=[(0.7, 0.6), (0.7, 12.2), (1.7, 12.2)])

xml = ('<mxfile host="app.diagrams.net"><diagram name="AMORA Architecture">'
       '<mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
       'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1150" '
       'pageHeight="1000" math="0" shadow="0"><root><mxCell id="0"/>'
       '<mxCell id="1" parent="0"/>' + "".join(cells) +
       '</root></mxGraphModel></diagram></mxfile>')
with open(OUT, "w", encoding="utf-8") as f:
    f.write(xml)
print("Saved", OUT)
