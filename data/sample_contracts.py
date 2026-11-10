"""
LegalLens - Indian Commercial Contracts Catalog for Instant Testing
Specifically tailored to the Indian Legal System (Indian Contract Act 1872,
Arbitration & Conciliation Act 1996, DPDP Act 2023, and Indian Court Precedents).
"""

SAMPLE_INDIAN_IT_EMPLOYMENT_BOND = """EMPLOYMENT AGREEMENT & SERVICE BOND

This Employment Agreement ("Agreement") is executed at Bengaluru, Karnataka, by and between CyberNxt Tech Solutions Pvt. Ltd., having its registered office at Electronic City, Bengaluru ("Company"), and the undersigned employee ("Employee").

SECTION 1: MANDATORY SERVICE BOND & RESIGNATION PENALTY
Employee agrees to serve the Company for a minimum, non-negotiable period of thirty-six (36) months from the Date of Joining. If Employee resigns, abandons service, or terminates employment prior to completing thirty-six (36) months for any reason whatsoever, Employee shall pay to Company a fixed liquidated damages penalty of INR 3,50,000 (Rupees Three Lakhs Fifty Thousand) within seven (7) days of notice.

SECTION 2: DEPOSIT OF ORIGINAL EDUCATIONAL CERTIFICATES
As security for due compliance with the Service Bond, Employee shall deposit original Degree Certificates, Marksheets, and PAN/Aadhaar copies with the Company's HR Department, to be retained in Company custody until successful completion of the 36-month service tenure.

SECTION 3: POST-TERMINATION NON-COMPETE RESTRICTION
Employee agrees that for a period of two (2) years following resignation or termination from the Company, Employee shall not directly or indirectly accept employment with, consult for, or advise any IT services or software engineering firm operating anywhere in Bengaluru, Hyderabad, Pune, Gurugram, or across India.

SECTION 4: UNILATERAL PAYCHECK DEDUCTIONS
Company reserves the unrestricted right to deduct amounts from Employee's monthly salary or final settlement to offset perceived training overheads, hardware depreciation, or client dissatisfaction, without requiring prior written consent.

SECTION 5: DISPUTE RESOLUTION BY SOLE ARBITRATOR APPOINTED BY MANAGING DIRECTOR
Any dispute arising under this Agreement shall be referred to arbitration by a Sole Arbitrator nominated and appointed unilaterally by the Managing Director of the Company. The arbitration seat shall be Bengaluru, and proceedings shall be final and binding.
"""

SAMPLE_INDIAN_COMMERCIAL_RENTAL = """COMMERCIAL LEASE & LEAVE AND LICENSE AGREEMENT

This Agreement is made at Mumbai, Maharashtra, between SeaView Commercial Properties LLP ("Licensor/Landlord") and Tenant LLP ("Licensee/Tenant").

SECTION 1: LOCK-IN PERIOD & UNILATERAL SECURITY DEPOSIT FORFEITURE
The Licensee agrees to a strict Lock-in Period of thirty-six (36) months. If Licensee vacates the Premises prior to expiry of the Lock-in Period, or if Licensee delays monthly rent payment by more than ten (10) days, the entire Security Deposit of INR 15,00,000 (Rupees Fifteen Lakhs) shall be permanently forfeited by Landlord as non-refundable liquidated penalty.

SECTION 2: STEEPEST ANNUAL RENT ESCALATION & STRUCTURAL PASS-THROUGH
The monthly license fee shall escalate automatically by twenty percent (20%) every twelve (12) months. Furthermore, Licensee shall bear 100% of all building structural repairs, lift replacements, and municipal property tax re-assessments levied by BMC, regardless of pre-existing wear and tear.

SECTION 3: OUSTER OF LOCAL JURISDICTION
Notwithstanding the location of the Premises in Mumbai, the parties agree that only the District Court at Shimla, Himachal Pradesh, shall have exclusive territorial jurisdiction to entertain any dispute or eviction suit arising under this Agreement.

SECTION 4: COMPLETE WAIVER OF STATUTORY LIMITATION
Licensee agrees that any claim against Landlord regarding billing disputes or property defects must be filed within thirty (30) days of occurrence, failing which Licensee's legal rights shall stand permanently extinguished.
"""

SAMPLE_INDIAN_FREELANCE_AGREEMENT = """CONSULTING & FREELANCE SERVICES AGREEMENT

This Agreement is made between BrandPulse Media Pvt. Ltd., New Delhi ("Client") and the Independent Consultant ("Consultant").

SECTION 1: UNLIMITED UNILATERAL INDEMNIFICATION
Consultant shall indemnify, defend, and hold harmless Client, its directors, and promoters from and against any and all claims, financial damages, consequential losses, and advocate fees arising from the deliverables, even if such loss results partly or wholly from Client's own delay, negligence, or defective brief.

SECTION 2: ASSIGNMENT OF ALL PAST AND FUTURE INTELLECTUAL PROPERTY
Consultant hereby assigns to Client all rights, title, copyright, and patent interest in all software, designs, methodologies, and frameworks created, conceived, or utilized during the term, without limitation of territory or medium under Section 19 of the Copyright Act, 1957, and waives all moral rights under Section 57.

SECTION 3: UNILATERAL TERMINATION WITHOUT ACCRUED COMPENSATION
Client reserves the right to cancel this project at any time upon twelve (12) hours' WhatsApp or email notice. Upon such cancellation, Client shall not be liable to pay any pending or milestone invoices for work already performed, and Consultant shall immediately surrender all project files.

SECTION 4: ARBITRATION UNDER MANAGING DIRECTOR'S NOMINEE
All disputes shall be resolved by a Sole Arbitrator appointed solely by the Client's Managing Director, with Consultant bearing 100% of all arbitrator fees and travel costs.
"""

SAMPLE_BALANCED_INDIAN_NDA = """MUTUAL NON-DISCLOSURE AGREEMENT (UNDER INDIAN LAW)

This Mutual Non-Disclosure Agreement ("Agreement") is executed at New Delhi, India, between Party A and Party B (collectively, the "Parties").

1. CONFIDENTIAL INFORMATION & PERMITTED USE
"Confidential Information" refers to proprietary technical, business, and financial information disclosed by either Party, marked as confidential or reasonably understood to be confidential. Each party agrees to use Confidential Information solely to evaluate a potential commercial collaboration.

2. STATUTORY LEGAL EXCLUSIONS
Confidential Information does not include information that: (a) is or becomes publicly available without breach; (b) was already in recipient's lawful possession prior to disclosure; (c) is independently developed without reference to discloser's confidential data; or (d) is required to be disclosed by order of a competent Indian court, regulatory body (SEBI, RBI, CCI), or statutory authority, provided prompt written notice is given.

3. STANDARD OF CARE & DURATION
Each party shall protect the other's Confidential Information with the same degree of care it uses for its own confidential data, but not less than reasonable care. Obligations under this Agreement shall survive for a period of two (2) years from the date of disclosure.

4. BALANCED LIABILITY CAP
Neither party shall be liable for indirect, incidental, or consequential damages under Section 73 of the Indian Contract Act, 1872. Cumulative aggregate liability for direct damages shall be capped at INR 10,00,000 (Rupees Ten Lakhs) or total fees exchanged under the engagement.

5. GOVERNING LAW & JURISDICTION
This Agreement shall be governed by the laws of the Republic of India. The courts of competent jurisdiction at New Delhi shall have exclusive jurisdiction over any dispute arising under this Agreement.
"""

SAMPLE_CONTRACTS_CATALOG = {
    "🇮🇳 Predatory IT Employment Bond (₹3.5L Penalty & Non-Compete)": SAMPLE_INDIAN_IT_EMPLOYMENT_BOND,
    "🇮🇳 Commercial Rental Agreement (Deposit Forfeiture & 20% Hike)": SAMPLE_INDIAN_COMMERCIAL_RENTAL,
    "🇮🇳 Freelancer Contract (Unilateral Arbitrator & Fee Forfeiture)": SAMPLE_INDIAN_FREELANCE_AGREEMENT,
    "🛡️ Balanced Mutual NDA (Indian Contract Act Compliant)": SAMPLE_BALANCED_INDIAN_NDA,
}
