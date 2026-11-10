"""
LegalLens - Interactive & Visual Report Generator
Generates standalone, beautifully formatted, beginner-friendly HTML and Word-compatible
reports with high-contrast typography, interactive risk filters, plain-English callouts,
and 1-click print-to-PDF styling with zero faded text.
"""

# [Summary]: Generates standalone interactive HTML reports (print-to-PDF) & formatted Word docs.

import json
from typing import Any
from modules.auditor import DocumentAuditReport
from modules.jargon_buster import render_jargon_buster_html, render_jargon_buster_word_html, find_matching_jargon


def generate_interactive_html_report(report: DocumentAuditReport, filename: str = "Contract") -> str:
    """
    Generates a standalone, executive-grade HTML legal safety report that opens in any browser
    with crystal-clear high-contrast typography, colored badges, plain-English callouts,
    and laser-sharp Print-to-PDF formatting (no faded grey or invisible text).
    """
    score = getattr(report, "overall_risk_score", 50)
    doc_title = getattr(report, "document_title", filename)
    exec_summary = getattr(report, "executive_summary", "Audit completed.")
    recommendations = getattr(report, "key_strategic_recommendations", [])
    email_draft = getattr(report, "negotiation_email_draft", "")
    clauses = getattr(report, "audited_clauses", [])

    high_count = sum(1 for c in clauses if getattr(c, "risk_tier", "") == "High Risk")
    mod_count = sum(1 for c in clauses if getattr(c, "risk_tier", "") == "Moderate Risk")
    safe_count = sum(1 for c in clauses if getattr(c, "risk_tier", "") == "Safe")
    total_count = len(clauses)

    if score >= 70:
        verdict_class = "verdict-danger"
        verdict_icon = "🚨"
        verdict_title = "DANGEROUS CONTRACT — DO NOT SIGN AS-IS!"
        verdict_desc = "This agreement contains severe one-sided traps under Indian law. If you sign without changes, you could face heavy penalties, pay their legal bills, or be banned from your profession."
        score_color = "#dc2626"
    elif score >= 40:
        verdict_class = "verdict-caution"
        verdict_icon = "⚠️"
        verdict_title = "PROCEED WITH CAUTION — NEEDS SIMPLE CHANGES"
        verdict_desc = "This contract is mostly standard, but contains a few unfair clauses tilted against you. Ask for our recommended adjustments below before signing."
        score_color = "#d97706"
    else:
        verdict_class = "verdict-safe"
        verdict_icon = "✅"
        verdict_title = "FAIR & BALANCED — SAFE TO SIGN"
        verdict_desc = "Great news! This agreement follows standard, fair market practices under Indian law with mutual protections for both sides."
        score_color = "#16a34a"

    # Build clause HTML cards
    clause_cards_html = []
    for c in clauses:
        tier = getattr(c, "risk_tier", "Moderate Risk")
        idx = getattr(c, "clause_index", 1)
        title = getattr(c, "clause_title", "Contract Clause")
        category = getattr(c, "risk_category", "General")
        clause_score = getattr(c, "risk_score", 5)
        explanation = getattr(c, "plain_english_explanation", "")
        issues = getattr(c, "flagged_issues", [])
        redline = getattr(c, "suggested_redline", "")
        orig_text = getattr(c, "original_text", "")
        citation = getattr(c, "grounded_citation", "")
        ref_id = getattr(c, "matched_benchmark_id", "")

        tier_slug = "high" if tier == "High Risk" else ("moderate" if tier == "Moderate Risk" else "safe")
        badge_label = "🚨 RED FLAG" if tier == "High Risk" else ("⚠️ CAUTION" if tier == "Moderate Risk" else "✅ FAIR")

        issues_html = "".join([f"<li>{issue}</li>" for issue in issues]) if issues else "<li>Unbalanced terms detected under Indian contract norms.</li>"

        # Find matching jargon terms for this specific clause
        matched_jargon = find_matching_jargon(f"{title} {orig_text} {explanation} {' '.join(issues)}")
        jargon_box_html = ""
        if matched_jargon:
            jargon_items = "".join([
                f"<div style='margin-bottom: 5px;'><strong>📖 {item['term']}</strong> <em>({item['literal']})</em>: {item['plain_english']}</div>"
                for item in matched_jargon
            ])
            jargon_box_html = f"""
            <div class="callout callout-jargon">
                <div class="callout-label">📖 Legal Terms Translated in this Clause:</div>
                <div class="callout-body">{jargon_items}</div>
            </div>
            """

        card = f"""
        <div class="clause-card filter-item filter-{tier_slug}" data-tier="{tier_slug}">
            <div class="clause-header">
                <div class="badge-row">
                    <span class="badge badge-{tier_slug}">{badge_label}</span>
                    <span class="badge badge-category">{category}</span>
                    <span class="badge badge-score">Severity: {clause_score}/10</span>
                </div>
                <div class="ref-tag">{f"Ref: {ref_id}" if ref_id else ""}</div>
            </div>

            <h3 class="clause-title">{idx}. {title}</h3>

            <div class="callout callout-blue">
                <div class="callout-label">💬 What this actually means in plain English:</div>
                <div class="callout-body">{explanation}</div>
            </div>

            {jargon_box_html}

            <div class="grid-2">
                <div class="callout callout-red">
                    <div class="callout-label">🚩 Why it's a trap under Indian Law:</div>
                    <ul class="trap-list">
                        {issues_html}
                    </ul>
                </div>
                <div class="callout callout-green">
                    <div class="callout-label">✍️ What to ask for instead (Counter-Offer):</div>
                    <div class="redline-text">{redline}</div>
                </div>
            </div>

            <div class="legal-quote-box">
                <div class="quote-header">📄 Original Contract Text & Statutory Reference</div>
                <div class="quote-text">"{orig_text}"</div>
                {f'<div class="quote-citation">⚖️ <strong>Indian Statutory Basis:</strong> {citation}</div>' if citation else ''}
            </div>
        </div>
        """
        clause_cards_html.append(card)

    clauses_rendered = "\n".join(clause_cards_html)
    recommendations_rendered = "".join([
        f'<li class="rec-item"><span class="rec-num">{i+1}</span><span class="rec-text">{r}</span></li>'
        for i, r in enumerate(recommendations)
    ])

    # Escape email draft for JS copy
    escaped_email = email_draft.replace("`", "\\`").replace("$", "\\$")

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LegalLens Safety Report - {doc_title}</title>
    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --border: #e2e8f0;
            --border-dark: #cbd5e1;
            --text-heading: #0f172a;
            --text-body: #1e293b;
            --text-muted: #475569;
            --text-subtle: #64748b;
            --red: #dc2626;
            --red-bg: #fef2f2;
            --red-border: #fecaca;
            --yellow: #d97706;
            --yellow-bg: #fffbeb;
            --yellow-border: #fde68a;
            --green: #16a34a;
            --green-bg: #f0fdf4;
            --green-border: #bbf7d0;
            --blue: #0284c7;
            --blue-bg: #f0f9ff;
            --blue-border: #bae6fd;
            --indigo: #4f46e5;
            --indigo-bg: #eef2ff;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        body {{
            background-color: var(--bg-page);
            color: var(--text-body);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-size: 15px;
            line-height: 1.6;
            padding: 30px 20px;
        }}

        .container {{
            max-width: 980px;
            margin: 0 auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 36px 40px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06);
        }}

        /* Header bar */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .brand {{
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--text-heading);
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.02em;
        }}
        .brand-subtitle {{
            font-size: 0.95rem;
            color: var(--text-muted);
            margin-top: 4px;
            font-weight: 500;
        }}
        .brand-subtitle strong {{
            color: var(--text-heading);
        }}
        .actions {{
            display: flex;
            gap: 12px;
        }}
        .btn {{
            background: #2563eb;
            color: #ffffff !important;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease-in-out;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        .btn:hover {{
            background: #1d4ed8;
            transform: translateY(-1px);
        }}
        .btn-outline {{
            background: #ffffff;
            border: 1px solid var(--border-dark);
            color: var(--text-body) !important;
        }}
        .btn-outline:hover {{
            background: #f1f5f9;
        }}

        /* Verdict Banner */
        .verdict-banner {{
            border-radius: 12px;
            padding: 22px 26px;
            margin-bottom: 25px;
            border-width: 2px;
            border-style: solid;
        }}
        .verdict-danger {{
            background: #fef2f2;
            border-color: #ef4444;
        }}
        .verdict-caution {{
            background: #fffbeb;
            border-color: #f59e0b;
        }}
        .verdict-safe {{
            background: #f0fdf4;
            border-color: #10b981;
        }}
        .verdict-title {{
            font-size: 1.35rem;
            font-weight: 800;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.01em;
        }}
        .verdict-danger .verdict-title {{ color: #991b1b; }}
        .verdict-caution .verdict-title {{ color: #92400e; }}
        .verdict-safe .verdict-title {{ color: #166534; }}

        .verdict-desc {{
            font-size: 1.05rem;
            line-height: 1.6;
            font-weight: 500;
        }}
        .verdict-danger .verdict-desc {{ color: #7f1d1d; }}
        .verdict-caution .verdict-desc {{ color: #78350f; }}
        .verdict-safe .verdict-desc {{ color: #14532d; }}

        /* Metrics Row */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
            margin-bottom: 28px;
        }}
        .metric-card {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 14px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .metric-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}
        .metric-val {{
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.2;
        }}

        /* Section Boxes */
        .summary-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .section-box {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }}
        .section-box-blue {{
            border-left: 4px solid var(--blue);
            background: #f8fafc;
        }}
        .section-box-green {{
            border-left: 4px solid var(--green);
            background: #f8fafc;
        }}
        .section-title {{
            font-size: 1.12rem;
            font-weight: 700;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-heading);
        }}
        .summary-text {{
            color: var(--text-body);
            font-size: 1rem;
            line-height: 1.65;
            font-weight: 450;
        }}

        /* Recommendations */
        .recommendations-list {{
            list-style: none;
            padding: 0;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .rec-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            line-height: 1.55;
            color: var(--text-body);
            font-size: 0.96rem;
        }}
        .rec-num {{
            background: #e2e8f0;
            color: var(--text-heading);
            font-weight: 700;
            font-size: 0.8rem;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        /* Email Card */
        .email-card {{
            background: #f0f7ff;
            border: 1px solid #bae6fd;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 35px;
        }}
        .email-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .email-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #0369a1;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .email-subtitle {{
            font-size: 0.9rem;
            color: #0c4a6e;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        .email-body {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 16px 18px;
            font-family: inherit;
            font-size: 0.95rem;
            line-height: 1.65;
            white-space: pre-wrap;
            color: #0f172a;
        }}

        /* Filter Tabs */
        .filter-bar {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            background: #ffffff;
            border: 1px solid var(--border-dark);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 9999px;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.88rem;
            transition: all 0.15s ease-in-out;
        }}
        .filter-btn:hover {{
            background: #f1f5f9;
            color: var(--text-heading);
        }}
        .filter-btn.active {{
            background: #2563eb;
            color: #ffffff !important;
            border-color: #2563eb;
            box-shadow: 0 1px 3px rgba(37, 99, 235, 0.3);
        }}

        /* Clause Cards */
        .clause-card {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 22px 24px;
            margin-bottom: 22px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        .filter-high {{
            border-left: 5px solid var(--red);
        }}
        .filter-moderate {{
            border-left: 5px solid var(--yellow);
        }}
        .filter-safe {{
            border-left: 5px solid var(--green);
        }}

        .clause-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .badge-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .badge-high {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }}
        .badge-moderate {{ background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }}
        .badge-safe {{ background: #dcfce7; color: #15803d; border: 1px solid #86efac; }}
        .badge-category {{ background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; }}
        .badge-score {{ background: #f1f5f9; color: #334155; border: 1px solid #e2e8f0; font-weight: 700; }}
        .ref-tag {{ font-size: 0.8rem; color: var(--text-subtle); font-family: monospace; font-weight: 600; }}

        .clause-title {{
            font-size: 1.25rem;
            font-weight: 800;
            margin: 8px 0 14px 0;
            color: var(--text-heading);
            letter-spacing: -0.01em;
        }}

        /* Callouts */
        .callout {{
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 14px;
        }}
        .callout-label {{
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 6px;
        }}
        .callout-blue {{
            background: #f0f9ff;
            border-left: 4px solid var(--blue);
            color: #0c4a6e;
        }}
        .callout-blue .callout-label {{ color: #0369a1; }}
        .callout-blue .callout-body {{
            font-size: 0.98rem;
            line-height: 1.6;
            color: #0f172a;
            font-weight: 450;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-bottom: 14px;
        }}
        .callout-red {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-left: 4px solid var(--red);
            color: #7f1d1d;
        }}
        .callout-red .callout-label {{ color: #991b1b; }}
        .trap-list {{
            padding-left: 18px;
            font-size: 0.92rem;
            line-height: 1.55;
            color: #7f1d1d;
        }}

        .callout-green {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-left: 4px solid var(--green);
            color: #14532d;
        }}
        .callout-green .callout-label {{ color: #166534; }}
        .redline-text {{
            font-family: inherit;
            font-size: 0.92rem;
            line-height: 1.55;
            color: #14532d;
            font-weight: 500;
        }}

        .callout-jargon {{
            background: #faf5ff;
            border: 1px solid #f3e8ff;
            border-left: 4px solid #a855f7;
            color: #581c87;
        }}
        .callout-jargon .callout-label {{ color: #7e22ce; }}
        .callout-jargon .callout-body {{
            font-size: 0.92rem;
            line-height: 1.55;
            color: #3b0764;
        }}

        /* Original Text Box */
        .legal-quote-box {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 14px;
            margin-top: 10px;
        }}
        .quote-header {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 6px;
        }}
        .quote-text {{
            font-size: 0.9rem;
            color: #334155;
            line-height: 1.5;
            font-style: italic;
            margin-bottom: 6px;
        }}
        .quote-citation {{
            font-size: 0.85rem;
            color: #4338ca;
            font-weight: 600;
        }}

        /* Legal Jargon Buster */
        .jargon-section-box {{
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 35px;
        }}
        .jargon-main-title {{
            font-size: 1.25rem;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 6px;
        }}
        .jargon-badge {{
            background: #e0e7ff;
            color: #3730a3;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .jargon-subtitle {{
            font-size: 0.92rem;
            color: #475569;
            margin-bottom: 20px;
            line-height: 1.5;
        }}
        .jargon-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}
        .jargon-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            transition: transform 0.1s ease, box-shadow 0.1s ease;
        }}
        .jargon-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(15,23,42,0.06);
            border-color: #cbd5e1;
        }}
        .jargon-header {{
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 8px;
        }}
        .jargon-term {{
            font-size: 1rem;
            font-weight: 800;
            color: #1e3a8a;
            display: block;
        }}
        .jargon-literal {{
            font-size: 0.8rem;
            color: #64748b;
            font-style: italic;
            display: block;
            margin-top: 2px;
        }}
        .jargon-body {{
            font-size: 0.88rem;
            line-height: 1.5;
            color: #1e293b;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .jargon-meaning {{
            background: #f0fdf4;
            border-left: 3px solid #16a34a;
            padding: 8px 10px;
            border-radius: 4px;
            color: #14532d;
        }}
        .jargon-risk {{
            background: #fef2f2;
            border-left: 3px solid #dc2626;
            padding: 8px 10px;
            border-radius: 4px;
            color: #7f1d1d;
        }}
        .jargon-shield {{
            background: #eff6ff;
            border-left: 3px solid #2563eb;
            padding: 8px 10px;
            border-radius: 4px;
            color: #1e40af;
            font-size: 0.82rem;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            border-top: 1px solid var(--border);
            padding-top: 24px;
            margin-top: 40px;
            font-size: 0.88rem;
            color: var(--text-muted);
        }}

        /* =====================================================================
           HIGH-CONTRAST PRINT STYLES (Print to PDF)
           Guarantees 100% crisp, dark, perfectly legible text on white paper.
           ===================================================================== */
        @page {{
            size: A4;
            margin: 12mm 15mm 15mm 15mm;
        }}

        @media print {{
            body {{
                background: #ffffff !important;
                color: #0f172a !important;
                padding: 0 !important;
                font-size: 10.5pt !important;
            }}
            .container {{
                max-width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                box-shadow: none !important;
            }}
            .no-print, .actions, .filter-bar {{
                display: none !important;
            }}

            /* Avoid breaking cards in half across pages */
            .clause-card, .verdict-banner, .section-box, .email-card, .metric-card {{
                break-inside: avoid !important;
                page-break-inside: avoid !important;
                box-shadow: none !important;
            }}

            /* Header & Brand in print */
            .brand {{
                color: #0f172a !important;
            }}
            .brand-subtitle {{
                color: #334155 !important;
            }}

            /* High-contrast Verdict banner */
            .verdict-banner {{
                border-width: 2px !important;
            }}
            .verdict-danger {{
                background: #fef2f2 !important;
                border-color: #ef4444 !important;
            }}
            .verdict-danger .verdict-title {{
                color: #991b1b !important;
            }}
            .verdict-danger .verdict-desc {{
                color: #450a0a !important;
            }}

            .verdict-caution {{
                background: #fffbeb !important;
                border-color: #f59e0b !important;
            }}
            .verdict-caution .verdict-title {{
                color: #92400e !important;
            }}
            .verdict-caution .verdict-desc {{
                color: #451a03 !important;
            }}

            .verdict-safe {{
                background: #f0fdf4 !important;
                border-color: #10b981 !important;
            }}
            .verdict-safe .verdict-title {{
                color: #166534 !important;
            }}
            .verdict-safe .verdict-desc {{
                color: #052e16 !important;
            }}

            /* High-contrast metrics */
            .metric-card {{
                border: 1px solid #cbd5e1 !important;
                background: #ffffff !important;
            }}
            .metric-label {{
                color: #1e293b !important;
                font-weight: 800 !important;
            }}

            /* Executive summary & recommendations */
            .section-box {{
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
            }}
            .section-title {{
                color: #0f172a !important;
            }}
            .summary-text {{
                color: #0f172a !important;
                font-weight: 500 !important;
            }}
            .rec-item {{
                color: #0f172a !important;
            }}
            .rec-num {{
                background: #cbd5e1 !important;
                color: #0f172a !important;
            }}

            /* Email card in print */
            .email-card {{
                background: #f8fafc !important;
                border: 1px solid #94a3b8 !important;
            }}
            .email-title {{
                color: #0369a1 !important;
            }}
            .email-subtitle {{
                color: #1e293b !important;
            }}
            .email-body {{
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                color: #0f172a !important;
            }}

            /* Clause cards in print */
            .clause-card {{
                border: 1px solid #cbd5e1 !important;
                background: #ffffff !important;
                margin-bottom: 16px !important;
            }}
            .clause-title {{
                color: #0f172a !important;
            }}
            .callout-blue {{
                background: #f0f9ff !important;
                border-left: 4px solid #0284c7 !important;
            }}
            .callout-blue .callout-label {{
                color: #0369a1 !important;
            }}
            .callout-blue .callout-body {{
                color: #0c4a6e !important;
                font-weight: 500 !important;
            }}

            .callout-red {{
                background: #fef2f2 !important;
                border: 1px solid #fca5a5 !important;
            }}
            .callout-red .callout-label {{
                color: #991b1b !important;
            }}
            .trap-list {{
                color: #7f1d1d !important;
            }}

            .callout-green {{
                background: #f0fdf4 !important;
                border: 1px solid #86efac !important;
            }}
            .callout-green .callout-label {{
                color: #166534 !important;
            }}
            .redline-text {{
                color: #14532d !important;
            }}

            .callout-jargon {{
                background: #faf5ff !important;
                border: 1px solid #d8b4fe !important;
                border-left: 4px solid #a855f7 !important;
            }}
            .callout-jargon .callout-label {{
                color: #6b21a8 !important;
            }}
            .callout-jargon .callout-body {{
                color: #3b0764 !important;
            }}

            .legal-quote-box {{
                background: #f8fafc !important;
                border: 1px solid #cbd5e1 !important;
            }}
            .quote-header {{
                color: #475569 !important;
            }}
            .quote-text {{
                color: #1e293b !important;
            }}
            .quote-citation {{
                color: #3730a3 !important;
            }}

            /* Jargon Buster Print */
            .jargon-section-box {{
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                margin-bottom: 20px !important;
            }}
            .jargon-card {{
                border: 1px solid #cbd5e1 !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                background: #ffffff !important;
            }}
            .jargon-main-title {{
                color: #0f172a !important;
            }}
            .jargon-term {{
                color: #0f172a !important;
            }}
            .jargon-literal {{
                color: #475569 !important;
            }}
            .jargon-meaning {{
                background: #f0fdf4 !important;
                color: #14532d !important;
                border-left: 3px solid #16a34a !important;
            }}
            .jargon-risk {{
                background: #fef2f2 !important;
                color: #7f1d1d !important;
                border-left: 3px solid #dc2626 !important;
            }}
            .jargon-shield {{
                background: #eff6ff !important;
                color: #1e40af !important;
                border-left: 3px solid #2563eb !important;
            }}

            .footer {{
                color: #475569 !important;
            }}
        }}

        @media (max-width: 768px) {{
            .container {{ padding: 20px 16px; border-radius: 0; }}
            .summary-grid, .grid-2 {{ grid-template-columns: 1fr; }}
            .header {{ flex-direction: column; align-items: flex-start; gap: 15px; }}
        }}
    </style>
</head>
<body>

<div class="container">

    <!-- Top Action Bar -->
    <div class="header">
        <div>
            <div class="brand">⚖️ LegalLens India</div>
            <div class="brand-subtitle">Contract Safety Audit Report for: <strong>{doc_title}</strong></div>
        </div>
        <div class="actions no-print">
            {f'<button class="btn btn-outline" onclick="copyEmail()">📋 Copy Negotiation Email</button>' if email_draft else ''}
            <button class="btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
        </div>
    </div>

    <!-- Overall Verdict -->
    <div class="verdict-banner {verdict_class}">
        <div class="verdict-title">
            <span>{verdict_icon}</span>
            <span>{verdict_title}</span>
        </div>
        <div class="verdict-desc">{verdict_desc}</div>
    </div>

    <!-- Quick Metrics -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Safety Risk Index</div>
            <div class="metric-val" style="color: {score_color};">{score}/100</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Red Flags (Traps)</div>
            <div class="metric-val" style="color: var(--red);">🚨 {high_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Cautions (To Fix)</div>
            <div class="metric-val" style="color: var(--yellow);">⚠️ {mod_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Fair Boilerplate</div>
            <div class="metric-val" style="color: var(--green);">✅ {safe_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Sections Scanned</div>
            <div class="metric-val" style="color: var(--text-heading);">📑 {total_count}</div>
        </div>
    </div>

    <!-- Plain-English Summary & Strategic Priorities -->
    <div class="summary-grid">
        <div class="section-box section-box-blue">
            <div class="section-title">💡 Plain-English Assessment</div>
            <p class="summary-text">{exec_summary}</p>
        </div>
        <div class="section-box section-box-green">
            <div class="section-title">🎯 Priority Recommendations Before Signing</div>
            <ul class="recommendations-list">
                {recommendations_rendered}
            </ul>
        </div>
    </div>

    <!-- Ready-to-Send Negotiation Message -->
    {f'''
    <div class="email-card">
        <div class="email-header">
            <div class="email-title">📩 Ready-to-Send Email to Client/Vendor</div>
            <button class="btn btn-outline no-print" style="font-size: 0.8rem; padding: 4px 10px;" onclick="copyEmail()">📋 Copy</button>
        </div>
        <p class="email-subtitle">Send this polite, professional message to negotiate fair terms:</p>
        <div class="email-body" id="emailDraft">{email_draft}</div>
    </div>
    ''' if email_draft else ''}

    <!-- Legal Jargon Buster (Demystifying Technical Terms) -->
    {render_jargon_buster_html()}

    <!-- Detailed Clause Explorer -->
    <div style="margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center;">
        <h2 style="font-size: 1.35rem; font-weight: 800; color: var(--text-heading); letter-spacing: -0.01em;">🔍 Detailed Clause Breakdown</h2>
    </div>

    <!-- Filter Buttons (Hidden in Print) -->
    <div class="filter-bar no-print">
        <button class="filter-btn active" onclick="filterClauses('all', this)">Show All ({total_count})</button>
        <button class="filter-btn" onclick="filterClauses('high', this)">🚨 Red Flags ({high_count})</button>
        <button class="filter-btn" onclick="filterClauses('moderate', this)">⚠️ Cautions ({mod_count})</button>
        <button class="filter-btn" onclick="filterClauses('safe', this)">✅ Fair Terms ({safe_count})</button>
    </div>

    <!-- Clauses List -->
    <div id="clausesContainer">
        {clauses_rendered}
    </div>

    <!-- Footer -->
    <div class="footer">
        Generated by <strong>LegalLens India</strong> • Citation-Grounded Legal Safety Pipeline • Indian Contract Act 1872 & DPDP Act 2023 Compliant
    </div>

</div>

<script>
    function filterClauses(tier, btn) {{
        const buttons = document.querySelectorAll('.filter-btn');
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const items = document.querySelectorAll('.clause-card');
        items.forEach(card => {{
            if (tier === 'all') {{
                card.style.display = 'block';
            }} else {{
                if (card.getAttribute('data-tier') === tier) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }}
        }});
    }}

    function copyEmail() {{
        const text = `{escaped_email}`;
        navigator.clipboard.writeText(text).then(() => {{
            alert('Negotiation Email copied to clipboard!');
        }}).catch(err => {{
            const el = document.getElementById('emailDraft');
            if (el) {{
                const range = document.createRange();
                range.selectNodeContents(el);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('copy');
                alert('Negotiation Email copied to clipboard!');
            }}
        }});
    }}
</script>

</body>
</html>
"""
    return html_template


def generate_word_friendly_doc(report: DocumentAuditReport, filename: str = "Contract") -> str:
    """
    Generates an HTML-based formatted document optimized for opening cleanly in Microsoft Word
    with colored callouts, tables, and borders (without unformatted Markdown hashes).
    """
    score = getattr(report, "overall_risk_score", 50)
    doc_title = getattr(report, "document_title", filename)
    exec_summary = getattr(report, "executive_summary", "")
    recommendations = getattr(report, "key_strategic_recommendations", [])
    email_draft = getattr(report, "negotiation_email_draft", "")
    clauses = getattr(report, "audited_clauses", [])

    rec_rows = "".join([f"<li style='margin-bottom: 6px; color: #1e293b;'>{r}</li>" for r in recommendations])

    clause_rows = []
    for c in clauses:
        tier = getattr(c, "risk_tier", "Moderate Risk")
        idx = getattr(c, "clause_index", 1)
        title = getattr(c, "clause_title", "Contract Clause")
        category = getattr(c, "risk_category", "General")
        explanation = getattr(c, "plain_english_explanation", "")
        issues = getattr(c, "flagged_issues", [])
        redline = getattr(c, "suggested_redline", "")
        orig_text = getattr(c, "original_text", "")
        citation = getattr(c, "grounded_citation", "")

        tier_color = "#dc2626" if tier == "High Risk" else ("#d97706" if tier == "Moderate Risk" else "#059669")
        tier_bg = "#fee2e2" if tier == "High Risk" else ("#fef3c7" if tier == "Moderate Risk" else "#d1fae5")
        issues_list = "".join([f"<li style='margin-bottom: 4px; color: #7f1d1d;'>{i}</li>" for i in issues])

        matched_jargon = find_matching_jargon(f"{title} {orig_text} {explanation} {' '.join(issues)}")
        jargon_word_box = ""
        if matched_jargon:
            jargon_lines = "<br>".join([
                f"<strong>📖 {item['term']} ({item['literal']}):</strong> {item['plain_english']}"
                for item in matched_jargon
            ])
            jargon_word_box = f"""
            <div style="background: #faf5ff; border: 1px solid #d8b4fe; border-left: 4px solid #a855f7; padding: 8px 10px; margin-bottom: 12px; font-size: 9.5pt; color: #581c87;">
                <strong style="color: #6b21a8;">📖 Legal Terms Translated in this Clause:</strong><br>
                {jargon_lines}
            </div>
            """

        row_html = f"""
        <div style="border: 1px solid #cbd5e1; border-left: 6px solid {tier_color}; border-radius: 6px; padding: 16px; margin-bottom: 18px; background: #ffffff;">
            <div style="margin-bottom: 8px;">
                <span style="background: {tier_bg}; color: {tier_color}; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 10pt;">
                    {tier.upper()}
                </span>
                <span style="color: #475569; font-size: 10pt; margin-left: 10px;">Domain: <strong>{category}</strong></span>
            </div>

            <h3 style="margin-top: 8px; margin-bottom: 10px; color: #0f172a; font-size: 13pt;">{idx}. {title}</h3>

            <div style="background: #f0f9ff; border-left: 4px solid #0284c7; padding: 10px 12px; margin-bottom: 12px; color: #0c4a6e; font-size: 10.5pt;">
                <strong style="color: #0369a1;">💬 What this means in plain English:</strong><br>
                {explanation}
            </div>

            {jargon_word_box}

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 12px;">
                <tr>
                    <td style="width: 50%; vertical-align: top; background: #fef2f2; border: 1px solid #fecaca; padding: 10px;">
                        <strong style="color: #991b1b;">🚩 Why it is a trap under Indian Law:</strong>
                        <ul style="margin: 6px 0; padding-left: 18px; font-size: 10pt;">
                            {issues_list}
                        </ul>
                    </td>
                    <td style="width: 50%; vertical-align: top; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px;">
                        <strong style="color: #166534;">✍️ What to ask for instead (Counter-Offer):</strong>
                        <div style="margin-top: 6px; color: #14532d; font-size: 9.5pt; font-family: monospace;">
                            {redline}
                        </div>
                    </td>
                </tr>
            </table>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 10px; font-size: 9pt; color: #334155;">
                <strong>Exact Contract Text:</strong> <em>"{orig_text}"</em><br>
                {f'<strong style="color: #3730a3;">Indian Law Basis:</strong> {citation}' if citation else ''}
            </div>
        </div>
        """
        clause_rows.append(row_html)

    clauses_doc_html = "\n".join(clause_rows)

    word_template = f"""<html xmlns:o="urn:schemas-microsoft-com:office:office"
xmlns:w="urn:schemas-microsoft-com:office:word"
xmlns="http://www.w3.org/TR/REC-html40">
<head>
    <meta charset="utf-8">
    <title>LegalLens Safety Report</title>
    <style>
        body {{
            font-family: 'Calibri', 'Arial', sans-serif;
            font-size: 11pt;
            color: #1e293b;
            line-height: 1.5;
            margin: 40px;
        }}
        h1 {{ font-size: 22pt; color: #0f172a; margin-bottom: 4px; }}
        h2 {{ font-size: 14pt; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; margin-top: 24px; }}
    </style>
</head>
<body>
    <h1>⚖️ LegalLens India: Contract Safety Audit</h1>
    <div style="font-size: 12pt; color: #334155; margin-bottom: 16px;">
        Contract Reviewed: <strong>{doc_title}</strong> | Overall Risk Score: <strong>{score}/100</strong>
    </div>

    <h2>1. Executive Summary</h2>
    <p style="font-size: 11pt; color: #0f172a; background: #f8fafc; border-left: 4px solid #2563eb; padding: 12px; line-height: 1.6;">
        {exec_summary}
    </p>

    <h2>2. Key Recommendations Before Signing</h2>
    <ul style="font-size: 11pt; line-height: 1.6; padding-left: 20px;">
        {rec_rows}
    </ul>

    {f'''
    <h2>3. Ready-to-Send Negotiation Message</h2>
    <div style="background: #eff6ff; border: 1px solid #bfdbfe; padding: 14px; font-family: monospace; font-size: 10pt; color: #0f172a; white-space: pre-wrap;">
{email_draft}
    </div>
    ''' if email_draft else ''}

    <!-- 4. Legal Jargon Buster -->
    {render_jargon_buster_word_html()}

    <h2>5. Detailed Clause-by-Clause Legal Analysis</h2>
    {clauses_doc_html}

    <div style="margin-top: 30px; text-align: center; font-size: 9pt; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 10px;">
        Generated by LegalLens India • Citation-Grounded Contract Auditing Pipeline
    </div>
</body>
</html>
"""
    return word_template
