"""
Detective Nexus Forensic Crime Lab Simulator
Provides simulated scientific laboratory testing on evidence exhibits:
1. AFIS Latent Fingerprint Ridge Matching
2. UV-Visible Chemical Fiber Spectrometry
3. Digital Cryptographic SHA-256 Tamper Audit
4. Touch DNA 16-Locus STR PCR Profiling
Produces official Forensic Laboratory Certificates.
"""

from typing import Dict, Any, Tuple
import hashlib
import time

class ForensicLabEngine:
    """
    Simulates scientific forensic laboratory tests on cataloged evidence exhibits.
    Converts circumstantial clues into laboratory-verified forensic proofs.
    """

    TEST_TYPES = [
        "🔬 UV-Vis Micro-Spectrometry & Dye Chromatography",
        "🖐️ AFIS Latent Friction Ridge / Fingerprint Match",
        "🧬 Touch DNA 16-Locus STR PCR Profiling",
        "💻 Digital Cryptographic HMAC / Tamper Audit"
    ]

    @classmethod
    def run_lab_test(cls, evidence_id: str, test_type: str, case_context: Dict[str, Any] = None) -> Tuple[str, str]:
        """
        Runs scientific test on chosen evidence exhibit.
        Returns: (result_summary, html_certificate)
        """
        ev_lower = (evidence_id or "").lower()
        test_lower = (test_type or "").lower()

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC")
        case_id = case_context.get("case_id", "CASE-001") if case_context else "CASE-001"

        # 1. Chemical Spectrometry (Fibers / Residue)
        if "spectrometry" in test_lower or "fiber" in ev_lower or "e-e" in ev_lower:
            test_name = "FTIR MICRO-SPECTROMETRY & DYE CHROMATOGRAPHY"
            lab_division = "Division of Materials & Forensic Chemistry"
            specimen = "Evidence Exhibit E-E (Recovered Blue Velvet Micro-Fibers)"
            method = "Fourier-Transform Infrared Microspectroscopy (4000-400 cm⁻¹)"
            findings = "Spectral absorbance peak matches 100% with the dyed silk-velvet cushion of the Northbridge Museum rotunda display vitrine. Dye formulation confirms CI Acid Blue 92."
            match_rate = "99.8% SPECTRAL MATCH"
            admissibility = "COURT ADMISSIBLE // DEFINITIVE PHYSICAL TRACE"
            status_color = "#10b981" # Emerald

        # 2. Latent Fingerprint AFIS Match
        elif "fingerprint" in test_lower or "ridge" in test_lower or "e-b" in ev_lower:
            test_name = "AUTOMATED FINGERPRINT IDENTIFICATION SYSTEM (AFIS-7)"
            lab_division = "Latent Print & Biometrics Section"
            specimen = f"Evidence Exhibit {evidence_id} (Latent Ridge Swab)"
            method = "Multi-Spectral Ridge Minutiae Extraction (16 Characteristic Points)"
            findings = "Minutiae pattern exhibits 14 matching bifurcations and ridge endings consistent with suspect database reference profile. Zero signs of glove slippage."
            match_rate = "98.7% CONCORDANCE (14 MATCHING MINUTIAE)"
            admissibility = "COURT ADMISSIBLE // STATISTICALLY CONCLUSIVE"
            status_color = "#10b981"

        # 3. Touch DNA Profiling
        elif "dna" in test_lower or "pcr" in test_lower:
            test_name = "16-LOCUS SHORT TANDEM REPEAT (STR) PCR AMPLIFICATION"
            lab_division = "Human Forensic Genomics Laboratory"
            specimen = f"Evidence Exhibit {evidence_id} (Epithelial Swab)"
            method = "Capillary Electrophoresis / GlobalFiler 16-Plex Amplification"
            findings = "Single-source male DNA profile recovered. Random match probability is 1 in 4.2 billion in the general population."
            match_rate = "1 IN 4.2 BILLION STATISTICAL CERTAINTY"
            admissibility = "COURT ADMISSIBLE // HIGHEST EVIDENTIARY GRADE"
            status_color = "#10b981"

        # 4. Digital Hash Audit
        else:
            test_name = "CRYPTOGRAPHIC DIGITAL LEDGER AUDIT & HASH VERIFICATION"
            lab_division = "Cyber Forensics & Digital Evidence Unit"
            specimen = f"Evidence Exhibit {evidence_id} (Hardware Controller Memory)"
            sha256_hash = hashlib.sha256(f"{case_id}-{evidence_id}-{time.time()}".encode()).hexdigest()
            method = f"SHA-256 Block Verification // Checksum: {sha256_hash[:16]}..."
            findings = "Electronic lock logs and timestamp headers verified authentic. No memory write buffer manipulation detected; record reflects authentic physical credential swipe."
            match_rate = "CRYPTOGRAPHICALLY VERIFIED (INTEGRITY INTACT)"
            admissibility = "COURT ADMISSIBLE // TAMPER-FREE DIGITAL AUDIT"
            status_color = "#38bdf8"

        summary = f"Forensic Lab Test Completed: {test_name} on {specimen}. Result: {match_rate}. Admissibility: {admissibility}."

        cert_html = f"""
<div class="forensic-cert-box" style="
    background: var(--nexus-bg-panel, #0b1120);
    border: 1px solid var(--nexus-border, #1e293b);
    border-top: 5px solid {status_color};
    border-radius: 8px;
    padding: 20px;
    margin: 18px 0;
    font-family: 'JetBrains Mono', monospace;
    color: var(--nexus-text-main, #f8fafc);
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
">
    <!-- Header -->
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--nexus-border, #1e293b); padding-bottom: 14px; margin-bottom: 18px;">
        <div>
            <div style="font-size: 0.75rem; letter-spacing: 0.15em; color: var(--nexus-text-dim, #94a3b8); text-transform: uppercase;">
                METROPOLITAN FORENSIC SCIENCE DIVISION // LAB RECORD
            </div>
            <div style="font-size: 1.35rem; font-weight: 800; color: var(--nexus-text-main, #f8fafc); margin-top: 4px;">
                OFFICIAL FORENSIC LABORATORY CERTIFICATE
            </div>
        </div>
        <div style="text-align: right;">
            <div style="background: var(--nexus-bg-subcard, #111a2e); border: 1px solid {status_color}; color: {status_color}; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">
                CERTIFIED EXHIBIT
            </div>
        </div>
    </div>

    <!-- Metadata Grid -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.85rem; margin-bottom: 18px; color: var(--nexus-text-main, #f8fafc);">
        <div><strong>CASE IDENTIFIER:</strong> <span style="color: var(--nexus-accent-amber, #fbbf24); font-weight: bold;">{case_id}</span></div>
        <div><strong>TEST TIMESTAMP:</strong> <span style="color: var(--nexus-text-muted, #cbd5e1);">{timestamp}</span></div>
        <div><strong>TESTING METHODOLOGY:</strong> <span style="color: var(--nexus-accent-blue, #38bdf8); font-weight: bold;">{test_name}</span></div>
        <div><strong>LABORATORY UNIT:</strong> <span style="color: var(--nexus-text-muted, #cbd5e1);">{lab_division}</span></div>
    </div>

    <!-- Specimen & Findings Box -->
    <div style="background: var(--nexus-bg-subcard, #080c16); border: 1px solid var(--nexus-border, #1e293b); border-radius: 6px; padding: 16px; margin-bottom: 18px; line-height: 1.5; font-size: 0.88rem; color: var(--nexus-text-main, #f8fafc);">
        <div style="color: var(--nexus-text-dim, #94a3b8); margin-bottom: 4px;"><strong>ANALYTICAL SPECIMEN:</strong> <span style="color: var(--nexus-text-main, #f8fafc);">{specimen}</span></div>
        <div style="color: var(--nexus-text-dim, #94a3b8); margin-bottom: 8px;"><strong>METHODOLOGY:</strong> <span style="color: var(--nexus-text-main, #f8fafc);">{method}</span></div>
        <div style="color: var(--nexus-text-main, #f8fafc); margin-bottom: 8px;"><strong>LABORATORY FINDINGS:</strong><br><span style="color: var(--nexus-text-main, #f8fafc);">{findings}</span></div>
        <div style="color: {status_color}; font-size: 1.05rem; font-weight: 800; margin-top: 10px;">
            VERIFICATION RESULT: {match_rate}
        </div>
    </div>

    <!-- Legal Certification Footer -->
    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: var(--nexus-text-dim, #94a3b8);">
        <div><strong>LEGAL ADMISSIBILITY:</strong> <span style="color: {status_color}; font-weight: bold;">{admissibility}</span></div>
        <div><em>Signed: Chief Forensic Toxicologist & Criminalist</em></div>
    </div>
</div>
"""
        return summary, cert_html
