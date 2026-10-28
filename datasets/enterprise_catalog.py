# datasets/enterprise_catalog.py
"""
AMORA Enterprise Knowledge Source Catalog (52 Production Sources)
Component Tag: [A. Heterogeneous Source Catalog]
"""

ENTERPRISE_SOURCES = [
    # ── 1. Sales, CRM & Revenue ─────────────────────────────────────────────
    {
        "source_id": "src_crm_salesforce",
        "name": "Global Salesforce CRM & Opportunities DB",
        "source_type": "REST API",
        "domain": "sales_crm",
        "description": "Enterprise CRM holding real-time customer accounts, sales opportunities, B2B deal pipelines, lead stages, and account executive assignments.",
        "endpoint_or_schema": "https://api.salesforce.enterprise.internal/v58/sobjects",
        "tool_type": "api_tool",
        "reliability": 0.97, "cost": 0.08, "latency": 0.12, "availability": 0.99
    },
    {
        "source_id": "src_sales_pos_na",
        "name": "North America Retail Point-of-Sale Transactions DB",
        "source_type": "SQL Database",
        "domain": "sales_pos",
        "description": "Live relational store transactional database recording in-store purchases, daily store revenue, register receipts, SKU sales, and regional tax for North American branches.",
        "endpoint_or_schema": "sqlite:///./data/pos_na.db",
        "tool_type": "sql_tool",
        "reliability": 0.99, "cost": 0.04, "latency": 0.08, "availability": 1.00
    },
    {
        "source_id": "src_sales_pos_emea",
        "name": "EMEA Retail Stores Transaction Ledger",
        "source_type": "SQL Database",
        "domain": "sales_pos",
        "description": "Relational POS records for European, Middle Eastern and African retail stores, capturing VAT calculations, multi-currency conversions, and returns.",
        "endpoint_or_schema": "sqlite:///./data/pos_emea.db",
        "tool_type": "sql_tool",
        "reliability": 0.98, "cost": 0.04, "latency": 0.09, "availability": 0.99
    },
    {
        "source_id": "src_ecommerce_checkout",
        "name": "E-Commerce Online Orders & Checkout Store",
        "source_type": "SQL Database",
        "domain": "ecommerce",
        "description": "High-throughput transactional database recording digital storefront carts, payment gateway confirmations, customer shipment addresses, and tracking numbers.",
        "endpoint_or_schema": "sqlite:///./data/ecommerce_orders.db",
        "tool_type": "sql_tool",
        "reliability": 0.99, "cost": 0.05, "latency": 0.06, "availability": 1.00
    },
    {
        "source_id": "src_pricing_discount_api",
        "name": "Global Pricing & Dynamic Discount Matrix API",
        "source_type": "REST API",
        "domain": "pricing",
        "description": "Microservice calculating live volume discounts, regional currency price books, promotional coupon codes, and enterprise negotiated contract rates.",
        "endpoint_or_schema": "https://api.pricing.enterprise.internal/v2/discounts",
        "tool_type": "api_tool",
        "reliability": 0.95, "cost": 0.06, "latency": 0.07, "availability": 0.99
    },
    {
        "source_id": "src_sales_commission_db",
        "name": "Sales Rep Quota & Commission Tracking DB",
        "source_type": "SQL Database",
        "domain": "sales_performance",
        "description": "Internal sales performance database tracking quota attainments, quarterly bonus tiers, commission payouts, and territory coverage metrics.",
        "endpoint_or_schema": "sqlite:///./data/commissions.db",
        "tool_type": "sql_tool",
        "reliability": 0.96, "cost": 0.03, "latency": 0.10, "availability": 0.98
    },

    # ── 2. Inventory, Logistics & Supply Chain ──────────────────────────────
    {
        "source_id": "src_warehouse_central",
        "name": "Central Distribution Warehouse Inventory DB",
        "source_type": "SQL Database",
        "domain": "inventory",
        "description": "Main logistics database maintaining bin locations, pallet identifiers, real-time safety stock counts, backorders, and dock arrival schedules.",
        "endpoint_or_schema": "sqlite:///./data/warehouse_central.db",
        "tool_type": "sql_tool",
        "reliability": 0.98, "cost": 0.05, "latency": 0.09, "availability": 0.99
    },
    {
        "source_id": "src_warehouse_west",
        "name": "West Coast Fulfillment Center Inventory",
        "source_type": "SQL Database",
        "domain": "inventory",
        "description": "Regional warehouse inventory database tracking Pacific regional stock allocations, cross-dock transit, and local carrier handoffs.",
        "endpoint_or_schema": "sqlite:///./data/warehouse_west.db",
        "tool_type": "sql_tool",
        "reliability": 0.97, "cost": 0.04, "latency": 0.08, "availability": 0.99
    },
    {
        "source_id": "src_logistics_freight_api",
        "name": "Global Freight & Intermodal Shipment Tracking API",
        "source_type": "REST API",
        "domain": "logistics",
        "description": "REST endpoint connecting to maritime container shipping carriers, air cargo manifests, bill of lading statuses, and customs port clearance timestamps.",
        "endpoint_or_schema": "https://api.freight-tracking.internal/v3/manifests",
        "tool_type": "api_tool",
        "reliability": 0.94, "cost": 0.12, "latency": 0.18, "availability": 0.98
    },
    {
        "source_id": "src_supplier_vendor_portal",
        "name": "Tier-1 Component Supplier Quality & Scorecard DB",
        "source_type": "SQL Database",
        "domain": "supply_chain",
        "description": "Database of raw material semiconductor suppliers, on-time delivery rates, component defect ratios, and procurement purchase orders.",
        "endpoint_or_schema": "sqlite:///./data/suppliers.db",
        "tool_type": "sql_tool",
        "reliability": 0.96, "cost": 0.06, "latency": 0.11, "availability": 0.98
    },
    {
        "source_id": "src_customs_tariff_docs",
        "name": "International Trade Customs & Harmonized Tariff Schedules",
        "source_type": "PDF Document",
        "domain": "customs_compliance",
        "description": "Regulatory documentation covering international HS code classifications, export control classifications (ECCN), import duties, and free-trade agreements.",
        "endpoint_or_schema": "./docs/customs_tariff_schedules_2026.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.99, "cost": 0.02, "latency": 0.10, "availability": 1.00
    },
    {
        "source_id": "src_fleet_telematics_api",
        "name": "Fleet GPS Telematics & Route Optimization Feed",
        "source_type": "REST API",
        "domain": "logistics",
        "description": "Real-time vehicle telemetry stream reporting truck route latencies, estimated delivery windows, fuel efficiency metrics, and driver logs.",
        "endpoint_or_schema": "https://telematics.fleet.internal/v1/vehicles",
        "tool_type": "api_tool",
        "reliability": 0.93, "cost": 0.07, "latency": 0.14, "availability": 0.97
    },

    # ── 3. Legal, Governance & Compliance ────────────────────────────────────
    {
        "source_id": "src_legal_master_bylaws",
        "name": "Corporate Bylaws & Master Governance Charter",
        "source_type": "PDF Document",
        "domain": "legal_governance",
        "description": "Authoritative corporate governance documentation outlining board voting rights, officer fiduciary duties, corporate resolutions, and delegation of authority.",
        "endpoint_or_schema": "./docs/corporate_bylaws_2026.pdf",
        "tool_type": "doc_tool",
        "reliability": 1.00, "cost": 0.01, "latency": 0.08, "availability": 1.00
    },
    {
        "source_id": "src_compliance_gdpr_ccpa",
        "name": "Global Privacy & Data Protection Compliance Manual",
        "source_type": "PDF Document",
        "domain": "legal_compliance",
        "description": "Legal compliance manual governing GDPR, CCPA, CPRA, data subject access requests (DSAR), cross-border data transfer, and privacy breach protocol.",
        "endpoint_or_schema": "./docs/privacy_gdpr_ccpa_manual.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.99, "cost": 0.02, "latency": 0.10, "availability": 1.00
    },
    {
        "source_id": "src_compliance_soc2",
        "name": "SOC 2 Type II Security & Audit Control Specification",
        "source_type": "PDF Document",
        "domain": "security_compliance",
        "description": "Detailed auditor report and system descriptions defining Trust Services Criteria for security, availability, processing integrity, and confidentiality.",
        "endpoint_or_schema": "./docs/soc2_type2_controls_report.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.99, "cost": 0.02, "latency": 0.09, "availability": 1.00
    },
    {
        "source_id": "src_legal_msa_contracts",
        "name": "Enterprise Master Services Agreement (MSA) Repository",
        "source_type": "PDF Document",
        "domain": "legal_contracts",
        "description": "Standard negotiated contract terms, indemnification clauses, limitation of liability thresholds, SLA guarantees, and termination covenants.",
        "endpoint_or_schema": "./docs/master_services_agreements.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.98, "cost": 0.03, "latency": 0.12, "availability": 1.00
    },
    {
        "source_id": "src_legal_ip_patents",
        "name": "Intellectual Property & Granted Patents Vault",
        "source_type": "PDF Document",
        "domain": "intellectual_property",
        "description": "Registered patents, trade secret disclosures, trademark filings, and licensing agreements for proprietary hardware and neural algorithms.",
        "endpoint_or_schema": "./docs/ip_patent_filings.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.97, "cost": 0.02, "latency": 0.11, "availability": 1.00
    },

    # ── 4. Finance, Accounting & Tax ─────────────────────────────────────────
    {
        "source_id": "src_sap_general_ledger",
        "name": "SAP ERP General Ledger & Financial Chart of Accounts",
        "source_type": "SQL Database",
        "domain": "finance_accounting",
        "description": "Core financial system storing journal vouchers, cost center allocations, debits, credits, balance sheets, and profit and loss line items.",
        "endpoint_or_schema": "sqlite:///./data/sap_general_ledger.db",
        "tool_type": "sql_tool",
        "reliability": 0.99, "cost": 0.06, "latency": 0.09, "availability": 1.00
    },
    {
        "source_id": "src_ap_invoicing_api",
        "name": "Accounts Payable & Vendor Invoicing Automation API",
        "source_type": "REST API",
        "domain": "finance_ap",
        "description": "REST endpoint for three-way invoice matching between purchase orders, warehouse receiving receipts, and vendor invoices awaiting disbursement.",
        "endpoint_or_schema": "https://api.invoicing.finance.internal/v1/invoices",
        "tool_type": "api_tool",
        "reliability": 0.96, "cost": 0.05, "latency": 0.11, "availability": 0.98
    },
    {
        "source_id": "src_tax_statutory_db",
        "name": "Corporate Tax & Multi-Jurisdiction Statutory Filing DB",
        "source_type": "SQL Database",
        "domain": "finance_tax",
        "description": "Tax repository documenting federal, state, and international corporate income tax provisions, R&D tax credit claims, and nexus assessments.",
        "endpoint_or_schema": "sqlite:///./data/corporate_tax.db",
        "tool_type": "sql_tool",
        "reliability": 0.98, "cost": 0.04, "latency": 0.10, "availability": 0.99
    },
    {
        "source_id": "src_forex_treasury_api",
        "name": "Treasury FX Rates & Currency Hedging Feed",
        "source_type": "REST API",
        "domain": "treasury_forex",
        "description": "Real-time financial market feed providing live central bank reference rates, forward swap curves, currency exposures, and liquidity pool balances.",
        "endpoint_or_schema": "https://api.treasury.finance.internal/v2/fx-rates",
        "tool_type": "api_tool",
        "reliability": 0.97, "cost": 0.08, "latency": 0.07, "availability": 0.99
    },
    {
        "source_id": "src_expense_concur_db",
        "name": "Employee Expense Reports & Concur Audit Database",
        "source_type": "SQL Database",
        "domain": "finance_expenses",
        "description": "Corporate credit card reconciliations, travel expense line items, per diem meal allowances, hotel receipt audits, and manager approvals.",
        "endpoint_or_schema": "sqlite:///./data/expense_reports.db",
        "tool_type": "sql_tool",
        "reliability": 0.95, "cost": 0.03, "latency": 0.08, "availability": 0.98
    },
    {
        "source_id": "src_sec_10k_reports",
        "name": "SEC Form 10-K & 10-Q Financial Disclosures",
        "source_type": "PDF Document",
        "domain": "investor_relations",
        "description": "Publicly filed annual and quarterly audited financial statements, MD&A disclosures, risk factor declarations, and executive compensation disclosures.",
        "endpoint_or_schema": "./docs/sec_form_10k_2025_2026.pdf",
        "tool_type": "doc_tool",
        "reliability": 1.00, "cost": 0.01, "latency": 0.10, "availability": 1.00
    },

    # ── 5. Human Resources, Payroll & Workforce ──────────────────────────────
    {
        "source_id": "src_workday_hris_api",
        "name": "Workday Global HRIS & Organizational Directory API",
        "source_type": "REST API",
        "domain": "hr_workforce",
        "description": "Authoritative employee system of record containing employee ID numbers, reporting structures, job levels, department codes, and work locations.",
        "endpoint_or_schema": "https://api.workday.internal/v3/workers",
        "tool_type": "api_tool",
        "reliability": 0.98, "cost": 0.06, "latency": 0.13, "availability": 0.99
    },
    {
        "source_id": "src_payroll_benefits_db",
        "name": "Global Payroll & Employee Benefits Database",
        "source_type": "SQL Database",
        "domain": "hr_payroll",
        "description": "Confidential database managing monthly base salary disbursements, 401(k) employer matching schedules, health insurance tier selections, and withholdings.",
        "endpoint_or_schema": "sqlite:///./data/payroll_benefits.db",
        "tool_type": "sql_tool",
        "reliability": 0.99, "cost": 0.04, "latency": 0.09, "availability": 0.99
    },
    {
        "source_id": "src_hr_employee_handbook",
        "name": "Employee Conduct, Leave & PTO Policy Handbook",
        "source_type": "PDF Document",
        "domain": "hr_policy",
        "description": "Comprehensive workforce policy manual detailing paid time off (PTO) accruals, parental leave duration, remote work stipend eligibility, and grievance procedures.",
        "endpoint_or_schema": "./docs/employee_handbook_2026.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.99, "cost": 0.01, "latency": 0.07, "availability": 1.00
    },
    {
        "source_id": "src_recruiting_greenhouse_api",
        "name": "Greenhouse Talent Acquisition & Job Openings API",
        "source_type": "REST API",
        "domain": "hr_recruiting",
        "description": "Applicant tracking system holding open engineering positions, candidate interview feedback, recruiter notes, and offer letter generation stages.",
        "endpoint_or_schema": "https://api.greenhouse.internal/v1/jobs",
        "tool_type": "api_tool",
        "reliability": 0.94, "cost": 0.05, "latency": 0.12, "availability": 0.97
    },
    {
        "source_id": "src_okr_performance_vector",
        "name": "Company OKR & Performance Review Semantic Index",
        "source_type": "Vector DB",
        "domain": "hr_performance",
        "description": "Vector index storing quarterly objectives and key results (OKRs), annual peer feedback evaluations, and promotion committee recommendations.",
        "endpoint_or_schema": "faiss://okr_performance_vector_index",
        "tool_type": "vector_tool",
        "reliability": 0.92, "cost": 0.07, "latency": 0.15, "availability": 0.98
    },

    # ── 6. Customer Support, Tickets & Knowledge Base ────────────────────────
    {
        "source_id": "src_zendesk_ticket_archive",
        "name": "Zendesk Customer Support Escalation Database",
        "source_type": "SQL Database",
        "domain": "customer_support",
        "description": "Historical support ticket log containing customer dispute records, resolution times, RMA hardware return IDs, and tier-3 engineering escalations.",
        "endpoint_or_schema": "sqlite:///./data/zendesk_tickets.db",
        "tool_type": "sql_tool",
        "reliability": 0.96, "cost": 0.04, "latency": 0.09, "availability": 0.99
    },
    {
        "source_id": "src_hardware_diagnostic_vector",
        "name": "Product Hardware Diagnostic & Error Codes Vector Index",
        "source_type": "Vector DB",
        "domain": "customer_support",
        "description": "Dense embedding database of hardware motherboard error codes, blinking LED diagnostics, thermal throttling troubleshooting, and power supply repair steps.",
        "endpoint_or_schema": "faiss://hardware_diagnostic_kb",
        "tool_type": "vector_tool",
        "reliability": 0.95, "cost": 0.06, "latency": 0.14, "availability": 0.98
    },
    {
        "source_id": "src_call_center_transcripts_vector",
        "name": "Call Center Audio Transcripts & Voice Sentiment Index",
        "source_type": "Vector DB",
        "domain": "customer_insights",
        "description": "Semantic vector search across transcribed customer service phone calls, recurring customer complaints, feature requests, and CSAT ratings.",
        "endpoint_or_schema": "faiss://call_transcripts_index",
        "tool_type": "vector_tool",
        "reliability": 0.91, "cost": 0.09, "latency": 0.16, "availability": 0.97
    },
    {
        "source_id": "src_vip_sla_agreements",
        "name": "VIP Enterprise Customer SLA Contracts & Dedicated Teams",
        "source_type": "PDF Document",
        "domain": "customer_contracts",
        "description": "Signed premium support agreements outlining 1-hour response guarantees, designated technical account manager (TAM) rosters, and liquidated damages.",
        "endpoint_or_schema": "./docs/vip_enterprise_sla_contracts.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.98, "cost": 0.02, "latency": 0.09, "availability": 1.00
    },

    # ── 7. IT Infrastructure, Cloud, DevOps & Security ───────────────────────
    {
        "source_id": "src_cloud_cost_aws_api",
        "name": "AWS & Multi-Cloud Infrastructure Resource Catalog API",
        "source_type": "REST API",
        "domain": "it_infrastructure",
        "description": "Cloud management API providing live EC2/EKS instance counts, S3 bucket storage utilization, monthly cloud spend burn rates, and idle resource alerts.",
        "endpoint_or_schema": "https://api.cloud-ops.internal/v1/aws-inventory",
        "tool_type": "api_tool",
        "reliability": 0.97, "cost": 0.07, "latency": 0.11, "availability": 0.99
    },
    {
        "source_id": "src_k8s_cluster_metrics",
        "name": "Kubernetes Production Clusters Telemetry & Health API",
        "source_type": "REST API",
        "domain": "devops_telemetry",
        "description": "Prometheus telemetry aggregator tracking node CPU pressure, pod restart loops, ingress HTTP p99 latencies, and service mesh traffic spikes.",
        "endpoint_or_schema": "https://prometheus.k8s.internal/api/v1/query",
        "tool_type": "api_tool",
        "reliability": 0.98, "cost": 0.05, "latency": 0.08, "availability": 0.99
    },
    {
        "source_id": "src_iam_active_directory",
        "name": "Okta & Active Directory Enterprise IAM User Store",
        "source_type": "SQL Database",
        "domain": "cybersecurity",
        "description": "Centralized security directory maintaining employee SSO credentials, RBAC security group memberships, MFA device bindings, and access token audit logs.",
        "endpoint_or_schema": "sqlite:///./data/identity_access.db",
        "tool_type": "sql_tool",
        "reliability": 0.99, "cost": 0.04, "latency": 0.07, "availability": 1.00
    },
    {
        "source_id": "src_cve_vulnerability_db",
        "name": "National Vulnerability Database (NVD) & Internal Patch Matrix",
        "source_type": "SQL Database",
        "domain": "cybersecurity",
        "description": "Security vulnerability database correlating CVE identifiers, CVSS severity scores, zero-day threat bulletins, and production host patch statuses.",
        "endpoint_or_schema": "sqlite:///./data/vulnerabilities.db",
        "tool_type": "sql_tool",
        "reliability": 0.97, "cost": 0.04, "latency": 0.10, "availability": 0.99
    },
    {
        "source_id": "src_siem_threat_vector",
        "name": "Splunk SIEM Firewall & Threat Intelligence Vector Index",
        "source_type": "Vector DB",
        "domain": "cybersecurity",
        "description": "High-density vector embeddings of anomaly detection logs, suspicious lateral network movements, DDoS intrusion signatures, and firewall drop patterns.",
        "endpoint_or_schema": "faiss://siem_threat_index",
        "tool_type": "vector_tool",
        "reliability": 0.94, "cost": 0.10, "latency": 0.17, "availability": 0.98
    },
    {
        "source_id": "src_it_incident_postmortems",
        "name": "IT Major Incident Post-Mortems & RCA Archive",
        "source_type": "PDF Document",
        "domain": "it_operations",
        "description": "Detailed post-incident reviews documenting root cause analyses, recovery timelines, action items, and prevention measures for P1 system outages.",
        "endpoint_or_schema": "./docs/incident_postmortems_archive.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.98, "cost": 0.02, "latency": 0.08, "availability": 1.00
    },

    # ── 8. Engineering, R&D & Product Architecture ───────────────────────────
    {
        "source_id": "src_spec_quantum_laptop",
        "name": "Quantum X Laptop Engineering Datasheets & Schematics",
        "source_type": "PDF Document",
        "domain": "hardware_engineering",
        "description": "Official hardware engineering specifications covering Quantum X laptop processor TDP, dual heat-pipe thermal dissipation, DDR5 RAM configurations, and battery cycles.",
        "endpoint_or_schema": "./docs/quantum_x_laptop_schematics.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.99, "cost": 0.02, "latency": 0.09, "availability": 1.00
    },
    {
        "source_id": "src_spec_aura_headphones",
        "name": "Aura Pro Wireless Headphones Acoustic & ANC Architecture",
        "source_type": "PDF Document",
        "domain": "hardware_engineering",
        "description": "Acoustics research paper detailing 40mm beryllium drivers, active noise cancellation feedforward microphone tuning, latency codecs (LDAC, AAC), and Bluetooth 5.4 specs.",
        "endpoint_or_schema": "./docs/aura_pro_acoustic_specs.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.98, "cost": 0.02, "latency": 0.09, "availability": 1.00
    },
    {
        "source_id": "src_firmware_release_api",
        "name": "Device Firmware OTA Release & Checksum API",
        "source_type": "REST API",
        "domain": "firmware_iot",
        "description": "Over-the-air firmware binary registry providing cryptographic SHA-256 signatures, delta update package links, minimum required bootloader versions, and changelogs.",
        "endpoint_or_schema": "https://ota.devices.internal/v2/firmware",
        "tool_type": "api_tool",
        "reliability": 0.99, "cost": 0.05, "latency": 0.08, "availability": 1.00
    },
    {
        "source_id": "src_jira_roadmap_api",
        "name": "Jira Enterprise Product Roadmap & Sprint Backlog",
        "source_type": "REST API",
        "domain": "product_management",
        "description": "Product development tracking system containing epic roadmaps, user story acceptance criteria, sprint velocity metrics, and scheduled release versions.",
        "endpoint_or_schema": "https://jira.enterprise.internal/rest/api/3/search",
        "tool_type": "api_tool",
        "reliability": 0.95, "cost": 0.06, "latency": 0.12, "availability": 0.98
    },
    {
        "source_id": "src_rd_patent_vector_kb",
        "name": "Neural RAG & Multi-Objective Optimization Research Papers",
        "source_type": "Vector DB",
        "domain": "research_ai",
        "description": "Dense vector embedding index of peer-reviewed papers on Dempster-Shafer evidential fusion, Pareto multi-objective search, and adaptive retrieval triggers in LLM architectures.",
        "endpoint_or_schema": "faiss://ai_research_vector_store",
        "tool_type": "vector_tool",
        "reliability": 0.96, "cost": 0.08, "latency": 0.15, "availability": 0.99
    },
    {
        "source_id": "src_msds_safety_docs",
        "name": "Material Safety Data Sheets (MSDS) & Battery Handling Manual",
        "source_type": "PDF Document",
        "domain": "regulatory_safety",
        "description": "Mandatory chemical and lithium-ion battery safety documentation detailing UN 38.3 transport testing, thermal runaway mitigation, and proper disposal handling.",
        "endpoint_or_schema": "./docs/battery_msds_safety_guidelines.pdf",
        "tool_type": "doc_tool",
        "reliability": 1.00, "cost": 0.01, "latency": 0.07, "availability": 1.00
    },

    # ── 9. Market Intelligence & Competitor Analytics ────────────────────────
    {
        "source_id": "src_market_competitor_crawler",
        "name": "Consumer Electronics Competitor Pricing Crawler",
        "source_type": "Web Source",
        "domain": "market_intelligence",
        "description": "Automated web crawler monitoring competitor retail websites for daily promotional discounts, laptop bundle prices, stockout alerts, and customer reviews.",
        "endpoint_or_schema": "https://web-crawler.market-intel.internal/scrapes",
        "tool_type": "web_tool",
        "reliability": 0.91, "cost": 0.11, "latency": 0.22, "availability": 0.95
    },
    {
        "source_id": "src_industry_trends_report",
        "name": "IDC & Gartner Global Hardware Market Trends 2026",
        "source_type": "PDF Document",
        "domain": "market_research",
        "description": "Market research report detailing global consumer electronics shipment volumes, average selling price (ASP) trajectories, and AI-enabled PC adoption rates.",
        "endpoint_or_schema": "./docs/idc_gartner_market_analysis_2026.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.96, "cost": 0.03, "latency": 0.10, "availability": 0.99
    },
    {
        "source_id": "src_semiconductor_commodity_api",
        "name": "Bloomberg Semiconductor & Memory Commodity Price Index",
        "source_type": "REST API",
        "domain": "market_commodity",
        "description": "Financial market feed tracking spot prices for DRAM, NAND flash wafers, copper, and rare-earth magnets impacting manufacturing bill-of-materials costs.",
        "endpoint_or_schema": "https://api.commodities-feed.internal/v1/semiconductors",
        "tool_type": "api_tool",
        "reliability": 0.97, "cost": 0.09, "latency": 0.10, "availability": 0.99
    },

    # ── 10. Quality Assurance & Factory Automation ───────────────────────────
    {
        "source_id": "src_factory_qa_telemetry_db",
        "name": "Factory Assembly Line Quality Assurance & Yield DB",
        "source_type": "SQL Database",
        "domain": "manufacturing_qa",
        "description": "Robotic manufacturing telemetry recording automated optical inspection (AOI) defect images, solder paste inspection yields, and final burn-in test pass rates.",
        "endpoint_or_schema": "sqlite:///./data/factory_qa_yield.db",
        "tool_type": "sql_tool",
        "reliability": 0.98, "cost": 0.05, "latency": 0.09, "availability": 0.99
    },
    {
        "source_id": "src_iso9001_quality_manual",
        "name": "ISO 9001 Quality Management System (QMS) Procedures",
        "source_type": "PDF Document",
        "domain": "quality_standards",
        "description": "Standard operating procedures for quality audit checklists, non-conformance reporting (NCR), corrective and preventive actions (CAPA), and management reviews.",
        "endpoint_or_schema": "./docs/iso9001_qms_standard_operating_procedures.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.99, "cost": 0.02, "latency": 0.08, "availability": 1.00
    },
    {
        "source_id": "src_esg_sustainability_index",
        "name": "Environmental, Social & Governance (ESG) Sustainability Metrics",
        "source_type": "PDF Document",
        "domain": "esg_compliance",
        "description": "Corporate sustainability disclosures covering greenhouse gas Scope 1-3 emissions, circular economy recycling rates, conflict mineral tracing, and renewable energy.",
        "endpoint_or_schema": "./docs/esg_sustainability_report_2026.pdf",
        "tool_type": "doc_tool",
        "reliability": 0.98, "cost": 0.02, "latency": 0.09, "availability": 1.00
    }
]
