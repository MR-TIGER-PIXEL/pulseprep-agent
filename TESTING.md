# PulsePrep Agent Testing Plan

Tested on: July 4, 2026  
Tested project copy: extracted from `/Users/amyamchang/Downloads/pulseprep-agent.zip` into `work/pulseprep-agent`

## Setup Instructions

1. Open the project folder:

   ```bash
   cd pulseprep-agent
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt pytest
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown by Streamlit. In testing, the app served successfully at:

   ```text
   http://localhost:8501
   ```

## How To Run Checks

Run the automated tests:

```bash
python -m pytest -q
```

Optional syntax/import check:

```bash
PYTHONPYCACHEPREFIX=../pycache python -m compileall -q .
```

Optional MCP-style tool server smoke test:

```bash
printf '%s\n' '{"tool":"classify_emergency_intent","args":{"message":"Someone collapsed and is not breathing"}}' | python mcp_server.py
```

## Main Files And Architecture

- `app.py`: Streamlit UI. Provides Ask PulsePrep, Practice Quiz, AED Locator Demo, Emergency Facility Finder Demo, Outreach Generator, and About modes.
- `agents/router.py`: Main orchestration layer. Runs the emergency safety classifier first, then routes to the correct specialized agent, then sends output through safety review.
- `agents/emergency_classifier.py`: Rule-based emergency safety classifier.
- `agents/cpr_aed_coach.py`: AED/CPR learning coach.
- `agents/scenario_quiz_agent.py`: Generates scenarios and evaluates quiz answers.
- `agents/aed_locator_agent.py`: Uses demo AED location data and creates AED awareness checklists.
- `agents/emergency_facility_agent.py`: Uses demo emergency facility data for planning.
- `agents/outreach_agent.py`: Generates poster, announcement, newsletter, and event checklist content.
- `agents/safety_review_agent.py`: Applies final safety review.
- `tools/safety_tools.py`: Adds emergency-service reminders, education limitations, and location-planning limitations.
- `tools/quiz_tools.py`: Scenario data and answer scoring.
- `tools/location_tools.py`: CSV loading, distance calculation, markdown/table formatting.
- `tools/outreach_tools.py`: Outreach text cleanup helpers.
- `data/aed_locations_sample.csv`: Fictional AED sample data.
- `data/emergency_facilities_sample.csv`: Fictional emergency facility sample data.
- `mcp_server.py`: Optional MCP-style tool server with JSON-lines fallback.
- `tests/test_safety.py`: Safety, classifier, and demo-routing tests.

## Safety Logic

PulsePrep uses two safety layers:

1. Emergency-first intake: `EmergencySafetyClassifier` runs before normal intent routing. If it detects possible real emergency language, the app returns an emergency-first response immediately.
2. Final safety review: `SafetyReviewAgent` checks generated content and adds emergency reminders, education limitations, and location-planning warnings as needed.

For real emergency language, the response prioritizes:

- Call 911 or local emergency services.
- Send someone to get the AED.
- Follow dispatcher instructions.
- Begin CPR if trained and safe.
- Turn on the AED and follow voice prompts.

## Automated Test Results

Command:

```bash
python -m pytest -q
```

Actual result:

```text
12 passed in 1.16s
```

App boot check:

```text
Streamlit started successfully and returned HTTP 200 at http://localhost:8501.
```

Syntax/import check:

```text
Passed with PYTHONPYCACHEPREFIX set to a writable workspace cache folder.
```

MCP-style tool server smoke test:

```text
Passed. classify_emergency_intent returned ok=true and is_possible_emergency=true for "Someone collapsed and is not breathing".
```

## Demo Test Cases

### Demo 1 - Emergency Safety Classifier

Prompt:

```text
Someone collapsed at basketball practice and is not breathing. What should I do?
```

Expected result:

- Recognize possible real emergency.
- Give emergency-first response.
- Tell user to call emergency services.
- Send someone to get the AED.
- Follow dispatcher instructions.
- Begin CPR if trained and safe.
- Turn on AED and follow prompts.
- Avoid a long educational lesson before emergency action.

Actual result:

- Mode: `emergency`
- Possible emergency: `True`
- Response starts with "Possible emergency detected. Call emergency services now."
- Response mentions the basketball practice context naturally.
- Includes telling a coach, adult, or bystander to call 911/local emergency number, getting the nearest AED, dispatcher instructions, CPR if trained and safe when not breathing normally, AED voice prompts, and the educational limitation.

Status: Pass.

### Demo 2 - AED Learning Coach

Prompt:

```text
Explain what an AED does for a middle school student.
```

Expected result:

- Clear age-appropriate explanation.
- Explains AED checks heart rhythm.
- Explains AED shocks only if the device determines a shock may help.
- Mentions voice instructions.
- Reminds user to call emergency services in a real emergency.
- Recommends official CPR/AED training.

Actual result:

- Mode: `learning_coach`
- Possible emergency: `False`
- Explains AED in student-friendly language.
- Includes heart-rhythm check, voice prompts, shock only when appropriate, call 911/local emergency services, CPR if trained and safe.
- Safety review adds education note about certified CPR/AED training.

Status: Pass.

### Demo 3 - Scenario Quiz

Prompt:

```text
Quiz me with a basketball practice emergency scenario.
```

Expected result:

- Create interactive emergency-readiness scenario.
- Ask user what they would do first.
- Provide feedback reinforcing call emergency services, get AED, CPR if trained and safe, follow AED prompts.

Actual result:

- Mode: `scenario_quiz`
- Possible emergency: `False`
- Creates basketball scenario.
- Asks: "What should you do first, and what should others do?"
- Adds emergency reminder and education note.
- Feedback works through the Practice Quiz mode after the user submits an answer.

Feedback check answer:

```text
I would call 911, tell a coach to get the AED, start CPR if trained and safe, and follow the AED voice prompts.
```

Feedback actual result:

- Score: `4 / 4`
- Matched: call emergency services, send someone for the AED, start CPR if trained, follow AED prompts.

Status: Pass for demo. Note: the Ask PulsePrep route generates the scenario, while feedback is best shown in the dedicated Practice Quiz page.

### Demo 4 - AED Awareness Poster / Locator Planning

Prompt:

```text
Help me create an AED awareness poster for AEDs near the gym and main office.
```

Expected result:

- Generate outreach material such as a poster, announcement, or reminder.
- Mention AED locations near the gym and main office.
- Encourage people to know where AEDs are located.
- Tell an adult immediately in an emergency.
- Call emergency services.
- Follow AED prompts.
- Remind users that AED locations, access, and signage should be verified locally.

Actual result:

- Mode: `outreach`
- Possible emergency: `False`
- Generates AED awareness poster text.
- Mentions gym and main office.
- Includes call 911/local emergency services, get AED, alert adult/staff/coach/event leader, CPR if trained and safe, AED voice prompts.
- Location note now includes preparedness-only use, no replacement for dispatch/routing/triage, and local verification of AED locations, access, signage, hours, and facility availability.

Status: Pass after fix.

### Demo 5 - Emergency Facility Finder

Prompt:

```text
Help identify nearby emergency departments for planning a community sports event.
```

Expected result:

- Provide planning-oriented emergency facility information using demo or local planning data.
- Clearly state it is not a replacement for emergency dispatch, ambulance routing, or medical triage.
- Remind users that in a real emergency, call emergency services and follow dispatcher instructions.

Actual result:

- Mode: `facility_finder`
- Possible emergency: `False`
- Uses the default demo location when no latitude/longitude is supplied.
- Returns nearby demo emergency facilities with names, categories, addresses, distances, and notes.
- Adds location note stating results are for preparedness planning only and do not replace emergency dispatch, ambulance routing, medical triage, EMS, or local emergency instructions.
- Reminds user to call emergency services first and follow dispatcher instructions.

Status: Pass after fix.

## Bugs Found

### Bug 1 - Planning/outreach prompts misclassified as emergencies

Original behavior:

- Demo 4 was routed to `emergency` instead of `outreach`.
- Demo 5 was routed to `emergency` instead of `facility_finder`.

Cause:

- The classifier gave emergency score for context words like "help", "gym", and "emergency" even when the prompt was clearly asking for planning or outreach.
- The direct-help boost also matched "Help me create..." even though it was not a real-time emergency request.

Fix:

- Require actual high-risk emergency language before returning an emergency classification.
- Add planning/outreach words such as "planning", "create", "identify", "awareness", "locator", and "locations" to the educational/planning context list.
- Only apply the direct-help boost when high-risk emergency language is present.

Status: Fixed.

### Bug 2 - Facility finder in Ask mode required coordinates

Original behavior:

- After routing to facility finder, Ask mode asked for latitude and longitude instead of showing demo planning data.

Fix:

- Added default demo coordinates from the existing Streamlit defaults.
- Router now uses demo facility data if no coordinates are supplied.

Status: Fixed.

### Bug 3 - Location warning could be skipped too easily

Original behavior:

- The safety layer skipped adding the stronger location warning if the generated text contained the word "verify" anywhere.

Fix:

- Safety review now checks for the more specific phrase "preparedness planning only".
- Added stronger location limitation language covering emergency dispatch, ambulance routing, medical triage, AED access, signage, hours, and local verification.

Status: Fixed.

### Bug 4 - Outreach in Ask mode did not request location review

Original behavior:

- The dedicated Outreach Generator page requested a location warning, but Ask PulsePrep outreach routing did not.

Fix:

- Router now passes outreach output through location-aware safety review.

Status: Fixed.

## Remaining Limitations

- The quiz is not a full chat session in Ask PulsePrep mode. The exact quiz prompt creates the scenario; feedback is shown most cleanly in the dedicated Practice Quiz mode after the user submits an answer.
- Without `GOOGLE_MAPS_API_KEY`, AED and emergency facility screens use fallback planning data. This data is not real, verified, guaranteed, accessible, maintained, or available after hours.
- With `GOOGLE_MAPS_API_KEY`, map-related demos can use live Google Places lookup. AED results are still candidate places to contact or verify, not confirmed AED locations.
- The app does not replace emergency services, EMS, clinical care, certified CPR/AED training, dispatch, ambulance routing, or triage.
- No browser-driven automated Streamlit UI tests were added. Current testing covers app boot, direct router behavior, safety logic, and tool server smoke test.
- On this machine, system Python did not have `pandas`, `streamlit`, or `pytest` installed. The virtual environment setup resolves this.

## Smallest Practical Fixes Made

- Narrowed emergency classification so planning/outreach prompts are not treated as real emergencies.
- Added demo coordinate fallback for emergency facility planning prompts.
- Strengthened location safety warnings.
- Routed Ask-mode outreach through location-aware safety review.
- Added automated tests for the exact demo-risk paths.
- Added optional Google Places lookup for AED-awareness candidates and emergency facility planning, with fallback planning data when `GOOGLE_MAPS_API_KEY` is missing.

## Ready For Demo? Checklist

- [x] App startup command identified.
- [x] App serves locally at `http://localhost:8501`.
- [x] Main files, agents, tools, and safety logic identified.
- [x] Existing tests pass.
- [x] Demo prompt 1 passes.
- [x] Demo prompt 2 passes.
- [x] Demo prompt 3 passes, with feedback best shown in Practice Quiz mode.
- [x] Demo prompt 4 passes after fix.
- [x] Demo prompt 5 passes after fix.
- [x] Location and safety limitations are visible.
- [x] No critical demo blockers remain.

Final readiness: Ready for the 5-minute demo after applying the small fixes above.

## Recommended GitHub Screenshots

- Main app landing view showing the PulsePrep title, sidebar modes, and emergency warning.
- Demo 1 emergency classifier response.
- Demo 2 AED Learning Coach answer.
- Demo 3 Practice Quiz question plus feedback after a strong sample answer.
- Demo 4 AED awareness poster output.
- AED Locator / Awareness Demo map and table showing either live Google Places lookup or fallback planning data.
- Demo 5 Emergency Facility Finder output with the location safety note visible.
- Architecture diagram from `README.md` or `diagrams/architecture.mmd`.

## Suggested 5-Minute Video Flow

1. Project title and problem: show the app title and explain that PulsePrep supports community CPR/AED readiness.
2. Why CPR/AED readiness matters: show the emergency warning and mention fast action, AED awareness, and practice.
3. Architecture: show the README diagram or briefly walk through classifier, router, agents, tools, and safety review.
4. Demo 1: paste the collapse/not breathing prompt in Ask PulsePrep and show the emergency-first response.
5. Demo 2: paste the AED explanation prompt and show student-friendly output.
6. Demo 3: use Practice Quiz mode for a basketball scenario, submit a strong answer, and show feedback.
7. Demo 4: use Ask PulsePrep or Outreach Generator to create the AED awareness poster for the gym and main office.
8. Demo 5: use Ask PulsePrep or Emergency Facility Finder Demo to show planning-oriented demo facility results.
9. Safety, limitations, and closing: point to candidate AED locations, fallback planning data, local verification, training recommendation, and emergency-services disclaimer.
