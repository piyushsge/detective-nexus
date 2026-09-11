"""
Detective Nexus Audio Dispatch & Voice Debrief Engine
Generates authentic forensic audio briefings and Chief Investigator debriefs using pure Python.
Supports zero-latency offline Windows SAPI, cross-platform gTTS, and procedural WAV fallback.
"""

import os
from pathlib import Path
from typing import Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIO_DIR = (PROJECT_ROOT / "data" / "audio").resolve()

class AudioDebriefEngine:
    """
    Synthesizes speech debriefings for active cases.
    Produces audio files ready for immediate playback in Gradio gr.Audio.
    """

    @classmethod
    def generate_briefing_audio(cls, case_title: str, incident_desc: str, critical_window: str) -> Tuple[bool, str]:
        """Generates police radio dispatch briefing audio."""
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        out_base = AUDIO_DIR / "dispatch_briefing"

        script = (
            f"Attention all investigative units. Incident alert for {case_title}. "
            f"A critical opportunity window occurred during the power outage from {critical_window}. "
            f"Summary of incident report: {incident_desc[:250]}. "
            "All units report to the Command Center. Multi-agent forensic investigation is now active."
        )

        return cls._synthesize_audio(script, out_base)

    @classmethod
    def generate_chief_verdict_audio(cls, leading_suspect: str, caveat: str) -> Tuple[bool, str]:
        """Generates classified Chief Investigator audio debrief."""
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        out_base = AUDIO_DIR / "chief_verdict_debrief"

        script = (
            f"This is the Chief Investigator with the official classified case debrief. "
            f"Based on current electronic logs and fiber evidence, the provisional leading suspect is {leading_suspect}. "
            f"However, notice this critical caveat: {caveat[:200]}. "
            "Under no circumstances is this lead to be treated as formal legal proof without verified touch DNA and fiber spectrometry."
        )

        return cls._synthesize_audio(script, out_base)

    @classmethod
    def generate_case_report_voice_summary(cls, raw_text: str, scorecard: dict) -> Tuple[bool, str]:
        """
        Generates spoken audio briefing of an uploaded user report and its scorecard evaluation.
        Summarizes case facts, solvability score, grade, and critical gaps.
        """
        import time
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        out_base = AUDIO_DIR / f"report_voice_debrief_{timestamp}"

        score = scorecard.get("overall_score", 50)
        grade = scorecard.get("grade", "GRADE C").split("//")[0].strip()
        summary = scorecard.get("verdict_summary", "Case review completed.")
        
        # Extract first key sentence or topic of the report
        lines = [l.strip() for l in raw_text.splitlines() if l.strip() and not l.strip().startswith("#")]
        first_line = lines[0] if lines else "Uploaded case document"
        if len(first_line) > 120:
            first_line = first_line[:120]

        vulnerabilities = scorecard.get("vulnerabilities", [])
        vuln_text = vulnerabilities[0] if vulnerabilities else "Verify physical evidence chain of custody."

        script = (
            f"Forensic Case Analysis and Spoken Audio Debrief. "
            f"Regarding case file: {first_line}. "
            f"The Solvability Index has been calculated at {score} out of 100, receiving {grade}. "
            f"Prosecutorial assessment: {summary}. "
            f"Critical evidentiary notice: {vuln_text}. "
            f"Multi-agent investigation is prepared for immediate dispatch."
        )

        return cls._synthesize_audio(script, out_base)

    @classmethod
    def _synthesize_audio(cls, text: str, out_base: Path) -> Tuple[bool, str]:
        """
        Synthesizes speech into an audio file with instant hash-based caching.
        Priority 1: Check existing cached audio file (instant 0.00s latency).
        Priority 2: Native Windows SAPI (instant, 100% offline).
        Priority 3: Google TTS (gTTS) MP3.
        Priority 4: Procedural sine wave WAV tone.
        """
        import hashlib
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        text_hash = hashlib.md5(text.strip().encode("utf-8")).hexdigest()[:12]
        
        # Check fast-cache on disk
        cached_wav = AUDIO_DIR / f"{out_base.stem}_{text_hash}.wav"
        cached_mp3 = AUDIO_DIR / f"{out_base.stem}_{text_hash}.mp3"
        if cached_wav.exists() and cached_wav.stat().st_size > 500:
            return True, str(cached_wav.resolve().as_posix())
        if cached_mp3.exists() and cached_mp3.stat().st_size > 500:
            return True, str(cached_mp3.resolve().as_posix())

        target_wav = cached_wav
        target_mp3 = cached_mp3

        # 1. Try Windows SAPI (instant, offline)
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(str(target_wav.resolve()), 3) # 3 = SSFMCreateForWrite
            speaker.AudioOutputStream = stream
            speaker.Speak(text)
            stream.Close()
            return True, str(target_wav.resolve().as_posix())
        except Exception:
            pass

        # 2. Try gTTS (online MP3)
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang="en", tld="com", slow=False)
            tts.save(str(target_mp3.resolve()))
            return True, str(target_mp3.resolve().as_posix())
        except Exception:
            pass

        # 3. Fallback: create procedural synthesized tone WAV
        try:
            import wave
            import math
            import struct
            with wave.open(str(target_wav.resolve()), "w") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                for i in range(44100):
                    val = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * (i / 44100.0)) * 0.1)
                    wav_file.writeframes(struct.pack("<h", val))
            return True, str(target_wav.resolve().as_posix())
        except Exception as e3:
            return False, f"Audio synthesis error: {str(e3)}"

