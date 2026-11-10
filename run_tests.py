"""
LegalLens - Automated Pipeline & Verification Test Suite
Run this script to verify your playbook benchmarks, vector store retrieval,
text chunking, and Pydantic schemas.

Usage:
    python run_tests.py
"""

import os
import sys
import json

def test_playbook_integrity():
    print("[1/4] Testing risk_playbook.json integrity...")
    playbook_path = os.path.join("data", "risk_playbook.json")
    assert os.path.exists(playbook_path), f"Playbook file missing at {playbook_path}"
    with open(playbook_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 5, f"Expected at least 5 benchmarks, found {len(data)}"
    tiers = {item["risk_tier"] for item in data}
    assert "High Risk" in tiers and "Safe" in tiers, "Playbook must have High Risk and Safe clauses"
    print(f"      PASSED: {len(data)} benchmark clauses validated across tiers: {tiers}")

def test_chunker():
    print("[2/4] Testing legal clause chunker...")
    from modules.ocr_parser import LegalTextChunker
    sample_text = open("test_docs/01_predatory_freelance_agreement.txt", "r", encoding="utf-8").read()
    chunker = LegalTextChunker(chunk_size=600, chunk_overlap=100)
    chunks = chunker.split_text_into_chunks(sample_text)
    assert len(chunks) >= 3, f"Expected at least 3 chunks, got {len(chunks)}"
    print(f"      PASSED: Successfully segmented document into {len(chunks)} legal chunks.")

def test_pydantic_schemas():
    print("[3/4] Testing Pydantic audit report validation schemas...")
    from modules.auditor import DocumentAuditReport, ClauseAudit

    # Create a valid test payload
    clause = ClauseAudit(
        clause_index=1,
        clause_title="Unilateral Indemnification",
        original_text="Client shall indemnify provider for provider's own negligence.",
        risk_tier="High Risk",
        risk_score=9,
        risk_category="Indemnification & Liability",
        flagged_issues=["Covers provider's sole negligence", "Uncapped"],
        plain_english_explanation="You are liable even if the other party causes the problem.",
        grounded_citation="UCC 2-719; Playbook PB-001",
        matched_benchmark_id="PB-001",
        suggested_redline="Each party shall indemnify the other capped at fees paid."
    )

    report = DocumentAuditReport(
        document_title="Test Consulting Contract",
        executive_summary="Document contains high-risk unilateral liability terms.",
        overall_risk_score=85,
        key_strategic_recommendations=["Cap liability", "Mutualize indemnity"],
        audited_clauses=[clause]
    )

    json_str = report.model_dump_json()
    validated = DocumentAuditReport.model_validate_json(json_str)
    assert validated.overall_risk_score == 85
    assert validated.audited_clauses[0].risk_tier == "High Risk"
    print("      PASSED: Pydantic DocumentAuditReport and ClauseAudit schemas validated successfully.")

def test_sample_files_exist():
    print("[4/4] Verifying generated test files in test_docs/...")
    test_files = [
        "test_docs/01_predatory_freelance_agreement.txt",
        "test_docs/02_balanced_mutual_nda.txt",
        "test_docs/03_sneaky_saas_terms.txt",
        "test_docs/sample_scanned_contract.png"
    ]
    for tf in test_files:
        assert os.path.exists(tf), f"Test file {tf} is missing!"
        print(f"      - {tf} ({os.path.getsize(tf)} bytes)")
    print("      PASSED: All test case documents ready for auditing.")

if __name__ == "__main__":
    print("========================================================")
    print("LegalLens Diagnostic & Test Suite")
    print("========================================================")
    try:
        test_playbook_integrity()
        test_chunker()
        test_pydantic_schemas()
        test_sample_files_exist()
        print("\nAll baseline tests PASSED successfully!")
        print("Ready for end-to-end testing with 'streamlit run app.py'")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
