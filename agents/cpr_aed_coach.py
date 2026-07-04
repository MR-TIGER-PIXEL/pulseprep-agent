from typing import Dict


class CPRAEDLearningCoach:
    """Creates audience-adapted CPR/AED educational explanations."""

    AUDIENCE_STYLE: Dict[str, str] = {
        "elementary student": "Use very simple words and short sentences.",
        "middle school student": "Use clear, student-friendly language with a calm tone.",
        "high school student": "Use clear language with a little more detail.",
        "parent": "Use practical family-oriented language.",
        "teacher": "Use classroom-ready language.",
        "coach": "Use sports-practice and event-readiness language.",
        "workplace team": "Use workplace safety language.",
        "community volunteer": "Use public-facing community education language.",
    }

    def explain_aed(self, audience: str = "middle school student") -> str:
        style = self.AUDIENCE_STYLE.get(audience, self.AUDIENCE_STYLE["middle school student"])
        return f"""
## What an AED Does

Audience: **{audience}**  
Style guide: {style}

An **AED**, or automated external defibrillator, is a device that can help during certain life-threatening heart rhythm emergencies.

Key points:

1. An AED checks the heart rhythm.
2. It gives voice prompts so a bystander can follow step by step.
3. It only advises a shock if the device detects a rhythm that may be helped by a shock.
4. It does not shock everyone.
5. Someone should call 911 or local emergency services immediately while another person gets the AED.
6. If you are trained and it is safe, start CPR while waiting for the AED and emergency responders.

Simple way to remember: **Call. Push. Shock if instructed.**
""".strip()

    def explain_cpr(self, audience: str = "middle school student") -> str:
        style = self.AUDIENCE_STYLE.get(audience, self.AUDIENCE_STYLE["middle school student"])
        return f"""
## CPR Basics

Audience: **{audience}**  
Style guide: {style}

CPR stands for **cardiopulmonary resuscitation**. It is used when someone is unresponsive and not breathing normally.

Basic readiness steps:

1. Check if the person responds.
2. Call 911 or local emergency services immediately.
3. Send someone to get the AED.
4. If you are trained and it is safe, begin chest compressions.
5. When the AED arrives, turn it on and follow the voice prompts.
6. Continue following dispatcher and AED instructions until help arrives.

PulsePrep can help you practice the sequence, but official CPR/AED training is still recommended.
""".strip()

    def create_lesson(self, topic: str, audience: str = "middle school student") -> str:
        topic_lower = (topic or "").lower()
        if "aed" in topic_lower:
            return self.explain_aed(audience)
        if "cpr" in topic_lower:
            return self.explain_cpr(audience)
        return f"""
## CPR/AED Readiness Mini-Lesson

Audience: **{audience}**

During a possible cardiac emergency, the first steps matter:

1. **Call emergency services.** Do this immediately.
2. **Get the AED.** Send someone else if possible.
3. **Start CPR if trained and safe.** Chest compressions help keep blood moving.
4. **Use the AED when it arrives.** Turn it on and follow the voice prompts.
5. **Keep going until help arrives.** Follow dispatcher and AED instructions.

An AED is designed to guide users. It checks the heart rhythm and only advises a shock when appropriate.
""".strip()
