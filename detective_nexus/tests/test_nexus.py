import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from detective_nexus.core.case_engine import get_case_engine
from detective_nexus.agents.detective import DetectiveAgent
from detective_nexus.agents.evidence import EvidenceAgent
from detective_nexus.agents.suspect import SuspectAgent
from detective_nexus.agents.skeptic import SkepticAgent
from detective_nexus.agents.chief import ChiefAgent
from detective_nexus.core.confidence import calculate_nexus_quality_score
from detective_nexus.core.validation import HallucinationAuditor

class TestDetectiveNexus(unittest.TestCase):

    def setUp(self):
        self.engine = get_case_engine()
        self.case_data = self.engine.get_agent_visible_data()

    def test_case_loading(self):
        case = self.engine.get_current_case()
        self.assertEqual(case.case_id, "CASE-001")
        self.assertEqual(len(case.suspects), 4)
        self.assertEqual(len(case.evidence), 7)
        self.assertIn("08:20 PM", case.critical_window)

    def test_secret_separation(self):
        self.assertNotIn("hidden_solution", self.case_data)
        self.assertNotIn("culprit", self.case_data)

    def test_detective_agent(self):
        agent = DetectiveAgent()
        report = agent.run(self.case_data)
        self.assertIsNotNone(report)
        self.assertIn("08:20 PM - 08:24 PM", report.critical_time_window)

    def test_evidence_agent(self):
        agent = EvidenceAgent()
        report = agent.run(self.case_data)
        self.assertEqual(len(report.evidence_table), 7)

    def test_suspect_agent(self):
        agent = SuspectAgent()
        report = agent.run(self.case_data)
        self.assertEqual(report.provisional_lead, "Arjun Vale")

    def test_skeptic_agent(self):
        agent = SkepticAgent()
        report = agent.run(self.case_data)
        self.assertTrue(len(report.assumptions_exposed) >= 3)
        self.assertTrue(len(report.alternative_theories) >= 1)

    def test_chief_agent(self):
        agent = ChiefAgent()
        report = agent.run(self.case_data)
        self.assertIn("NOT PROVEN", report.not_proven_caveat)
        self.assertEqual(report.confidence_level, "MODERATE")

    def test_quality_score(self):
        score = calculate_nexus_quality_score(6, 4, 3, 4, 2)
        self.assertTrue(70 <= score["overall"] <= 100)

    def test_hallucination_auditor(self):
        clean_text = "Evidence B and Evidence E-E establish proximity at 8:23 PM."
        valid, warnings = HallucinationAuditor.audit_report(clean_text)
        self.assertTrue(valid)
        self.assertEqual(len(warnings), 0)

        hallucinated_text = "Evidence E-Z proves that Arjun confessed to Dr. Mira Sen."
        valid, warnings = HallucinationAuditor.audit_report(hallucinated_text)
        self.assertFalse(valid)
        self.assertTrue(len(warnings) >= 2)

    def test_scorecard_engine(self):
        from detective_nexus.core.scorecard import ForensicScorecardEngine
        sample_doc = "Homicide in server room. Suspect Arjun Vale was seen at 8:23 PM. Missing keycard B. DNA sample found."
        card = ForensicScorecardEngine.evaluate_case_report(sample_doc, self.case_data)
        self.assertTrue(0 <= card["overall_score"] <= 100)
        self.assertIn("GRADE", card["grade"])
        html = ForensicScorecardEngine.render_html_scorecard(card, is_dark_mode=True)
        self.assertIn("SOLVABILITY INDEX", html)

    def test_interrogation_engine(self):
        from detective_nexus.core.interrogation import InterrogationEngine
        reply, telemetry, gauge_html = InterrogationEngine.interrogate_suspect(
            suspect_name="Arjun Vale",
            user_question="Where were you at 8:23 PM?",
            chat_history=[],
            confront_evidence_item="E-B: Keycard Log",
            case_data=self.case_data
        )
        self.assertTrue(len(reply) > 0)
        self.assertTrue(0 <= telemetry["stress_score"] <= 100)
        self.assertIn("BIOMETRIC STRESS MONITOR", gauge_html)

    def test_audio_debrief_engine(self):
        from detective_nexus.core.audio_debrief import AudioDebriefEngine
        ok, path = AudioDebriefEngine.generate_briefing_audio(
            case_title="The Stolen Aurora Diamond",
            incident_desc="Vault breach at 8:23 PM",
            critical_window="08:20 PM - 08:24 PM"
        )
        self.assertTrue(ok)
        self.assertTrue(Path(path).exists())

        # Test case report voice summary synthesis
        from detective_nexus.core.scorecard import ForensicScorecardEngine
        sc = ForensicScorecardEngine.evaluate_case_report("Robbery reported in train coach B2")
        ok_report, report_path = AudioDebriefEngine.generate_case_report_voice_summary("Robbery in train coach B2", sc)
        self.assertTrue(ok_report)
        self.assertTrue(Path(report_path).exists())

    def test_procedural_generator(self):
        from detective_nexus.core.procedural_generator import ProceduralCaseGenerator
        ok, case, msg = ProceduralCaseGenerator.generate_mystery_case(
            genre="Cyber & Tech Heist",
            difficulty="Mastermind",
            num_suspects=4,
            num_evidence=6
        )
        self.assertTrue(ok)
        self.assertTrue(case["case_id"].startswith("CASE-PROC-"))
        self.assertGreaterEqual(len(case["suspects"]), 3)
        self.assertGreaterEqual(len(case["evidence"]), 4)


    def test_forensic_lab_engine(self):
        from detective_nexus.core.forensic_lab import ForensicLabEngine
        badge_html, cert_html = ForensicLabEngine.run_lab_test(
            evidence_id="E-B",
            test_type="Automated Fingerprint Identification System (AFIS)",
            case_context=self.case_data
        )
        self.assertIn("OFFICIAL FORENSIC LABORATORY CERTIFICATE", cert_html)
        self.assertIn("AFIS", cert_html)

    def test_courtroom_trial_engine(self):
        from detective_nexus.core.courtroom import CourtroomTrialEngine
        transcript, verdict_banner, jury_metrics = CourtroomTrialEngine.conduct_trial(
            indicted_suspect="Arjun Vale",
            case_data=self.case_data,
            has_lab_certificate=False
        )
        self.assertIn("TRIAL PROCEEDINGS", transcript)
        self.assertIn("VERDICT", verdict_banner)
        self.assertEqual(jury_metrics["guilty_votes"] + jury_metrics["not_guilty_votes"], 12)

    def test_visual_evidence_graph(self):
        from detective_nexus.core.visual_graph import VisualEvidenceGraph
        svg = VisualEvidenceGraph.generate_svg_graph(self.case_data, is_dark_mode=True)
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)

    def test_user_profile_and_history(self):
        from detective_nexus.core.user_profile import UserProfileManager
        import time
        uname = f"test_officer_{int(time.time() * 1000)}"
        ok, msg, profile = UserProfileManager.register_officer(
            username=uname,
            password="test_password_123",
            officer_name="Inspector Test",
            badge_id="BADGE-TEST-01"
        )
        self.assertTrue(ok)
        self.assertEqual(profile["officer_name"], "Inspector Test")

        # Authenticate
        auth_ok, auth_msg, auth_profile = UserProfileManager.authenticate(uname, "test_password_123")
        self.assertTrue(auth_ok)

        # Log case to history
        log_ok = UserProfileManager.log_case_to_user_history(
            username=uname,
            case_title="Vault Break-in",
            report_category="High-Security Asset Theft",
            score=82,
            grade="GRADE B+",
            summary="Keycard log correlates with window."
        )
        self.assertTrue(log_ok)
        history = UserProfileManager.get_user_history(uname)
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[0]["case_title"], "Vault Break-in")

    def test_report_classifier(self):
        from detective_nexus.core.report_classifier import ReportClassifier
        fir_text = "Standard Operating Procedure for lodging FIR in running train via RPF/GRP."
        res = ReportClassifier.classify_report(fir_text)
        self.assertTrue(any(w in res["category"].lower() for w in ["transit", "railway", "train"]))
        self.assertTrue(any(w in res["subject"].lower() for w in ["railway", "train", "fir", "operating procedure", "running train"]))


    def test_dossier_exporter(self):
        from detective_nexus.core.dossier_exporter import DossierExporter
        from pathlib import Path
        path = DossierExporter.export_case_dossier(
            case_title="Test Theft Dossier",
            category="Burglary",
            raw_narrative="Vault breach reported at 03:00 AM.",
            scorecard={"overall_score": 75, "grade": "GRADE B"},
            agent_analysis="Agent findings: Keycard logged."
        )
        self.assertTrue(Path(path).exists())

if __name__ == "__main__":
    unittest.main()



