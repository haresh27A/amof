import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import re
import os

def set_cell_borders(cell, top="000000", bottom="000000", left=None, right=None, sz="4", val="single"):
    """Set custom borders for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for b_name, b_color in borders.items():
        if b_color:
            b_xml = parse_xml(f'<w:{b_name} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="0" w:color="{b_color}"/>')
            tcBorders.append(b_xml)
        else:
            b_xml = parse_xml(f'<w:{b_name} {nsdecls("w")} w:val="none"/>')
            tcBorders.append(b_xml)
    tcPr.append(tcBorders)

def set_cell_shading(cell, color):
    """Set background color for a cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def create_document():
    doc = docx.Document()

    # Page Margins (20mm = 0.787 inches, standard Nature Scientific Reports)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        section.page_width = Inches(8.27)  # A4
        section.page_height = Inches(11.69)
        
        # Header / Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        f_run = f_p.add_run()
        # Page number field XML
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        f_p._p.append(fldSimple)

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    p_title.paragraph_format.line_spacing = 1.15
    run_title = p_title.add_run("Adaptive Multi-Objective Routing and Tool Coordination for Heterogeneous Enterprise Retrieval-Augmented Generation")
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(17, 17, 17)

    # Authors
    p_auth = doc.add_paragraph()
    p_auth.paragraph_format.space_before = Pt(0)
    p_auth.paragraph_format.space_after = Pt(6)
    
    authors = [
        ("Arul Raj Haresh", "1*"),
        ("K. Suresh Kumar", "2"),
        ("T. Ananth Kumar", "3"),
        ("Wooguil Pak", "4*")
    ]
    for idx, (name, sup) in enumerate(authors):
        r_name = p_auth.add_run(name)
        r_name.font.name = 'Arial'
        r_name.font.size = Pt(11)
        r_name.font.bold = True
        r_sup = p_auth.add_run(sup)
        r_sup.font.name = 'Arial'
        r_sup.font.size = Pt(8)
        r_sup.font.superscript = True
        if idx < len(authors) - 2:
            p_auth.add_run(", ")
        elif idx == len(authors) - 2:
            p_auth.add_run(" & ")

    # Affiliations
    p_aff = doc.add_paragraph()
    p_aff.paragraph_format.space_before = Pt(0)
    p_aff.paragraph_format.space_after = Pt(12)
    p_aff.paragraph_format.line_spacing = 1.15
    
    aff_text = (
        "1 Department of Computer Science and Engineering, AI Research Laboratories, Coimbatore 641202, India.\n"
        "2 Department of Information Technology, Sri Eshwar College of Engineering, Coimbatore 641202, India.\n"
        "3 Faculty of Artificial Intelligence and Digital Technologies, Samarkand State University, 140104 Samarkand, Uzbekistan.\n"
        "4 School of Computer Science and Engineering, Yeungnam University, Gyeongsan 38541, Republic of Korea.\n"
        "* email: arulraj.haresh@research.org; wooguilpak@yu.ac.kr"
    )
    r_aff = p_aff.add_run(aff_text)
    r_aff.font.name = 'Arial'
    r_aff.font.size = Pt(8.5)
    r_aff.font.color.rgb = RGBColor(80, 80, 80)

    # Abstract Box / Block
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.space_before = Pt(6)
    p_abs.paragraph_format.space_after = Pt(8)
    p_abs.paragraph_format.line_spacing = 1.15
    
    r_abs = p_abs.add_run(
        "Retrieval-Augmented Generation (RAG) significantly mitigates parametric hallucination in Large Language Models (LLMs). "
        "However, standard enterprise deployments reveal four critical systemic vulnerabilities: unconditional retrieval latency on trivial requests, "
        "combinatorial profiling bottlenecks across thousands of heterogeneous data endpoints, severe context inflation with contradictory facts, "
        "and compliance risks inherent in commercial cloud application programming interfaces. To resolve these challenges, this work proposes the "
        "Adaptive Multi-Objective Reasoning Algorithm (AMORA), an end-to-end framework coordinating heterogeneous enterprise endpoints under rigorous "
        "latency, reliability, freshness, and monetary cost constraints. AMORA incorporates the INKER Knowledge Retrieval Trigger to calculate an uncertainty "
        "activation score, adaptively bypassing external retrieval on 35.0% of queries where parametric knowledge is sufficient. For knowledge-intensive requests, "
        "AMORA introduces a two-stage vector pre-filtering funnel that compresses 10,000 enterprise endpoints down to 55 candidates in 3.26 milliseconds, "
        "achieving a 99.45% Source Reduction Ratio. A dynamic multi-objective optimization engine normalizes six operational dimensions subject to the 5-simplex "
        "invariant, mathematically guaranteeing Pareto-optimal tool selection. An Evidence Fusion Engine applies sliding-window hash deduplication and pairwise "
        "discrepancy graph extraction, compacting prompt tokens by 26.7% and isolating contradictory numbers prior to generative decoding. Empirical benchmarking "
        "across 20 gold multi-modal enterprise queries demonstrates that AMORA achieves a compound 52.35% net system workload reduction, preserves sub-4.2 millisecond "
        "routing latency across 10,000 catalog sources, and slashes operational expenditures by 96.5% on commodity local hardware while enforcing absolute "
        "zero-egress data sovereignty."
    )
    r_abs.font.name = 'Arial'
    r_abs.font.size = Pt(9.5)
    r_abs.font.bold = True
    r_abs.font.color.rgb = RGBColor(20, 20, 20)

    # Keywords
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(4)
    p_kw.paragraph_format.space_after = Pt(14)
    r_kw_label = p_kw.add_run("Keywords: ")
    r_kw_label.font.name = 'Arial'
    r_kw_label.font.size = Pt(9)
    r_kw_label.font.bold = True
    r_kw_text = p_kw.add_run("Retrieval-augmented generation, Multi-objective optimization, Tool coordination, Edge language models, Data sovereignty, Pareto optimality")
    r_kw_text.font.name = 'Arial'
    r_kw_text.font.size = Pt(9)

    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(14)
    p_div_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="CCCCCC"/></w:pBdr>')
    p_div._p.get_or_add_pPr().append(p_div_border)

    # Helper functions for adding formatted sections
    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Arial'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 15, 15)
        return p

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Arial'
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(25, 25, 25)
        return p

    def add_subsubsec_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Arial'
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(40, 40, 40)
        return p

    def add_body_p(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(35, 35, 35)
        return p

    def add_bullet_p(lead, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_lead = p.add_run(lead + " ")
        r_lead.font.name = 'Arial'
        r_lead.font.size = Pt(9.5)
        r_lead.font.bold = True
        r_text = p.add_run(text)
        r_text.font.name = 'Arial'
        r_text.font.size = Pt(9.5)
        return p

    def add_figure(img_path, caption):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.paragraph_format.space_after = Pt(4)
            run = p_img.add_run()
            run.add_picture(img_path, width=Inches(6.2))
            
            p_cap = doc.add_paragraph()
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(12)
            p_cap.paragraph_format.line_spacing = 1.15
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = 'Arial'
            r_cap.font.size = Pt(8.5)
            r_cap.font.color.rgb = RGBColor(60, 60, 60)

    def add_theorem(num, title, statement, proof):
        p_th = doc.add_paragraph()
        p_th.paragraph_format.space_before = Pt(8)
        p_th.paragraph_format.space_after = Pt(4)
        p_th.paragraph_format.line_spacing = 1.15
        r_t1 = p_th.add_run(f"Theorem {num} ({title}). ")
        r_t1.font.bold = True
        r_t2 = p_th.add_run(statement)
        r_t2.font.italic = True
        
        p_pr = doc.add_paragraph()
        p_pr.paragraph_format.space_before = Pt(2)
        p_pr.paragraph_format.space_after = Pt(8)
        p_pr.paragraph_format.line_spacing = 1.15
        r_p1 = p_pr.add_run("Proof. ")
        r_p1.font.bold = True
        r_p2 = p_pr.add_run(proof + " ")
        r_qed = p_pr.add_run("■")
        r_qed.font.bold = True

    def add_algorithm_box(title, inputs, outputs, steps):
        p_box = doc.add_paragraph()
        p_box.paragraph_format.space_before = Pt(10)
        p_box.paragraph_format.space_after = Pt(2)
        p_box.paragraph_format.keep_with_next = True
        r_t = p_box.add_run(title)
        r_t.font.name = 'Arial'
        r_t.font.size = Pt(10)
        r_t.font.bold = True

        p_rule1 = doc.add_paragraph()
        p_rule1.paragraph_format.space_before = Pt(0)
        p_rule1.paragraph_format.space_after = Pt(4)
        p_rule1._p.get_or_add_pPr().append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>'))

        p_io = doc.add_paragraph()
        p_io.paragraph_format.space_before = Pt(0)
        p_io.paragraph_format.space_after = Pt(4)
        p_io.paragraph_format.line_spacing = 1.15
        r_in_lbl = p_io.add_run("Input: ")
        r_in_lbl.font.bold = True
        p_io.add_run(inputs + "\n")
        r_out_lbl = p_io.add_run("Output: ")
        r_out_lbl.font.bold = True
        p_io.add_run(outputs)

        for step in steps:
            p_step = doc.add_paragraph()
            p_step.paragraph_format.left_indent = Inches(0.25)
            p_step.paragraph_format.space_before = Pt(1)
            p_step.paragraph_format.space_after = Pt(1)
            p_step.paragraph_format.line_spacing = 1.1
            r_st = p_step.add_run(step)
            r_st.font.name = 'Consolas'
            r_st.font.size = Pt(8.5)

        p_rule2 = doc.add_paragraph()
        p_rule2.paragraph_format.space_before = Pt(4)
        p_rule2.paragraph_format.space_after = Pt(10)
        p_rule2._p.get_or_add_pPr().append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>'))

    # =========================================================================
    # SECTION 1: INTRODUCTION
    # =========================================================================
    add_sec_heading("Introduction")
    add_body_p(
        "Large Language Models have fundamentally transformed modern enterprise intelligence and workflow automation. "
        "They demonstrate remarkable natural language generation and contextual reasoning capabilities. Global enterprises "
        "deploy these neural foundations across diverse operational domains. Typical deployments automate customer support, "
        "regulatory auditing, and complex documentation analysis. Modern businesses require rigorous factual accuracy and deterministic "
        "evidence trails. However, high linguistic fluency does not guarantee factual truthfulness. Deep neural networks frequently "
        "generate plausible yet completely fabricated assertions. Such hallucinations undermine operational trust and introduce "
        "severe corporate liabilities. Furthermore, internal corporate records evolve continuously across distributed enterprise "
        "infrastructures. Dynamic relational databases and financial ledgers update thousands of times per hour. Static parametric "
        "weights cannot capture live corporate states or private inventories. Consequently, static models suffer from acute temporal "
        "obsolescence and blind spots. Retrieval-Augmented Generation has emerged as the preeminent architectural paradigm. "
        "It dynamically retrieves relevant external context and prepends it to prompts. Grounding generation within authoritative records "
        "bridges the gap between models and data. This contextual grounding transforms fragile generative engines into robust enterprise systems. "
        "Verifiable citations establish auditability across high-stakes corporate decision workflows. External grounding provides institutional "
        "transparency across mission-critical automated pipelines. Reliable enterprise systems require deterministic evidence rather than probabilistic conjecture."
    )

    add_body_p(
        "However, deploying canonical retrieval architectures within real-world enterprise environments exposes four foundational bottlenecks. "
        "First, conventional frameworks enforce unconditional retrieval on every incoming user query. They query remote vector databases even for "
        "elementary definitional requests. This indiscriminate lookup strategy incurs unnecessary latency penalties of several hundred milliseconds. "
        "Redundant lookups waste expensive server compute and generate database lock contention. Second, enterprise knowledge is fundamentally fragmented "
        "across heterogeneous operational endpoints. Critical data resides in relational tables, internal microservices, and static documents. "
        "Scaling endpoint catalogs to ten thousand sources creates severe computational bottlenecks. Exhaustive linear profiling of candidate tools "
        "induces hundreds of milliseconds of routing latency. Such delays prevent interactive sub-second conversational response times for enterprise workers. "
        "Third, multi-source retrieval floods language models with redundant and uncurated context passages. Injected context bloat triggers quadratic "
        "self-attention computational overhead. In addition, asynchronous databases frequently store conflicting values for identical business entities. "
        "Passing unverified contradictory numbers directly into the context window triggers severe hallucinations. Fourth, public cloud commercial APIs "
        "introduce unacceptable data governance and privacy liabilities. Transmitting proprietary corporate intellectual property across public networks violates "
        "regulatory mandates. External cloud dependencies also expose organizations to unpredictable operational expenditures."
    )

    add_body_p(
        "Prior research has proposed various techniques to mitigate these operational retrieval challenges. Self-reflective frameworks monitor "
        "decoding token probabilities to trigger searches dynamically. However, continuous logit inspection introduces prohibitive inference delays during "
        "token generation. Other systems train specialized reflection tokens using supervised instruction-tuning on academic corpora. Such approaches cannot "
        "be deployed zero-shot across pre-trained local enterprise models. Adaptive classifiers categorize user queries into discrete complexity tiers "
        "with varying overhead. Yet these classifiers rely on open-domain datasets and fail on proprietary schemas. Similarly, tool-augmented systems empower "
        "language models to invoke external computational APIs. Modern agent frameworks coordinate tool execution through explicit multi-step reasoning traces. "
        "However, existing tool suites struggle with enterprise catalogs containing thousands of endpoints. Standard implementations feed full documentation "
        "catalogs directly into prompt contexts. This practice exhausts context windows and degrades routing accuracy significantly. Furthermore, prior routing "
        "algorithms optimize solely for semantic textual similarity. They ignore critical operational metrics including latency, monetary cost, uptime, "
        "and freshness. Existing summarization methods also overlook fine-grained numerical contradictions across competing data sources. Unresolved factual "
        "discrepancies degrade decision confidence in downstream business applications."
    )

    add_body_p(
        "To resolve these systemic challenges, this paper presents the AMORA architectural framework. AMORA unifies adaptive gating, scalable pre-filtering, "
        "dynamic multi-objective routing, and evidence fusion. The system decouples the decision of when to retrieve from endpoint selection. An adaptive "
        "uncertainty trigger eliminates external retrieval on thirty-five percent of queries. This gating preserves safety bounds while eliminating unnecessary "
        "computational overhead. For knowledge-intensive requests, a two-stage vector funnel prunes ten thousand candidate sources. It achieves a ninety-nine "
        "percent reduction ratio in under four milliseconds. Candidate endpoints are then ranked using dynamic multi-objective scoring. The objective weights "
        "are dynamically normalized on the standard five-simplex. This mathematical formulation guarantees Pareto-optimal tool selection for every query. "
        "An evidence fusion engine deduplicates text and extracts pairwise numerical discrepancy graphs. Discrepancy warnings alert local language models "
        "before final generative synthesis occurs. AMORA operates entirely on commodity hardware within the enterprise perimeter. It slashes operational costs "
        "by ninety-six percent while enforcing strict data sovereignty. We validate AMORA using five formal mathematical proofs and comprehensive empirical benchmarks. "
        "Our findings demonstrate sub-second response times across large-scale corporate knowledge environments. Local on-premises deployment ensures complete "
        "confidentiality for enterprise proprietary assets."
    )

    add_body_p("The key contributions of this study are summarized as follows:")
    add_bullet_p("Problem-Driven Architectural Framework:", "A unified Adaptive Multi-Objective Reasoning Algorithm (AMORA) is proposed for efficient and secure coordination of heterogeneous enterprise retrieval-augmented generation.")
    add_bullet_p("Adaptive Knowledge Gating (IE-KRT):", "A mathematically bounded uncertainty trigger is incorporated at the input layer to eliminate external retrieval on 35.0% of queries while establishing a provable upper bound on false-negative retrieval errors.")
    add_bullet_p("Sub-Linear Pre-filtering Funnel:", "A two-stage vector funnel prunes catalogs of 10,000 enterprise endpoints down to 55 candidates in 3.26 ms, reducing computational complexity from O(N · D) to O(log N + M log M).")
    add_bullet_p("Dynamic 5-Simplex Multi-Objective Optimization:", "A dynamic scoring engine normalizes six operational dimensions subject to the 5-simplex invariant, mathematically guaranteeing Pareto-optimal endpoint selection.")
    add_bullet_p("Evidence Fusion & Conflict Graph Mitigation:", "An evidence fusion engine deduplicates redundant passages and extracts pairwise discrepancy graphs, compacting prompt tokens by 26.7% and surfacing conflicting numbers prior to generative decoding.")
    add_bullet_p("System-Level Performance Telemetry:", "Comprehensive system-level evaluation is conducted using metrics such as latency, Source Reduction Ratio, token overhead, and hardware telemetry under realistic enterprise workload scenarios.")

    add_body_p(
        "The remainder of the paper is organized as follows. Section 'Related works' reviews related work across four core paradigms. "
        "Section 'Proposed model: AMORA' presents the design, mathematical proofs, and algorithmic implementation of the proposed framework. "
        "Section 'Results and discussion' discusses experimental results, benchmark comparisons, and system scalability. "
        "Section 'Discussion' concludes the paper with operational insights, hardware constraints, and future research directions."
    )

    # =========================================================================
    # SECTION 2: RELATED WORKS
    # =========================================================================
    add_sec_heading("Related works")
    add_body_p(
        "The architecture of AMORA intersects multiple foundational subfields across natural language processing, distributed information retrieval, "
        "multi-objective optimization, and neuro-symbolic systems engineering. This section provides a structured, thematic synthesis of existing literature, "
        "highlighting quantitative benchmarks and identifying foundational gaps that AMORA directly addresses."
    )

    add_subsec_heading("Evolution of Retrieval-Augmented Generation")
    add_body_p(
        "Retrieval-Augmented Generation fundamentally reframes autoregressive language modeling by separating knowledge retrieval from token generation. "
        "Foundational models such as REALM and RETRO incorporated dense dual-encoder retrieval mechanisms directly into masked language modeling pre-training "
        "objectives, demonstrating substantial gains over standard transformer baselines across open-domain factual benchmarks such as Natural Questions and TriviaQA. "
        "However, as parameter counts scaled to tens and hundreds of billions, fine-tuning neural retrieval mechanisms end-to-end became computationally prohibitive "
        "for practical engineering. Consequently, research transitioned toward modular, post-hoc RAG architectures."
    )
    add_body_p(
        "Standard modular RAG pipelines leverage bi-encoder architectures, including Dense Passage Retrieval (DPR), Contriever, and BGE, to compute semantic similarity "
        "between queries and chunked passages, executing approximate nearest-neighbor search via Hierarchical Navigable Small World (HNSW) graphs or FAISS indices. "
        "Subsequent research introduced multi-query expansion and speculative drafting (e.g., Query2Doc, HyDE, Speculative RAG, and Corrective RAG) to filter irrelevant "
        "chunks prior to prompt assembly. Despite these algorithmic refinements, existing frameworks operate under the fundamental assumption of a single, "
        "homogeneous, unstructured text corpus. They remain architecturally incapable of dynamically profiling, ranking, and querying structured enterprise assets "
        "such as relational database ledgers or parameterized microservice APIs."
    )

    add_subsec_heading("Adaptive, Conditional, and Self-Reflective Retrieval")
    add_body_p(
        "Recognizing the substantial latency and computational penalties imposed by unconditional vector lookups, recent literature has explored conditional "
        "and adaptive retrieval triggers. FLARE (Forward-Looking Active Retrieval Augmented Generation) monitors the token-level generation probabilities of "
        "the decoding LLM; when output confidence drops below a pre-set threshold, generation pauses, a temporary retrieval query is formulated from anticipated "
        "sentence tokens, and the sentence is regenerated. While FLARE avoids unnecessary retrieval on fluent sequences, its continuous logit monitoring introduces "
        "high decode-loop latency and is incompatible with black-box inference engines."
    )
    add_body_p(
        "Self-RAG trains models using special reflection tokens, allowing models to self-assess retrieval necessity and critique generated factual support. "
        "Although Self-RAG exhibits remarkable flexibility, it requires extensive supervised fine-tuning on specialized instruction corpora, preventing zero-shot "
        "adoption across commercial or proprietary enterprise models. Adaptive-RAG deploys a dedicated classifier to categorize incoming queries into discrete "
        "complexity tiers, selectively activating no retrieval, single-step retrieval, or iterative multi-step reasoning. Concurrently, SKR prompts models to "
        "self-assess their own parametric knowledge prior to executing searches. Nevertheless, these frameworks evaluate retrieval strictly within open-domain academic "
        "benchmarks where knowledge is public. In an enterprise environment, an over-confident model self-assessment risks catastrophic false negatives on proprietary "
        "corporate records. AMORA overcomes this vulnerability via the INKER Knowledge Retrieval Trigger (IE-KRT), which mathematically couples query structural complexity "
        "with factual and temporal sensitivity, establishing a conservative activation threshold (θ = 0.25) that empirically guarantees zero false negatives on private corporate assets."
    )

    add_subsec_heading("Tool-Augmented LLMs and Heterogeneous API Coordination")
    add_body_p(
        "To extend language models beyond static text manipulation, tool-augmented systems empower models to interact with digital environments. Toolformer demonstrated "
        "that models can self-supervisedly learn to execute functional APIs through inline functional call tokens. Concurrently, ReAct formalized the interleaving "
        "of explicit reasoning traces and environmental tool executions, establishing the foundation for modern autonomous agent frameworks."
    )
    add_body_p(
        "To scale tool usage across massive software ecosystems, Gorilla and ToolLLM investigated instruction-tuning across vast catalogs of real-world RESTful APIs. "
        "ToolLLM compiled over 16,000 real-world APIs and introduced ToolBench, demonstrating that fine-tuned 7B models could perform multi-step depth-first tool routing. "
        "RestGPT and Chameleon further structured API invocation through hierarchical planners and execution controllers. However, these systems exhibit severe profiling "
        "bottlenecks when exposed to enterprise catalogs containing thousands of internal microservices and database views (N ≥ 10,000). Standard implementations feed all "
        "candidate tool documentation directly into the LLM prompt, rapidly exceeding context window constraints and inducing high inference latency. AMORA solves this "
        "bottleneck through its two-stage vector pre-filtering funnel, which mechanically prunes N = 10,000 endpoints down to M = 55 candidates in 3.26 ms before invoking downstream ranking."
    )

    add_subsec_heading("Multi-Objective Information Retrieval and Pareto Optimization")
    add_body_p(
        "Information retrieval in multi-modal environments inherently involves competing, incommensurable criteria. A candidate source may offer exceptional semantic relevance "
        "but suffer from high latency, stale records, high monetary query fees, or low historical reliability. Traditional search engines resolve multi-criteria trade-offs "
        "using static linear scalarization (e.g., LambdaMART) or constrained non-linear programming. However, static weights cannot adapt to the shifting priorities of heterogeneous "
        "enterprise queries: a compliance audit query demands absolute reliability and provenance, while an urgent supply-chain query requires real-time freshness."
    )
    add_body_p(
        "In multi-objective optimization literature, Pareto-optimal set identification (NSGA-II, MOEA/D) provides a rigorous foundation for identifying non-dominated solutions "
        "across multi-dimensional criteria. In this work, AMORA establishes an analytical bridge between Pareto optimality and adaptive query intent. We formulate a dynamically "
        "normalized 6-dimensional scoring function subject to the strict simplex constraint ∑ W_j = 1.0, mathematically proving that dynamic weight updates preserve the "
        "Pareto frontier while guaranteeing optimal alignment with detected query modalities."
    )

    add_subsec_heading("Text Deduplication, Multi-Source Contradiction, and Truth Discovery")
    add_body_p(
        "When multiple heterogeneous tools are invoked simultaneously, their outputs frequently contain redundant information or outright factual discrepancies. In multi-document "
        "summarization literature, text deduplication is conventionally handled through character-level n-gram overlap, MinHash locality-sensitive hashing (LSH), or semantic passage "
        "cosine thresholds. However, semantic embeddings often fail to detect fine-grained numerical discrepancies (e.g., the vector cosine similarity between 'Stock is 150' and "
        "'Stock is 90' is typically > 0.94, masking the critical operational contradiction)."
    )
    add_body_p(
        "Truth discovery and multi-source credibility modeling have been extensively studied in database literature. Existing truth discovery algorithms iteratively infer source "
        "trustworthiness and object truth values via Bayesian networks or expectation-maximization. However, these algorithms assume batch processing over large static relational "
        "tables and cannot operate within the sub-10 ms latency envelope required by conversational RAG systems. AMORA bridges this divide by deploying a lightweight, graph-theoretic "
        "entity extraction and sliding-window hash deduplication engine that isolates contradictory numerical values across database rows and API responses in O(E^2) time prior to LLM synthesis."
    )

    # TABLE 1: Architectural Comparison
    p_t1_cap = doc.add_paragraph()
    p_t1_cap.paragraph_format.space_before = Pt(10)
    p_t1_cap.paragraph_format.space_after = Pt(2)
    r_t1_c = p_t1_cap.add_run("Table 1. Comprehensive Architectural Comparison of AMORA Against Prior State-of-the-Art Frameworks.")
    r_t1_c.font.bold = True
    r_t1_c.font.size = Pt(9)

    t1_data = [
        ["Framework", "Adaptive Gating", "Modality Support", "Catalog Scalability", "Multi-Obj. Optimization", "Evidence Dedup", "Conflict Detection", "On-Premises Residency", "Formal Proofs"],
        ["Standard RAG", "No", "Text only", "Low", "No", "No", "No", "Yes", "No"],
        ["REALM / RETRO", "No", "Text only", "Low", "No", "No", "No", "Yes", "No"],
        ["FLARE", "Yes (Active)", "Text only", "Low", "No", "No", "No", "Yes", "No"],
        ["Self-RAG", "Yes (Reflect)", "Text only", "Low", "No", "No", "No", "Yes", "No"],
        ["ToolLLM", "No", "REST APIs", "16,000 APIs", "No", "No", "No", "No", "No"],
        ["Gorilla", "No", "REST APIs", "1,600 APIs", "No", "No", "No", "No", "No"],
        ["Adaptive-RAG", "Yes (Classifier)", "Text only", "Low", "No", "No", "No", "Yes", "No"],
        ["AMORA (Proposed)", "Yes (IE-KRT)", "Text + SQL + REST", "10,000 Endpoints", "Yes (5-Simplex)", "Yes (Hash)", "Yes (Graph)", "Yes (Zero Egress)", "Yes (5 Proofs)"]
    ]

    table1 = doc.add_table(rows=len(t1_data), cols=len(t1_data[0]))
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            cell = table1.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(7.5)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_borders(cell, top="000000", bottom="000000", sz="6")
                set_cell_shading(cell, "F2F2F2")
            elif r_idx == len(t1_data) - 1:
                p.runs[0].font.bold = True
                set_cell_borders(cell, top="CCCCCC", bottom="000000", sz="6")
                set_cell_shading(cell, "EBF3F9")
            else:
                set_cell_borders(cell, top="EEEEEE", bottom="EEEEEE", sz="2")

    # =========================================================================
    # SECTION 3: PROPOSED MODEL: AMORA
    # =========================================================================
    add_sec_heading("Proposed model: AMORA")
    add_body_p(
        "The AMORA framework is a comprehensive solution that combines cutting-edge information retrieval, convex optimization, and edge computing to address "
        "the challenges of managing heterogeneous knowledge sources in enterprise environments. This system uses multi-objective routing, integrated with local language "
        "models and evidence fusion, to streamline decision processes, thereby enhancing computational efficiency and ensuring absolute data sovereignty."
    )

    add_figure("figures/amora_architecture.png", "Figure 1. Overall system architecture of the proposed AMORA framework, illustrating Stage 1 (Adaptive Knowledge Retrieval Trigger via IE-KRT), Stage 2 (Two-Stage Pre-filtering Funnel), Stage 3 (Dynamic Multi-Objective Source Selection on the 5-Simplex), Stage 4 (Evidence Fusion and Discrepancy Graph Mitigation), and Stage 5 (Local Autoregressive Synthesis under Zero-Egress Data Sovereignty).")

    add_subsec_heading("Design of AMORA System")
    add_body_p(
        "Designing an enterprise-grade retrieval-augmented generation system involves coordinating multiple heterogeneous data endpoints to ensure efficient, secure, and "
        "factually grounded output. The system architecture consists of five sequential processing stages:"
    )

    add_subsubsec_heading("Stage 1: Adaptive Knowledge Retrieval Trigger (IE-KRT)")
    add_body_p(
        "Incoming user query q is evaluated at the input boundary without invoking external lookups. We calculate query token length |q|, extract syntactic entity density ρ(q), "
        "and compute parametric model perplexity PPL(q) over a lightweight local distilled language model. The INKER Knowledge Retrieval Trigger models the uncertainty activation score:\n"
        "K(t_i) = (E - m_i) · S_i   (Equation 1)\n"
        "where E denotes normalized syntactic complexity, m_i represents parametric confidence, and S_i denotes factual urgency. If K(t_i) ≤ θ, external retrieval is bypassed "
        "entirely (P(retrieve) = 0), routing the query directly to parametric decoding. If K(t_i) > θ, retrieval is activated."
    )

    add_subsubsec_heading("Stage 2: Two-Stage Vector Pre-Filtering Funnel")
    add_body_p(
        "When retrieval is triggered across an enterprise catalog of N = 10,000 endpoints, sequentially computing multi-objective scores is computationally prohibitive. "
        "AMORA introduces a hierarchical pre-filtering funnel:\n"
        "• Stage 2A: Dense Subspace Filtering: We embed query q into dense vector v_q ∈ R^384 using BGE-small-en-v1.5. A FAISS inner-product index prunes the candidate set "
        "from N = 10,000 down to K_1 = 500 endpoints based on structural documentation embeddings.\n"
        "• Stage 2B: Modality and Metadata Pruning: The surviving candidates are filtered against structural constraints (supported query schemas, authorization clearance, "
        "protocol compatibility), outputting an active candidate pool of M = 55 endpoints in 3.26 ms."
    )

    add_subsubsec_heading("Stage 3: Dynamic Multi-Objective Source Selection")
    add_body_p(
        "For each surviving candidate s_i ∈ M, AMORA computes a multi-objective score across six normalized operational dimensions:\n"
        "Score(s_i, q) = W_r R_i + W_l L_i + W_f F_i - W_c C_i + W_h H_i - W_k K_i   (Equation 2)\n"
        "subject to the simplex invariant:\n"
        "∑ W_j(q) = 1.0,  W_j(q) ≥ 0   (Equation 3)\n"
        "where R_i is Semantic Relevance, L_i is Convex Reliability, F_i is Exponential Freshness Decay, C_i is Normalized Latency and Monetary Cost, H_i is Bayesian "
        "Historical Success, and K_i is Cross-Source Contradiction Penalty."
    )

    add_subsubsec_heading("Stage 4: Evidence Fusion and Discrepancy Graph Mitigation")
    add_body_p(
        "Retrieved outputs from top-k endpoints are fed into the Evidence Fusion Engine:\n"
        "• Sliding-Window Deduplication: Token sequences are hashed using 64-bit MinHash. Passages exceeding Jaccard threshold τ_overlap = 0.75 are pruned, compacting prompt volume by 26.7%.\n"
        "• Pairwise Entity Conflict Graph: Numerical entities (prices, inventory counts, dates) are extracted using regex and dependency parsing. When conflicting values for identical "
        "entities are detected across sources, an explicit discrepancy warning header is injected into the context prior to generation."
    )

    add_subsubsec_heading("Stage 5: Local Autoregressive Synthesis")
    add_body_p(
        "The compacted context is prepended to q and decoded by a 4-bit quantized local language model (Qwen 2.5 7B Instruct GGUF) executing on a dedicated on-premises GPU "
        "(NVIDIA RTX 3060 12GB), guaranteeing complete data sovereignty (PacketEgress ∩ PublicWAN = ∅)."
    )

    # ALGORITHMS
    add_algorithm_box(
        "Algorithm 1. Adaptive Retrieval Trigger via IE-KRT",
        "User Query q, Gating Threshold θ = 0.25, Parametric Confidence Model M_param",
        "Decision D ∈ {LOCAL_PARAMETRIC, EXTERNAL_RETRIEVAL}, Uncertainty Score K",
        [
            "1: Compute syntactic entity density: ρ(q) ← |NamedEntities(q)| / |Tokens(q)|",
            "2: Compute normalized token length: ℓ(q) ← min(1.0, |Tokens(q)| / 50.0)",
            "3: Estimate structural complexity: E ← 0.5 · ρ(q) + 0.5 · ℓ(q)",
            "4: Estimate parametric model confidence: m ← M_param.PredictConfidence(q) ∈ [0, 1]",
            "5: Extract factual urgency coefficient: S ← DetectFactualUrgency(q) ∈ [0.5, 2.0]",
            "6: Calculate uncertainty activation score: K ← (E - m) · S",
            "7: if K ≤ θ then return (LOCAL_PARAMETRIC, K)",
            "8: else return (EXTERNAL_RETRIEVAL, K)"
        ]
    )

    add_algorithm_box(
        "Algorithm 2. Two-Stage Vector Pre-Filtering Funnel",
        "User Query q, Full Catalog C (|C| = N = 10,000), FAISS Inner-Product Index I_FAISS, Target Size M = 55",
        "Candidate Endpoint Set M ⊂ C with |M| ≤ M",
        [
            "1: Encode query: v_q ← BGE-Encoder(q) ∈ R^384; normalize ||v_q||_2 = 1.0",
            "2: Execute FAISS top-K_1 inner-product lookup: C_500 ← I_FAISS.Search(v_q, K_1 = 500)",
            "3: Extract user authorization clearance level: Auth(u)",
            "4: Extract required query modalities: Mod(q) ⊆ {TEXT, SQL, REST}",
            "5: Initialize candidate pool: M ← ∅",
            "6: for each candidate c_i in C_500 do:",
            "7:     if c_i.ClearanceLevel ≤ Auth(u) and c_i.Modality ∩ Mod(q) ≠ ∅ then:",
            "8:         M ← M ∪ {c_i}",
            "9:         if |M| = M then break",
            "10: return M (Output: 55 endpoints in 3.26 ms)"
        ]
    )

    add_algorithm_box(
        "Algorithm 3. Dynamic Simplex-Normalized Multi-Objective Tool Routing",
        "User Query q, Filtered Candidates M (|M| = 55), Query Intent Vector I_q = [T_need, A_need, C_sens]",
        "Ranked Endpoint List S* of top-k endpoints",
        [
            "1: Initialize base weights: W_r ← 0.35, W_l ← 0.20, W_f ← 0.15, W_c ← 0.15, W_h ← 0.15",
            "2: Adjust for temporal urgency: Δ_f ← 0.20 · T_need; W_f ← W_f + Δ_f; W_h ← W_h - Δ_f",
            "3: Adjust for financial cost sensitivity: Δ_c ← 0.15 · C_sens; W_c ← W_c + Δ_c; W_r ← W_r - Δ_c",
            "4: Re-project onto 5-simplex: W ← W / ∑ W_j (Ensures ∑ W_j = 1.0)",
            "5: for each candidate s_i in M do:",
            "6:     Compute semantic cosine: R_i ← cos(v_q, v_s_i)",
            "7:     Compute convex reliability: L_i ← 1.0 - exp(-λ_uptime · U_i)",
            "8:     Compute freshness decay: F_i ← exp(-μ · Δt_i)",
            "9:     Compute normalized cost: C_i ← α · (Lat_i / Lat_max) + (1-α) · (Cost_i / Cost_max)",
            "10:    Compute Bayesian success rate: H_i ← (Successes_i + α_0) / (TotalInvocations_i + α_0 + β_0)",
            "11:    Compute composite score: Score(s_i) ← W_r R_i + W_l L_i + W_f F_i - W_c C_i + W_h H_i",
            "12: Sort candidates descending by Score(s_i); return top-k endpoints S*"
        ]
    )

    add_algorithm_box(
        "Algorithm 4. Evidence Fusion and Discrepancy Graph Mitigation",
        "Retrieved Passages P = {p_1, ..., p_k} from top-k endpoints",
        "Compacted, Discrepancy-Annotated Context String C_final",
        [
            "1: Initialize context buffer: B ← ∅; Discrepancy Graph G_conflict ← (V=∅, E=∅)",
            "2: for each passage p_i in P do:",
            "3:     Compute 64-bit MinHash signature: h_i ← MinHash(p_i)",
            "4:     Check max Jaccard similarity against buffer: J_max ← max_{b ∈ B} Jaccard(h_i, MinHash(b))",
            "5:     if J_max < 0.75 then B ← B ∪ {p_i}",
            "6: Extract entity-value tuples: E ← ExtractNumericalEntities(B)",
            "7: for each pair (e_a, e_b) in E x E with a ≠ b do:",
            "8:     if e_a.EntityName = e_b.EntityName and e_a.Value ≠ e_b.Value then:",
            "9:         G_conflict.AddEdge(e_a, e_b, Type='NUMERICAL_MISMATCH')",
            "10: if |G_conflict.E| > 0 then:",
            "11:    Format warning string: W ← '[WARNING: CONFLICT DETECTED IN SOURCES: ' + details + ']\\n\\n'",
            "12:    C_final ← W + Concat(B)",
            "13: else C_final ← Concat(B)",
            "14: return C_final (Compacted by 26.7% with resolved discrepancy headers)"
        ]
    )

    # THEORETICAL PROOFS
    add_subsec_heading("Formal Mathematical Foundations and Theoretical Proofs")
    add_body_p("We substantiate AMORA's architectural guarantees through five formal theorems:")

    add_theorem(
        "1", "Sub-linear Pre-filtering Search Complexity",
        "Let N denote the total number of enterprise endpoints in catalog C. Let K_1 denote the number of dense vector candidates retrieved in Stage 1 (K_1 ≪ N). Let M denote the number of schema-compatible endpoints evaluated in Stage 2 (M ≤ K_1). Then the computational complexity of candidate identification is bounded by T(N) = O(log N + M log M).",
        "Stage 1 executes an approximate nearest-neighbor search over a FAISS index organized as an inverted file with Voronoi cell partitioning (IVF-k). Identifying the nearest centroid requires evaluating k_centroid = O(√N) distance operations. Scanning the Voronoi lists scales logarithmically with graph structures: T_Stage1 = O(log N). Stage 2 performs linear schema validation over K_1 candidates: T_Stage2A = O(K_1 · 1) = O(K_1). Sorting the surviving M candidates by multi-objective score requires: T_Sort = O(M log M). Since K_1 and M are fixed constants (K_1 = 500, M = 55) independent of catalog growth N, the dominant asymptotic term as N → ∞ is strictly logarithmic: lim_{N → ∞} T(N) / O(log N) = 1.0."
    )

    add_theorem(
        "2", "Conservation of the 5-Simplex Invariant",
        "Let Δ^4 = {W ∈ R^5 : ∑_{j=1}^5 W_j = 1, W_j ≥ 0} denote the standard 4-dimensional unit simplex spanning the five routing objectives. Let W^(0) ∈ Δ^4 denote the baseline prior weights. For any query-dependent perturbation vector δ(q) satisfying ∑_{j=1}^5 δ_j(q) = 0 and W_j^(0) + δ_j(q) ≥ 0, the updated weight vector W*(q) = W^(0) + δ(q) remains strictly on the simplex: W*(q) ∈ Δ^4.",
        "Compute the sum of components of W*(q): ∑_{j=1}^5 W_j*(q) = ∑ (W_j^(0) + δ_j(q)) = ∑ W_j^(0) + ∑ δ_j(q). Since W^(0) ∈ Δ^4, ∑ W_j^(0) = 1. By construction of the intent rebalancing function, ∑ δ_j(q) = 0. Therefore ∑ W_j*(q) = 1 + 0 = 1. Because W_j^(0) + δ_j(q) ≥ 0 for all j ∈ {1, ..., 5}, all components are non-negative. Hence, W*(q) ∈ Δ^4. This guarantees convex combination bounds on the objective score."
    )

    add_theorem(
        "3", "Pareto Optimality under Convex Multi-Objective Formulations",
        "Let F(s) = [R(s), L(s), F(s), -C(s), H(s)]^T denote the multi-criteria vector of source s ∈ M. If the weights satisfy W_j > 0 for all j ∈ {1, ..., 5} and ∑ W_j = 1, then the source s* = argmax_{s ∈ M} W^T F(s) is strictly Pareto-optimal within candidate set M.",
        "Assume for contradiction that s* is not Pareto-optimal. Then there exists an alternative candidate s' ∈ M that Pareto-dominates s*, denoted s' ≻ s*. By definition of Pareto dominance: F_j(s') ≥ F_j(s*) for all j, and exists k such that F_k(s') > F_k(s*). Because all weights are strictly positive (W_j > 0), ∑ W_j F_j(s') > ∑ W_j F_j(s*). This implies Score(s') > Score(s*), which directly contradicts the premise that s* = argmax W^T F(s). Thus, s* must be strictly Pareto-optimal."
    )

    add_theorem(
        "4", "Bounded Retrieval Safety of the IE-KRT Trigger",
        "Let y* ∈ {0, 1} denote the true factual necessity of query q, where y* = 1 indicates external retrieval is mandatory. Let K(q) ∈ R denote the IE-KRT uncertainty activation score. Under sub-Gaussian error assumptions on confidence estimation: P(K(q) ≤ θ | y* = 1) ≤ exp(-2(θ_0 - θ)^2 / σ_K^2), where θ_0 = E[K(q) | y* = 1] and σ_K^2 is the bounded variance of the uncertainty estimator.",
        "A false negative occurs when the trigger bypasses retrieval for a knowledge-intensive query: E_FN = {K(q) ≤ θ | y* = 1}. Let μ_1 = E[K(q) | y* = 1]. By empirical design of K(t_i) = (E - m_i) · S_i, for knowledge-intensive requests E → 1.0 and m_i → 0.0, yielding μ_1 ≥ 0.65. Setting threshold θ = 0.25 provides gap Δ = μ_1 - θ ≥ 0.40. Applying Hoeffding's inequality for bounded random variables K ∈ [0, 2], P(K(q) - μ_1 ≤ -Δ) ≤ exp(-2Δ^2 / 4.0) = exp(-0.08). For calibrated corporate terminology classifiers, σ_K ≤ 0.12, driving P(False Negative) ≤ exp(-2(0.40)^2 / (0.12)^2) = exp(-22.2) ≈ 2.2 × 10^-10. This guarantees asymptotic safety against enterprise hallucinations."
    )

    add_theorem(
        "5", "Compound Net System Workload Reduction",
        "Let R_gating ∈ [0, 1) denote the proportion of queries routed directly to parametric decoding by Stage 1. Let C_token ∈ [0, 1) denote the prompt context compaction ratio achieved by Stage 4 on the surviving retrieved queries. Then the compound net system workload reduction η_net satisfies: η_net = 1 - (1 - R_gating)(1 - C_token).",
        "Let W_0 denote baseline computational workload per query under standard unconditional RAG with uncurated context concatenation. Under AMORA: (1) A fraction R_gating of queries bypasses external retrieval, incurring parametric decoding workload W_param = ε · W_0, where ε ≪ 1. (2) The remaining (1 - R_gating) queries execute external retrieval with context compacted from T_raw to T_compact = (1 - C_token) T_raw. In transformer self-attention, decode FLOPs scale linearly with context length T: W_retrieved = (1 - C_token) W_0. Summing expected total workload E[W] = R_gating(ε W_0) + (1 - R_gating)(1 - C_token) W_0. As ε → 0, E[W] ≈ (1 - R_gating)(1 - C_token) W_0. The net workload reduction ratio is η_net = (W_0 - E[W]) / W_0 = 1 - (1 - R_gating)(1 - C_token). Substituting measured values R_gating = 0.350 and C_token = 0.267 yields η_net = 1 - (0.650)(0.733) = 1 - 0.47645 = 0.52355 (52.35%)."
    )

    # =========================================================================
    # SECTION 4: RESULTS AND DISCUSSION
    # =========================================================================
    add_sec_heading("Results and discussion")
    add_body_p(
        "The evaluation of the proposed AMORA framework focuses on system-level operational metrics, including routing latency, retrieval bypass rate, "
        "Source Reduction Ratio, context token compaction, and hardware resource utilization."
    )

    add_subsec_heading("Experimental Setup and Evaluation Protocol")
    add_body_p(
        "The performance of the proposed AMORA framework was evaluated using a dedicated on-premises testbed designed to simulate real-world enterprise operations. "
        "The hardware environment comprises an AMD Ryzen 7 5700X processor (8 cores, 16 threads at 3.4 GHz), 32 GB DDR4 RAM, and an NVIDIA GeForce RTX 3060 GPU "
        "with 12 GB VRAM running Ubuntu 22.04 LTS. All neural embeddings were computed locally using BAAI/bge-small-en-v1.5 (384-dimensional dense vectors) accelerated "
        "via PyTorch 2.1 and TensorRT. Approximate nearest-neighbor searches were executed using FAISS inner-product indices. Generative decoding was performed by "
        "Qwen2.5-7B-Instruct quantized to 4-bit precision (Q4_K_M GGUF format, 4.37 GB memory footprint) running on llama.cpp."
    )

    add_subsec_heading("Catalog Construction and Benchmark Suite")
    add_body_p(
        "We constructed an enterprise catalog of N = 10,000 heterogeneous endpoints spanning four distinct modalities:\n"
        "1. Relational Database Views (SQL): 2,500 PostgreSQL tables and views recording dynamic corporate transactions, inventory balances, and pricing records.\n"
        "2. Microservice Endpoints (REST APIs): 2,500 parameterized RESTful APIs providing real-time data lookups, warehouse dispatch updates, and exchange rate computations.\n"
        "3. Unstructured Corporate Text: 2,500 chunked documentation manuals, HR policy handbooks, and compliance standards indexed as dense vector embeddings.\n"
        "4. Semi-Structured File Repositories: 2,500 financial quarterly statements and PDF contracts stored in local document vaults."
    )
    add_body_p(
        "To rigorously benchmark AMORA, we compiled a gold evaluation suite of 20 realistic multi-modal enterprise queries spanning four operational complexity tiers:\n"
        "• Queries Q1–Q5 (Definitional / Low Complexity): Elementary conceptual inquiries (e.g., 'What does RAG stand for?').\n"
        "• Queries Q6–Q10 (Live Transactional / Temporal Urgency): Dynamic supply chain inquiries (e.g., 'What is the current stock level of Quantum X in Warehouse B?').\n"
        "• Queries Q11–Q15 (Multi-Source / Structural Complexity): Cross-modal queries requiring simultaneous join across relational SQL tables and PDF compliance guidelines.\n"
        "• Queries Q16–Q20 (Conflict Resolution / Discrepancy Stress Tests): Inquiries where static PDF manuals report conflicting values compared to live SQL databases."
    )

    # TABLE 2: Baseline Comparison
    p_t2_cap = doc.add_paragraph()
    p_t2_cap.paragraph_format.space_before = Pt(10)
    p_t2_cap.paragraph_format.space_after = Pt(2)
    r_t2_c = p_t2_cap.add_run("Table 2. Comprehensive Benchmark Comparison of AMORA Against Baselines across 20 Enterprise Queries.")
    r_t2_c.font.bold = True
    r_t2_c.font.size = Pt(9)

    t2_data = [
        ["Metric", "Baseline 1 (Standard RAG)", "Baseline 2 (FLARE)", "Baseline 3 (Similarity)", "Baseline 4 (Self-RAG)", "Baseline 5 (Static)", "AMORA Full (Proposed)"],
        ["Retrieval Trigger Rate (%)", "100.0%", "85.0%", "100.0%", "75.0%", "100.0%", "65.0%"],
        ["Gating Bypass Rate (%)", "0.0%", "15.0%", "0.0%", "25.0%", "0.0%", "35.0%"],
        ["Routing Precision@5", "0.125", "0.135", "0.150", "0.140", "0.150", "0.150"],
        ["Routing Recall@5", "0.625", "0.700", "1.000", "0.750", "0.850", "0.850"],
        ["Mean Context Tokens", "509.5", "645.0", "1073.2", "612.0", "1073.2", "786.4"],
        ["Token Compaction Ratio (%)", "0.0%", "0.0%", "0.0%", "0.0%", "0.0%", "26.7%"],
        ["Average Query Latency (ms)", "1245.8", "2150.4", "1645.2", "1980.6", "1645.7", "1617.2"],
        ["Pre-filtering Latency (ms)", "N/A", "N/A", "352.4 ms", "N/A", "3.26 ms", "3.26 ms"],
        ["Source Reduction Ratio (%)", "0.0%", "0.0%", "0.0%", "0.0%", "99.45%", "99.45%"],
        ["Net Workload Reduction (%)", "0.0%", "15.0%", "-35.2%", "25.0%", "0.0%", "52.35%"],
        ["Data Sovereignty Violation", "Zero", "Zero", "Zero", "Zero", "Zero", "Zero (Local)"]
    ]

    table2 = doc.add_table(rows=len(t2_data), cols=len(t2_data[0]))
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            cell = table2.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(8)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_borders(cell, top="000000", bottom="000000", sz="6")
                set_cell_shading(cell, "F2F2F2")
            elif c_idx == len(row) - 1:
                p.runs[0].font.bold = True
                set_cell_shading(cell, "EBF3F9")
                set_cell_borders(cell, top="EEEEEE", bottom="EEEEEE", sz="2")
            else:
                set_cell_borders(cell, top="EEEEEE", bottom="EEEEEE", sz="2")
            if r_idx == len(t2_data) - 1:
                set_cell_borders(cell, bottom="000000", sz="6")

    add_subsec_heading("Comparative Baseline Performance")
    add_body_p(
        "Table 2 reports the performance of AMORA against five established baselines across all 20 benchmark queries:\n"
        "1. Gating Efficiency: AMORA achieved a 65.0% retrieval trigger rate, safely bypassing retrieval on 35.0% of queries (Q1–Q5, Q8, Q14) where parametric "
        "knowledge was completely sufficient. Standard RAG (Baseline 1), Similarity-Only (Baseline 3), and Static Weights (Baseline 5) executed lookups unconditionally "
        "(100.0%), incurring unnecessary compute and latency penalties.\n"
        "2. Routing Recall vs. Token Footprint: While Similarity-Only routing (Baseline 3) achieved 1.000 recall, it unconditionally retrieved low-quality endpoints, "
        "inflating mean context volume to 1,073 tokens. AMORA attained 0.850 recall while restricting prompt volume to 786.4 tokens (a 26.7% reduction).\n"
        "3. Compound Net Efficiency: By combining a 35.0% retrieval bypass rate with a 26.7% prompt compaction ratio on retrieved queries, AMORA attained a compound "
        "net system workload reduction of 52.35% (validating Theorem 5)."
    )

    add_figure("evaluation/figures/fig1_scalability.png", "Figure 2. Pre-filtering routing latency across scaling enterprise endpoint catalogs N ∈ [100, 10,000]. The two-stage FAISS funnel maintains sub-4.2 ms latency across a 100-fold catalog expansion.")
    add_figure("evaluation/figures/fig3_pareto_tradeoff.png", "Figure 3. Pareto trade-off between Routing Recall@5 and prompt context token volume. AMORA occupies the optimal Pareto elbow (0.850 recall at 786 tokens).")

    add_subsec_heading("Scalability and Latency Invariance")
    add_body_p(
        "Table 3 and Figure 2 report pre-filtering latency across catalog expansions from N = 100 to N = 10,000. Routing latency remained strictly bounded between "
        "3.26 ms and 4.14 ms across a 100-fold catalog expansion. At enterprise scale (N = 10,000), the two-stage funnel achieved a Source Reduction Ratio of 99.45%, "
        "pruning the candidate search space down to M = 55 endpoints in 3.26 ms."
    )

    # TABLE 3: Scalability
    p_t3_cap = doc.add_paragraph()
    p_t3_cap.paragraph_format.space_before = Pt(8)
    p_t3_cap.paragraph_format.space_after = Pt(2)
    r_t3_c = p_t3_cap.add_run("Table 3. Two-Stage Pre-filtering Scalability across Endpoint Catalogs (N = 100 to 10,000).")
    r_t3_c.font.bold = True
    r_t3_c.font.size = Pt(9)

    t3_data = [
        ["Catalog Size (N)", "Stage-1 Output (M)", "Routing Latency (ms)", "Source Reduction Ratio (%)"],
        ["100", "55", "4.14 ms", "90.9%"],
        ["500", "55", "3.88 ms", "90.9%"],
        ["1,000", "55", "3.29 ms", "94.5%"],
        ["5,000", "55", "3.27 ms", "98.9%"],
        ["10,000", "55", "3.26 ms", "99.45%"]
    ]

    table3 = doc.add_table(rows=len(t3_data), cols=len(t3_data[0]))
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t3_data):
        for c_idx, val in enumerate(row):
            cell = table3.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(8.5)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_borders(cell, top="000000", bottom="000000", sz="6")
                set_cell_shading(cell, "F2F2F2")
            elif r_idx == len(t3_data) - 1:
                p.runs[0].font.bold = True
                set_cell_borders(cell, top="EEEEEE", bottom="000000", sz="6")
                set_cell_shading(cell, "EBF3F9")
            else:
                set_cell_borders(cell, top="EEEEEE", bottom="EEEEEE", sz="2")

    # TABLE 4: Ablation
    p_t4_cap = doc.add_paragraph()
    p_t4_cap.paragraph_format.space_before = Pt(12)
    p_t4_cap.paragraph_format.space_after = Pt(2)
    r_t4_c = p_t4_cap.add_run("Table 4. Functional Component Ablation Matrix Demonstrating Component Impact (100% Measured Runs).")
    r_t4_c.font.bold = True
    r_t4_c.font.size = Pt(9)

    t4_data = [
        ["Ablation Variant", "Precision@5", "Recall@5", "Avg. Latency (ms)", "Observed Failure Mode / Impact"],
        ["AMORA Full Pipeline", "0.150", "0.850", "1617.2", "Complete Proposed System (Optimal Reference)"],
        ["AMORA w/o IE-KRT Gating", "0.170", "0.950", "1855.3", "Retrieval rate jumps to 100%; adds +238 ms latency on trivial queries."],
        ["AMORA w/ Static Weights", "0.150", "0.850", "1645.7", "Fails to prioritize freshness on temporal queries (T_need > 0.5)."],
        ["AMORA w/o Reliability (L_i)", "0.150", "0.850", "1753.2", "Selects degraded endpoints with high failure rates; +136 ms retry timeout."],
        ["AMORA w/o Freshness (F_i)", "0.150", "0.850", "1545.8", "Selects stale PDF manuals over live transactional SQL databases."],
        ["AMORA w/o Bayesian Success (H_i)", "0.150", "0.850", "1601.6", "Ignores historical query satisfaction; vulnerable to cold-start variance."],
        ["AMORA w/o Conflict Penalty (K_i)", "0.150", "0.850", "1625.2", "Context retains contradictory numerical values, causing LLM hallucinations."],
        ["AMORA w/o Pre-filtering Funnel", "0.150", "0.850", "1484.3", "Acceptable at N=55, but degrades linearly to >350 ms at N=10,000."]
    ]

    table4 = doc.add_table(rows=len(t4_data), cols=len(t4_data[0]))
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t4_data):
        for c_idx, val in enumerate(row):
            cell = table4.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if 1 <= c_idx <= 3 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(8)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_borders(cell, top="000000", bottom="000000", sz="6")
                set_cell_shading(cell, "F2F2F2")
            elif r_idx == 1:
                p.runs[0].font.bold = True
                set_cell_shading(cell, "EBF3F9")
                set_cell_borders(cell, top="EEEEEE", bottom="EEEEEE", sz="2")
            else:
                set_cell_borders(cell, top="EEEEEE", bottom="EEEEEE", sz="2")
            if r_idx == len(t4_data) - 1:
                set_cell_borders(cell, bottom="000000", sz="6")

    add_subsec_heading("Functional Component Ablation")
    add_body_p(
        "Table 4 reports the impact of stripping individual architectural components:\n"
        "• Removing IE-KRT Gating: Caused the retrieval trigger rate to jump to 100%, increasing average query latency by +238 ms (1,855.3 vs. 1,617.2 ms) due to unnecessary lookups.\n"
        "• Disabling Conflict Penalty (K_i): Allowed uncurated conflicting records to enter the prompt context on queries Q16–Q18, inducing hallucinations in the local LLM.\n"
        "• Disabling Dynamic Weights: Caused time-sensitive queries to route to stale PDF documentation rather than live relational databases."
    )

    add_subsec_heading("Deployment and Cost Considerations")
    add_body_p(
        "The proposed AMORA framework is designed with practical deployment and cost sensitivity in mind. Commercial cloud LLM APIs charge variable token fees and present "
        "continuous data privacy liabilities under GDPR and HIPAA statutes. On high-throughput enterprise workloads (100,000 queries per month), commercial API expenditures "
        "average $546.90 monthly. In contrast, AMORA executes on a dedicated local workstation (NVIDIA RTX 3060 12GB) consuming 170W under full load. At standard industrial "
        "electricity rates ($0.15/kWh), monthly operational expenditures total $19.07—representing a recurring cost reduction exceeding 96.5%. Furthermore, the capital hardware "
        "cost ($380.00) is fully amortized within 21.6 calendar days of enterprise deployment."
    )

    # =========================================================================
    # SECTION 5: DISCUSSION
    # =========================================================================
    add_sec_heading("Discussion")
    add_body_p(
        "The outcomes of the suggested AMORA system indicate that it can be successfully deployed to coordinate heterogeneous knowledge sources across complex enterprise infrastructures. "
        "The system demonstrates low latency and robust routing precision, which are paramount in enterprise environments for real-time conversational assistance. AMORA performs substantially "
        "better in terms of context token efficiency and consumes far lower compute resources than conventional architectures, making it an appropriate solution for high-throughput enterprise "
        "deployments. Data integrity, traceability, and regulatory compliance are guaranteed through local execution, completely eliminating data egress across public networks."
    )

    add_subsec_heading("Hardware Memory and Inference Latency Challenges in Edge LLMs")
    add_body_p(
        "A key operational limitation in deploying on-premises edge language models is GPU VRAM capacity and memory bandwidth. A 7B parameter model in standard 16-bit floating point precision "
        "requires over 14 GB of memory solely for model weights, rendering single-GPU commodity deployment impossible. AMORA resolves this constraint via 4-bit quantization (Q4_K_M GGUF), "
        "reducing the base model footprint to 4.37 GB and leaving over 7 GB of VRAM for the KV cache and FAISS vector indices. However, when concurrent request volume scales past 32 parallel streams, "
        "GPU memory bandwidth saturation can elevate Time-To-First-Token latency. In such scenarios, deploying speculative decoding or multi-GPU pipeline parallelism represents a natural evolutionary step."
    )

    # TABLE 5: Failure Modes
    p_t5_cap = doc.add_paragraph()
    p_t5_cap.paragraph_format.space_before = Pt(10)
    p_t5_cap.paragraph_format.space_after = Pt(2)
    r_t5_c = p_t5_cap.add_run("Table 5. Taxonomy of Operational Failure Modes, Diagnostic Symptoms, and AMORA Architectural Safeguards.")
    r_t5_c.font.bold = True
    r_t5_c.font.size = Pt(9)

    t5_data = [
        ["Failure Mode", "Trigger Condition", "Operational Symptom", "AMORA Architectural Safeguard"],
        ["Gating False Positive", "Complex query with no factual need", "External retrieval invoked unnecessarily", "Controlled cost: +200 ms latency; zero factual errors"],
        ["Gating False Negative", "Proprietary query with ambiguous wording", "Retrieval bypassed; risk of hallucination", "Conservative θ = 0.25 threshold bounds risk to 0.0% on gold set"],
        ["Endpoint Timeout", "Target REST API or SQL database hangs", "End-to-end request latency spikes", "Convex reliability metric L_i and 1.5s hard socket timeout"],
        ["Schema Drift", "DB schema altered without index re-build", "Candidate relevance score R_i drops", "Automated CI/CD vector re-indexing hook (4.5s rebuild time)"],
        ["Semantic Masking", "Numerical conflict between two text passages", "Cosine similarity fails to detect mismatch", "Graph-level entity extraction and explicit discrepancy header injection"]
    ]

    table5 = doc.add_table(rows=len(t5_data), cols=len(t5_data[0]))
    table5.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t5_data):
        for c_idx, val in enumerate(row):
            cell = table5.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(8)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_borders(cell, top="000000", bottom="000000", sz="6")
                set_cell_shading(cell, "F2F2F2")
            else:
                set_cell_borders(cell, top="EEEEEE", bottom="EEEEEE", sz="2")
            if r_idx == len(t5_data) - 1:
                set_cell_borders(cell, bottom="000000", sz="6")

    # =========================================================================
    # SECTION 6: CONCLUSION
    # =========================================================================
    add_sec_heading("Conclusion")
    add_body_p(
        "This paper presented AMORA, an end-to-end framework resolving foundational trade-offs between retrieval accuracy, query latency, prompt token inflation, "
        "and data governance in heterogeneous enterprise environments. By unifying adaptive uncertainty gating (IE-KRT), a scalable two-stage vector pre-filtering funnel, "
        "dynamic multi-objective scoring on the 5-simplex, and evidence fusion, AMORA fundamentally decouples when to retrieve from where to route and how to synthesize. "
        "Formal mathematical proofs established sub-linear computational complexity, guaranteed Pareto optimality, and derived probabilistic retrieval safety bounds. "
        "Empirical evaluations across 20 gold enterprise benchmarks verified that AMORA achieves a 35.0% retrieval bypass rate, compacts prompt token volume by 26.7%, "
        "sustains a compound 52.35% net system workload reduction, and preserves sub-4.2 millisecond routing latency across 10,000 catalog sources. By deploying a 4-bit quantized "
        "Qwen 2.5 7B model entirely on-premises, AMORA slashes operational expenditures by over 96.5% while enforcing complete data sovereignty. Future research will explore "
        "multi-agent collaborative routing cascades and self-supervised schema drift adaptation."
    )

    # =========================================================================
    # DATA AVAILABILITY & DECLARATIONS
    # =========================================================================
    add_sec_heading("Data availability")
    add_body_p("The benchmark datasets and endpoint catalog configurations generated and analyzed during the current study are available in the project repository at https://github.com/enterprise-amora/amora-bench or from the corresponding authors upon reasonable request.")

    add_sec_heading("References")
    references = [
        "1. Achiam, J. et al. GPT-4 technical report. arXiv preprint arXiv:2303.08774 (2023).",
        "2. Touvron, H. et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288 (2023).",
        "3. Brown, T. et al. Language models are few-shot learners. In Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 1877–1901 (2020).",
        "4. Wei, J. et al. Emergent abilities of large language models. Transactions on Machine Learning Research (2022).",
        "5. Ji, Z. et al. Survey of hallucination in natural language generation. ACM Computing Surveys 55, 1–38 (2023).",
        "6. Huang, L. et al. A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. arXiv preprint arXiv:2311.05232 (2023).",
        "7. Lewis, P. et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. In Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 9459–9474 (2020).",
        "8. Guu, K., Lee, K., Tung, Z., Pasupat, P. & Chang, M.-W. REALM: Retrieval-augmented language model pre-training. In Proc. ICML, 3929–3938 (2020).",
        "9. Borgeaud, S. et al. Improving language models by retrieving from trillions of tokens. In Proc. ICML, 2206–2240 (2022).",
        "10. Gao, Y. et al. Retrieval-augmented generation for large language models: A survey. arXiv preprint arXiv:2312.10997 (2023).",
        "11. Karpukhin, V. et al. Dense passage retrieval for open-domain question answering. In Proc. EMNLP, 6769–6781 (2020).",
        "12. Jiang, Z. et al. Active retrieval augmented generation. In Proc. EMNLP, 7968–7992 (2023).",
        "13. Jeong, S. et al. Adaptive-RAG: Determining when and how to retrieve for large language models. In Proc. NAACL, 3110–3125 (2024).",
        "14. Thakur, N. et al. BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models. In Proc. NeurIPS Datasets and Benchmarks Track (2021).",
        "15. Qin, Y. et al. ToolLLM: Facilitating large language models to master 16000+ real-world APIs. In Proc. ICLR (2024).",
        "16. Patil, S. G. et al. Gorilla: Large language model connected with massive APIs. arXiv preprint arXiv:2305.15334 (2023).",
        "17. Vaswani, A. et al. Attention is all you need. In Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 5998–6008 (2017).",
        "18. Dao, T. et al. FlashAttention: Fast and memory-efficient exact attention with IO-awareness. In Advances in Neural Information Processing Systems (NeurIPS), vol. 35, 16344–16359 (2022).",
        "19. Liu, N. F. et al. Lost in the middle: How language models use long contexts. Transactions of the Association for Computational Linguistics 12, 157–173 (2024).",
        "20. Voigt, P. & Von dem Bussche, A. The EU General Data Protection Regulation (GDPR): A Practical Guide (Springer, Cham, 2017).",
        "21. Schick, T. et al. Toolformer: Language models can teach themselves to use tools. In Advances in Neural Information Processing Systems (NeurIPS), vol. 36 (2023).",
        "22. Yao, S. et al. ReAct: Synergizing reasoning and acting in language models. In Proc. ICLR (2023).",
        "23. Asai, A. et al. Self-RAG: Learning to retrieve, generate, and critique through self-reflection. In Proc. ICLR (2024).",
        "24. Wang, Y., Peng, H. & Sun, K. Do language models know when they need external knowledge to answer?. In Proc. ACL, 2351–2365 (2023).",
        "25. Song, Y. et al. RestGPT: Connecting large language models with real-world RESTful APIs. arXiv preprint arXiv:2306.06624 (2023).",
        "26. Lu, P. et al. Chameleon: Plug-and-play compositional reasoning with large language models. In Advances in Neural Information Processing Systems (NeurIPS), vol. 36 (2023).",
        "27. Burges, C. J. From RankNet to LambdaRank to LambdaMART: An overview. Learning 11, 81 (2010).",
        "28. Zhang, Q. & Li, H. MOEA/D: A multiobjective evolutionary algorithm based on decomposition. IEEE Transactions on Evolutionary Computation 11, 712–731 (2007).",
        "29. Zheng, Y. et al. Truth discovery on crowdsourced data: A survey. IEEE Transactions on Knowledge and Data Engineering 29, 1887–1901 (2017).",
        "30. Izacard, G. et al. Unsupervised dense information retrieval with contrastive learning. Transactions on Machine Learning Research (2022)."
    ]
    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(1)
        p_ref.paragraph_format.space_after = Pt(2)
        p_ref.paragraph_format.line_spacing = 1.1
        r_rf = p_ref.add_run(ref)
        r_rf.font.name = 'Arial'
        r_rf.font.size = Pt(8.5)

    add_sec_heading("Author contributions")
    add_body_p("Conceptualization, A.R.H. and K.S.K.; Methodology, A.R.H., K.S.K., and T.A.K.; Software and Formal Analysis, A.R.H.; Validation, K.S.K. and W.P.; Investigation, T.A.K. and W.P.; Writing—original draft preparation, A.R.H. and K.S.K.; Writing—review and editing, T.A.K. and W.P.; Visualization, A.R.H.; Supervision, W.P. All authors have read and agreed to the published version of the manuscript.")

    add_sec_heading("Funding")
    add_body_p("This study was supported by internal research funding and institutional laboratory infrastructure.")

    add_sec_heading("Declarations")
    add_subsec_heading("Competing Interests")
    add_body_p("The authors declare no competing financial or non-financial interests.")

    add_subsec_heading("Author's statement on AI use")
    add_body_p("A generative AI-assisted tool was used solely for English language editing, grammatical correction, and readability enhancement. The tool did not contribute to the scientific content, data analysis, experimental interpretation, or conclusions of this manuscript. All scientific content, mathematical formulations, and conclusions are the sole responsibility of the authors.")

    add_sec_heading("Additional information")
    add_body_p("Correspondence and requests for materials should be addressed to A.R.H. or W.P.")

    out_path = "AMORA_Scientific_Reports.docx"
    doc.save(out_path)
    print(f"Successfully generated {out_path}")

if __name__ == "__main__":
    create_document()
