from tools.outreach_tools import normalize_audience, clean_locations


class OutreachMaterialGenerator:
    """Generates reusable community CPR/AED awareness materials."""

    def morning_announcement(self, audience: str = "middle school students", locations: str = "main office and gym") -> str:
        audience = normalize_audience(audience)
        locations = clean_locations(locations)
        return f"""
## School Morning Announcement

Good morning. Today’s safety reminder is about AED awareness. An AED is a device that can help during certain heart emergencies by checking the heart rhythm and giving voice instructions.

Our AED locations include: **{locations}**.

If you ever see someone collapse or not respond, tell an adult immediately, call emergency services, and send someone to get the AED. In a real emergency, every second matters.

This reminder is for **{audience}** and is meant to build awareness, not replace CPR/AED training.
""".strip()

    def poster_text(self, locations: str = "main office and gym") -> str:
        locations = clean_locations(locations)
        return f"""
## AED Awareness Poster Text

# Know Where the AED Is

AED locations to verify:
**{locations}**

If someone collapses and is not breathing normally:

1. Call 911 or local emergency services.
2. Send someone to get the AED.
3. Alert an adult, staff member, coach, or event leader.
4. Start CPR if trained and safe.
5. Turn on the AED and follow the voice prompts.

AEDs are designed to guide users step by step.
""".strip()

    def newsletter_blurb(self, audience: str = "families", locations: str = "main office and gym") -> str:
        audience = normalize_audience(audience)
        locations = clean_locations(locations)
        return f"""
## Newsletter Blurb

This month, we are encouraging CPR/AED awareness for {audience}. AEDs are emergency devices that can help during certain life-threatening heart rhythm events. They provide voice prompts and analyze the heart rhythm before advising a shock.

Please take a moment to learn where AEDs are located in our building. Current AED locations to verify include: **{locations}**.

In a real emergency, call 911 or local emergency services immediately, send someone to get the AED, and follow dispatcher and AED instructions.
""".strip()

    def event_checklist(self, event_name: str = "community sports event", locations: str = "gym entrance") -> str:
        locations = clean_locations(locations)
        return f"""
## Emergency Readiness Checklist: {event_name}

Before the event:

- Confirm AED locations: **{locations}**.
- Confirm building access to AEDs during the event.
- Identify who will call emergency services if needed.
- Identify who will retrieve the AED.
- Know the exact event address for emergency dispatch.
- Confirm where emergency responders should enter.
- Encourage coaches, staff, and volunteers to complete official CPR/AED training.

During a real emergency:

- Call emergency services immediately.
- Send someone to get the AED.
- Follow dispatcher instructions.
- Begin CPR if trained and safe.
- Turn on the AED and follow voice prompts.
""".strip()

    def create_material(self, material_type: str, audience: str, locations: str, event_name: str = "community event") -> str:
        kind = (material_type or "announcement").lower()
        if "poster" in kind:
            return self.poster_text(locations)
        if "newsletter" in kind or "blurb" in kind:
            return self.newsletter_blurb(audience, locations)
        if "event" in kind or "checklist" in kind:
            return self.event_checklist(event_name, locations)
        return self.morning_announcement(audience, locations)
