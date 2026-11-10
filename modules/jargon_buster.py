"""
LegalLens India - Legal Jargon Buster & Plain-English Contract Dictionary
Demystifies complex Latin, legalese, and technical terms into simple, relatable language
grounded in the Indian Legal System (Indian Contract Act 1872, Arbitration Act 1996, DPDP Act 2023).
"""

# [Summary]: Plain-English dictionary for complex legal terms (e.g. Void Ab Initio, Liquidated Damages).

from typing import List, Dict

COMMON_LEGAL_TERMS: List[Dict[str, str]] = [
    {
        "term": "Void Ab Initio",
        "pronunciation": "VOH-yd ab in-ISH-ee-oh",
        "literal": "Invalid from day one",
        "plain_english": "A clause that is legally dead on arrival. In the eyes of an Indian court, it has zero legal power and is treated as if it was never written.",
        "real_life_risk": "Many employment agreements state you cannot work for any competitor for 1 to 2 years after leaving. In India, post-employment non-competes are 100% void ab initio under Section 27. An employer cannot legally stop you from taking another job.",
        "indian_law_shield": "Section 27, Indian Contract Act 1872 & Supreme Court of India in Percept D'Mark v. Zaheer Khan (2006)"
    },
    {
        "term": "Liquidated Damages",
        "pronunciation": "LIK-wid-ay-tid DAM-ij-iz",
        "literal": "Pre-agreed penalty or compensation sum",
        "plain_english": "A fixed amount written into a contract as a penalty fine if someone terminates early or makes a mistake.",
        "real_life_risk": "If an employment bond says 'You must pay ₹5 Lakhs if you resign before 2 years', they CANNOT automatically demand or seize that full amount. Under Indian law, companies can only recover actual, proven training expenses—never punitive penalty profits.",
        "indian_law_shield": "Section 74, Indian Contract Act 1872 & Supreme Court in Kailash Nath Associates v. DDA (2015)"
    },
    {
        "term": "Unilateral Indemnity",
        "pronunciation": "YOO-nih-LAT-er-ul in-DEM-nih-tee",
        "literal": "One-sided promise to pay someone else's legal losses",
        "plain_english": "An unfair clause where you promise to pay out of your own pocket for all lawsuits, government fines, or attorney fees the client/landlord suffers—while they promise nothing to protect you.",
        "real_life_risk": "If a third party sues the company for any reason related to the project—even if the company was partly at fault—a unilateral indemnity clause could be used to demand you pay their expensive legal bills.",
        "indian_law_shield": "Sections 124 & 125, Indian Contract Act 1872. Always negotiate this to be 'Mutual and capped to total fees paid'."
    },
    {
        "term": "Ouster of Jurisdiction",
        "pronunciation": "OW-ster of joor-is-DIK-shun",
        "literal": "Forcing all legal disputes into a faraway court",
        "plain_english": "A sneaky clause specifying that if any legal disagreement happens, you can only file a case in a specific distant city (e.g. forcing a Bangalore software developer to travel to Shimla or Delhi).",
        "real_life_risk": "Companies deliberately insert distant jurisdiction clauses to intimidate individual freelancers, tenants, or employees from filing claims to recover unpaid salaries or retained security deposits.",
        "indian_law_shield": "Section 28, Indian Contract Act 1872 & Supreme Court in ABC Laminart v. A.P. Agencies (1989). A court cannot have jurisdiction if no part of the contract was performed there."
    },
    {
        "term": "Unilateral Arbitrator Appointment",
        "pronunciation": "YOO-nih-LAT-er-ul AHR-bih-tray-tor",
        "literal": "Hand-picking the private judge in one's own dispute",
        "plain_english": "A clause stating that only the company's Managing Director or their appointed representative has the sole authority to choose who acts as the arbitrator (private judge).",
        "real_life_risk": "When one party hand-picks the judge, the proceedings are heavily biased against you. You lose the fundamental constitutional right to a fair, neutral hearing.",
        "indian_law_shield": "Section 12(5), Arbitration and Conciliation Act 1996 & Supreme Court in Perkins Eastman Architects v. HSCC (2019)"
    },
    {
        "term": "Quantum Meruit",
        "pronunciation": "KWAN-tum MARE-oo-it",
        "literal": "As much as one has earned / Fair compensation for work completed",
        "plain_english": "A legal principle guaranteeing that if a client cancels a contract early, they MUST pay you for the percentage of work you already finished—they cannot refuse payment by claiming the milestone wasn't 100% complete.",
        "real_life_risk": "A client cancels a project after you finished 80% of the code or designs, and points to a clause saying 'Payment only upon final delivery'. Under quantum meruit, they are legally bound to pay for the 80% completed.",
        "indian_law_shield": "Section 70, Indian Contract Act 1872 (Obligation of person enjoying benefit of non-gratuitous act)"
    },
    {
        "term": "Severability",
        "pronunciation": "SEV-er-uh-BIL-ih-tee",
        "literal": "The rest of the contract stays alive",
        "plain_english": "If a judge rules that one specific clause in your contract is illegal or void (like an unlawful non-compete), the rest of the contract remains active and valid instead of the whole deal falling apart.",
        "real_life_risk": "Without a severability clause, an entire contract could theoretically be voided in court if one minor section violates local regulations.",
        "indian_law_shield": "Common law 'Blue Pencil Doctrine' recognized by Indian High Courts & Supreme Court"
    },
    {
        "term": "Force Majeure",
        "pronunciation": "FORS mah-ZHUR",
        "literal": "Superior force / Acts of God",
        "plain_english": "A clause that pauses or excuses contract duties when extreme, unavoidable disasters (floods, earthquakes, wars, government lockdowns) make fulfilling the agreement physically or legally impossible.",
        "real_life_risk": "Without a fair force majeure clause, a tenant or service provider could be sued for breach of contract even when citywide flooding or government curfews prevent work.",
        "indian_law_shield": "Section 56, Indian Contract Act 1872 (Doctrine of Frustration) & Energy Watchdog v. CERC (2017)"
    }
]


def render_jargon_buster_html() -> str:
    """
    Renders the Legal Jargon Buster card grid for inclusion in the standalone HTML report.
    Includes print-safe high-contrast styling and responsive design.
    """
    cards_html = []
    for item in COMMON_LEGAL_TERMS:
        card = f"""
        <div class="jargon-card">
            <div class="jargon-header">
                <span class="jargon-term">📖 {item['term']}</span>
                <span class="jargon-literal">({item['literal']})</span>
            </div>
            <div class="jargon-body">
                <div class="jargon-meaning">
                    <strong>In Plain English:</strong> {item['plain_english']}
                </div>
                <div class="jargon-risk">
                    <strong>⚠️ Real-World Trap:</strong> {item['real_life_risk']}
                </div>
                <div class="jargon-shield">
                    <strong>⚖️ Indian Law Protection:</strong> {item['indian_law_shield']}
                </div>
            </div>
        </div>
        """
        cards_html.append(card)

    rendered_cards = "\n".join(cards_html)

    return f"""
    <!-- Legal Jargon Buster Section -->
    <div class="jargon-section-box">
        <div class="jargon-main-title">
            <span>📖 Legal Jargon Buster: Demystifying Complex Contract Terms</span>
            <span class="jargon-badge">Plain English Translation</span>
        </div>
        <p class="jargon-subtitle">
            Contracts often use dense Latin or legal phrasing to hide unfair obligations.
            Here is what these common technical terms actually mean under Indian Law:
        </p>
        <div class="jargon-grid">
            {rendered_cards}
        </div>
    </div>
    """


def render_jargon_buster_word_html() -> str:
    """
    Renders the Legal Jargon Buster table for Microsoft Word (.doc) exports.
    """
    rows = []
    for item in COMMON_LEGAL_TERMS:
        row = f"""
        <tr style="border-bottom: 1px solid #cbd5e1;">
            <td style="padding: 10px; background: #f8fafc; font-weight: bold; color: #0f172a; width: 25%; vertical-align: top;">
                <strong>{item['term']}</strong><br>
                <span style="font-size: 9pt; color: #64748b; font-style: italic;">({item['literal']})</span>
            </td>
            <td style="padding: 10px; color: #1e293b; width: 45%; vertical-align: top; font-size: 10pt;">
                <strong>What it means:</strong> {item['plain_english']}<br><br>
                <strong style="color: #b91c1c;">⚠️ Real-World Risk:</strong> {item['real_life_risk']}
            </td>
            <td style="padding: 10px; background: #f0fdf4; color: #166534; width: 30%; vertical-align: top; font-size: 9.5pt;">
                <strong>Indian Law Protection:</strong><br>
                {item['indian_law_shield']}
            </td>
        </tr>
        """
        rows.append(row)

    rendered_rows = "\n".join(rows)

    return f"""
    <h2>📖 Legal Jargon Buster: Understand Complex Contract Terms in Plain English</h2>
    <p style="font-size: 10.5pt; color: #475569; margin-bottom: 12px;">
        Common legal and Latin terms explained simply with their corresponding protections under the Indian Legal System:
    </p>
    <table style="width: 100%; border-collapse: collapse; border: 1px solid #cbd5e1; margin-bottom: 24px;">
        <thead>
            <tr style="background: #e2e8f0; color: #0f172a; font-weight: bold; font-size: 10.5pt;">
                <th style="padding: 10px; text-align: left; border: 1px solid #cbd5e1;">Legal Term</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #cbd5e1;">Plain-English Meaning & Real-World Trap</th>
                <th style="padding: 10px; text-align: left; border: 1px solid #cbd5e1;">Indian Statutory Protection</th>
            </tr>
        </thead>
        <tbody>
            {rendered_rows}
        </tbody>
    </table>
    """


def find_matching_jargon(text: str) -> List[Dict[str, str]]:
    """
    Scans a contract clause or explanation and returns matching jargon dictionary entries
    so beginners get instant, 1-click clarity on what specific legal words mean.
    """
    if not text:
        return []
    lower_text = text.lower()
    matches = []

    triggers = [
        (["void ab initio", "ab initio", "void"], "Void Ab Initio"),
        (["liquidated damage", "liquidated damages", "penalty bond", "forfeiture", "forfeited"], "Liquidated Damages"),
        (["indemnif", "indemnity", "indemnities", "hold harmless"], "Unilateral Indemnity"),
        (["jurisdiction", "ouster", "courts at", "courts in", "seat of arbitration"], "Ouster of Jurisdiction"),
        (["arbitrat", "sole arbitrator", "managing director shall appoint"], "Unilateral Arbitrator Appointment"),
        (["quantum meruit", "pro-rata", "prorated payment"], "Quantum Meruit"),
        (["severab", "severability", "blue pencil"], "Severability"),
        (["force majeure", "act of god", "doctrine of frustration"], "Force Majeure"),
    ]

    matched_term_names = set()
    for keywords, term_name in triggers:
        if any(kw in lower_text for kw in keywords):
            matched_term_names.add(term_name)

    for item in COMMON_LEGAL_TERMS:
        if item["term"] in matched_term_names:
            matches.append(item)

    return matches
