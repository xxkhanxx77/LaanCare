# EMS LINE Check-in Simulator

เว็บ UI และ backend สำหรับจำลอง LINE check-in bot ที่ใช้เอกสาร EMS Markdown ใน `Symptoms/` เป็น knowledge source สำหรับคัดกรองความเสี่ยงเบื้องต้นแบบ `red` / `yellow` / `green` เท่านั้น

ระบบนี้ไม่ได้ทำ diagnosis และไม่ได้ให้คำแนะนำการรักษา จุดประสงค์คือช่วย engineer เห็น end-to-end flow ของ LINE webhook, RAG retrieval, short-term/long-term memory, state machine, Gemini token modes, debug logs, และ caregiver alert simulation

## Scope

ระบบทำได้:

- ถาม check-in ประจำวัน
- รับรายงานอาการผิดปกติจากผู้ใช้
- เลือก EMS symptom group จาก Markdown ใน `Symptoms/`
- รองรับหลายกลุ่มอาการในข้อความเดียว เช่น `ปวดท้องและหายใจขัด`
- รวม red flags เป็นคำถามเดียวพร้อมปุ่ม flex message `ใช่` / `ไม่ใช่`
- ถ้าเข้า `red` ให้หยุดถามและจำลอง caregiver alert ทันที
- ถ้าเข้า `yellow` ให้ถาม yellow ให้ครบก่อน แล้วค่อยจำลอง caregiver alert
- ถ้าไม่เข้า `red` หรือ `yellow` ให้บันทึกเป็น `green` เมื่อมี source ที่รองรับ
- เก็บ chat log, observations, alerts, session state, LLM usage และ memory ลง SQLite
- แสดง `Knowledge Retrieved`, console event, API call count และ token usage ให้ engineer debug

ระบบห้ามทำ:

- ห้ามวินิจฉัยโรค
- ห้ามตอบว่าผู้ใช้เป็นโรคอะไร
- ห้ามตอบคำถามสุขภาพทั่วไป
- ห้ามแนะนำยา การรักษา หรือการปฐมพยาบาล
- ห้ามสร้างเกณฑ์ `red` / `yellow` / `green` เอง
- ห้ามใช้ความรู้แพทย์นอก `Symptoms/*.md`
- ห้ามถามคำถามที่ถูก skip สำหรับ `self_checkin`
- ห้ามเปิดเผยข้อมูลผู้ป่วยให้ caregiver ที่ไม่ได้ผูกหรือไม่มี consent

ข้อความปฏิเสธคำถามสุขภาพทั่วไป:

```text
ระบบนี้ใช้สำหรับเช็กอินอาการผิดปกติและแจ้งเตือนเท่านั้น ไม่สามารถตอบคำถามสุขภาพหรือวินิจฉัยอาการได้
```

## Project Layout

```text
.
├─ app/
│  ├─ server.py          # HTTP API, web static serving, LINE webhook simulation
│  ├─ engine.py          # Main state machine and screening logic
│  ├─ ems_loader.py      # Loads Symptoms/*.md and builds deterministic retrieval
│  ├─ db.py              # SQLite storage via sqlite3 CLI
│  ├─ gemini_client.py   # Gemini JSON API wrapper and usage accounting
│  └─ env.py             # .env loader
├─ web/
│  ├─ index.html         # Simulator UI
│  ├─ app.js             # Chat, flex buttons, console, memory, knowledge panel
│  └─ styles.css
├─ Symptoms/
│  ├─ symptom_index.md
│  ├─ symptom_group_01.md
│  ├─ ...
│  └─ symptom_group_25.md
├─ prompts/
│  └─ system_prompt.md   # Safety and runtime LLM prompt
├─ data/
│  └─ chatbot.sqlite3    # Created at runtime
├─ .env
├─ .env.example
└─ README.md
```

Notes:

- `Symptoms/` is the only clinical knowledge source used for risk criteria.
- `EMS11` is intentionally not selected by backend validation because group 11 is empty in the extracted set.
- Supplemental questions such as pain score and vomiting count are stored as observation only. They do not create new risk criteria.

## Run

Install/runtime assumptions:

- Python available as `python`
- `sqlite3` CLI available in `PATH`
- Optional Gemini API key in `.env`

Run server:

```powershell
python -m app.server
```

Open:

```text
http://127.0.0.1:8000
```

Example `.env`:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_DISABLED=0
CHATBOT_DB=data/chatbot.sqlite3
HOST=127.0.0.1
PORT=8000
```

If `GEMINI_API_KEY` is empty or `GEMINI_DISABLED=1`, the system still works with deterministic Markdown retrieval and local answer interpretation.

## UI Panels

The web simulator has four important areas:

- Chat panel: simulates LINE user/bot messages.
- Alert panel: shows simulated caregiver alert chat.
- Console log: shows backend events, API calls, token usage, selected groups, rule IDs, and state transitions.
- Knowledge Retrieved: shows the exact Markdown-derived context used in the latest turn.

The UI does not call LINE. It posts to local endpoints and renders LINE-like flex messages with buttons.

## API Overview

### Health

```http
GET /api/health
```

Returns DB path, Gemini status, model, and number of EMS groups loaded.

### Bootstrap

```http
GET /api/bootstrap?user_id=U_DEMO
```

Loads user profile, active session, alerts, Gemini status, and group count.

### Save User Profile

```http
POST /api/users
Content-Type: application/json

{
  "user_id": "U_DEMO",
  "display_name": "Demo User",
  "caregiver_user_id": "CAREGIVER_DEMO",
  "consent_to_share": true,
  "personalized_prompt": "",
  "config": {
    "daily_summary": true,
    "line_simulation": true,
    "llm_retrieval_assist": false,
    "llm_first": false,
    "llm_group_selection": false,
    "llm_session_summary": false
  }
}
```

### Web Chat

```http
POST /api/chat
Content-Type: application/json

{
  "user_id": "U_DEMO",
  "text": "ปวดหัว เวียนหัว",
  "session_mode": "self_checkin",
  "user_can_chat": true
}
```

Response shape:

```json
{
  "reply_messages": [],
  "alert_messages": [],
  "ui_messages": [],
  "state": {},
  "knowledge_retrieved": {},
  "debug": {
    "events": [],
    "api_calls_delta": 0,
    "token_delta": {},
    "session_llm_totals": {}
  }
}
```

### Simulated LINE Webhook

```http
POST /api/line/webhook
Content-Type: application/json

{
  "events": [
    {
      "type": "message",
      "source": { "userId": "U_DEMO" },
      "message": { "type": "text", "text": "เช็กอิน" }
    }
  ],
  "session_mode": "self_checkin",
  "user_can_chat": true
}
```

This endpoint adapts LINE-style events into the same `engine.handle_message()` flow used by `/api/chat`.

## LINE Application Considerations

The current app is a simulator. It intentionally keeps LINE transport separate from screening logic so the same backend can be used by:

- local web UI
- simulated LINE webhook
- future real LINE Messaging API webhook
- future scheduled daily check-in job

### Production LINE Adapter Boundary

Keep the production boundary like this:

```text
LINE webhook event
  -> transport adapter
  -> ChatEngine.handle_message()
  -> backend response contract
  -> LINE message renderer
  -> reply message or push message
```

`ChatEngine` should not depend on LINE SDK objects directly. It should receive normalized input:

```json
{
  "user_id": "LINE source.userId",
  "text": "message text or postback data text",
  "session_mode": "self_checkin",
  "user_can_chat": true,
  "raw_payload": {
    "channel": "line_webhook",
    "payload": "original LINE event"
  }
}
```

The renderer should convert backend output into LINE messages:

| Backend field | LINE production behavior |
|---|---|
| `reply_messages` | Send as LINE text messages to the current user. |
| `ui_messages.template = red_bundle_confirm` | Render as Flex Message or button template with `ใช่` / `ไม่ใช่`. |
| `ui_messages.template = choice_buttons` | Render as Flex Message or quick reply choices. |
| `ui_messages.template = scale_0_10` | Render as Flex Message or quick replies for `0` to `10`. |
| `ui_messages.template = history_button` | Render as button/postback carrying `/history <session_id>`. |
| `alert_messages` | Push message to linked caregiver if consent is valid. |
| `debug` and `knowledge_retrieved` | Do not send to LINE users; keep for engineer console/logs. |

### LINE Webhook Event Handling

The simulator currently supports text message events:

```json
{
  "events": [
    {
      "type": "message",
      "source": { "userId": "U_DEMO" },
      "message": { "type": "text", "text": "หายใจขัด" }
    }
  ]
}
```

For a real LINE app, the adapter should also handle:

- `message` events with text
- `postback` events from Flex buttons
- repeated deliveries or retries idempotently where possible
- missing or unsupported message types with a short fallback text

Recommended postback payload style:

```json
{
  "action": "answer",
  "text": "ใช่",
  "session_id": 123,
  "source": "red_bundle"
}
```

The adapter can pass `text` into `handle_message()` and keep the structured postback in `raw_payload`.

### Reply vs Push

Use reply messages for the active user turn:

- normal bot text
- red bundle flex
- yellow questions
- detail buttons
- history button

Use push messages for caregiver alerts:

- final `red`
- final `yellow`

The simulator represents caregiver push as `alert_messages`. A production adapter should convert each delivered alert into a push message to `caregiver_user_id`.

Do not push if:

- `caregiver_user_id` is empty
- `consent_to_share = false`
- caregiver is not linked/verified

### Patient-facing Copy in LINE

The patient-facing LINE messages intentionally hide internal rule IDs.

For `red`:

```text
ประเมินความรุนแรงระดับสีแดงจากข้อมูลที่ตอบ
แนะนำให้ไปโรงพยาบาลทันที หรือโทร 1669 หากต้องการความช่วยเหลือฉุกเฉิน
ระบบส่งแจ้งเตือนไปยังผู้ดูแลแล้ว
กดปุ่มด้านล่างเพื่อดูประวัติที่ระบบซักถาม
```

For `yellow`:

```text
ประเมินความรุนแรงระดับสีเหลืองจากข้อมูลที่ตอบ
แนะนำให้ไปโรงพยาบาลเพื่อประเมินเพิ่มเติม
ระบบส่งแจ้งเตือนไปยังผู้ดูแลแล้ว
กดปุ่มด้านล่างเพื่อดูประวัติที่ระบบซักถาม
```

For `green`:

```text
บันทึกแล้ว: ประเมินความรุนแรงระดับสีเขียวจากข้อมูลที่ตอบ
ยังไม่พบเกณฑ์แจ้งเตือนแดงหรือเหลืองจากชุดคำถามนี้
ระบบจะรอส่งรายงานประจำวันให้ผู้ดูแลตาม config
```

Internal `rule_id`, `source_ref`, and Markdown excerpts remain available in:

- `knowledge_retrieved`
- `debug.events`
- caregiver alert message
- SQLite `observations`
- SQLite `alerts`

### LINE Privacy Notes

For a real LINE application:

- Treat `source.userId` as the primary external user key.
- Do not expose one user's session history to another user ID.
- The `/history <session_id>` command checks session ownership before returning history.
- Do not send `knowledge_retrieved` or raw debug logs to LINE users.
- Keep caregiver linkage and consent in `users`.
- Avoid putting unnecessary clinical details in broadcast messages.
- Store raw LINE payloads only for engineering/audit needs and apply the project's data retention policy.

### LINE Daily Check-in Scheduling

The current app supports daily check-in text flow but does not include a scheduler.

Production options:

- A cron/job worker sends a daily push to users who enabled check-in.
- The push text can be `วันนี้มีอาการผิดปกติไหม?` with buttons `มี` / `ไม่มี`.
- Button payloads should call the same `handle_message()` flow with `pending_rule_id = DAILY_ABNORMAL`.
- If the user answers `ไม่มี`, session closes as `green`.
- If the user answers `มี`, ask for the main abnormal symptom.

### LINE Message Length and UX

Keep LINE messages short:

- Ask 1-2 questions per turn.
- Use buttons for red yes/no and structured details.
- Use open-ended text for yellow screening.
- Use history button for longer detail instead of sending all history automatically.
- Avoid repeating what the user already said; auto-match handles common synonyms such as `เวียนหัว` and `เวียนศีรษะ`.

### Memory

```http
GET /api/memory?user_id=U_DEMO
```

Returns:

- `previous_sessions`: closed session summaries for long-term memory
- `recent_chat`: recent short-term chat log for current session
- `alerts`: recent simulated caregiver alerts
- `llm_stats`: token and call totals for current session

### Reset

```http
POST /api/reset
Content-Type: application/json

{ "user_id": "U_DEMO" }
```

Closes the active session and starts a new one.

## Data Model

SQLite path defaults to:

```text
data/chatbot.sqlite3
```

Tables:

- `users`: user profile, caregiver link, consent, personalized prompt, per-user config toggles
- `sessions`: current/previous session state, short conclusion, long conclusion, summary status
- `chat_logs`: every raw user and assistant message
- `observations`: structured clinical observations and rule-answer events
- `alerts`: simulated caregiver alert messages and delivery/block status
- `llm_calls`: Gemini request/response excerpts and token usage

Important `sessions.state_json` keys:

```json
{
  "active_group_id": "EMS12",
  "active_group_ids": ["EMS12"],
  "risk_level": "insufficient",
  "asked_rule_ids": [],
  "pending_rule_id": "",
  "pending_question": "",
  "observations": [],
  "matched_rules": [],
  "skip_questions": [],
  "red_bundle_done": false,
  "red_bundle_rule_ids": [],
  "yellow_done": false,
  "yellow_rule_ids": [],
  "yellow_current_rule_ids": [],
  "yellow_answers": {},
  "auto_matched_rule_ids": [],
  "yellow_detail_questions": [],
  "yellow_details": {},
  "pending_detail_key": "",
  "flow_phase": "",
  "session_mode": "self_checkin",
  "user_can_chat": true
}
```

## Memory Design

Short-term memory:

- Current open session state in `sessions.state_json`
- Recent chat from `chat_logs`
- Observations in `state.observations` and `observations` table
- Pending question/rule state so the bot remembers what it already asked

Long-term memory:

- Closed sessions in `sessions`
- `short_conclusion` is always generated locally at close
- `long_conclusion` is generated by Gemini only when `llm_session_summary=true`
- Previous summaries are loaded at the start of each message and can be passed to Gemini when LLM modes are enabled

The local deterministic screening logic does not depend on long-term memory for risk criteria. Memory is for context, personalization, and engineering visibility.

## Gemini Token Modes

Gemini is never called just because an API key exists. Calls are controlled per user by UI toggles stored in `users.config_json`.

If the UI shows `Gemini: disabled - GEMINI_API_KEY is missing`, no real API call can happen. Create `.env` from `.env.example`, set `GEMINI_API_KEY`, keep `GEMINI_DISABLED=0`, and restart the server.

### `llm_retrieval_assist`

Label in UI: `LLM retrieval assist`

This mode lets Gemini help only with the retrieval topic, not risk decisions.

When enabled, Gemini receives:

- current message
- symptom index
- deterministic candidates
- recent chat
- previous session summaries
- personalized prompt

Gemini returns:

- `retrieval_topics`: short Thai topic phrases suitable for Markdown retrieval
- `query_terms`: aliases/synonyms to expand deterministic retrieval
- `candidate_group_ids`: optional EMS group IDs from `symptom_index.md`
- confidence and backend reason

Backend validation rules:

- Returned group IDs must exist in `symptom_index.md`.
- `EMS11` is still excluded.
- Retrieval assist never sets `risk_level`.
- Retrieval assist never provides matched rule IDs.
- Red/yellow/green still come only from Markdown rules after the retrieved group is selected.
- If confidence is low, backend ignores the assisted topics.

Example:

```text
User: เหนื่อยมากเหมือนหายใจไม่สุด
Gemini retrieval assist:
  retrieval_topics = ["หายใจยากลำบาก"]
  query_terms = ["หายใจไม่อิ่ม", "หายใจลำบาก", "เหนื่อยหอบ"]
  candidate_group_ids = ["EMS05"]
Backend:
  deterministic retrieval runs again with expanded terms
  selected group is validated against Symptoms markdown
```

Use this when the user uses natural wording that may not exactly match extracted Markdown keywords.

### `llm_first`

Label in UI: `LLM fallback + answer interpretation`

When enabled, Gemini receives:

- current message
- session state
- active group Markdown excerpt if any
- deterministic candidates
- candidate group rules or all group rule index
- symptom index
- recent chat
- previous session summaries
- personalized prompt

Gemini may propose:

- intent
- normalized yes/no answer
- candidate group IDs
- exact matched rule IDs
- next questions mapped to exact rule IDs
- short natural prefix

Backend validation rules:

- Any matched rule ID must exist in the supplied Markdown-derived group/rule context.
- Gemini cannot create new criteria.
- If no exact rule ID is accepted, risk remains `insufficient`.
- Gemini questions are rejected if they do not map to an exact rule ID.
- Natural prefix must not contain diagnosis, advice, or extra medical questions.

### `llm_group_selection`

Label in UI: `LLM symptom selector (multi)`

When enabled, Gemini can select multiple EMS groups from `symptom_index.md`.
Even when this toggle is off, the backend will still call Gemini for group selection if deterministic retrieval cannot select any group and Gemini is enabled. This is the "unknown symptom fallback" path, used for messages such as `ไข้ หนาวสั่น` where exact extracted keywords may not match well enough.

Use case:

```text
ปวดท้องและหายใจขัด
```

Possible selected groups:

```text
EMS01 + EMS05
```

Backend still validates:

- group ID must exist in corpus
- `EMS11` is excluded
- max selected groups are capped
- group selection does not decide risk by itself

### `llm_session_summary`

When enabled, Gemini is called only when the session closes to generate long-term memory:

- `short_conclusion`
- `long_conclusion`

The summary instruction says no diagnosis.

## Knowledge Retrieval

The engine uses `EmsCorpus` to load:

- `symptom_index.md`
- `symptom_group_01.md` to `symptom_group_25.md`
- group metadata
- keywords
- rules
- question bank
- Markdown excerpts

Deterministic retrieval:

1. Score user text against group names, aliases, keywords, and Markdown-derived terms.
2. Return ranked candidates with `group_id`, score, and reasons.
3. Remove duplicated candidate groups when one candidate's reasons are a subset of another selected group.
4. Select up to 3 distinct groups.

Retrieval also has a small local synonym/fuzzy layer for common LINE wording. This does not create new risk rules; it only helps select the closest Markdown group before rule-based screening starts.

Examples mapped to `EMS05 หายใจยากลำบาก`:

- `เหนื่อย`
- `เหนื่อยง่าย`
- `หอบ`
- `หายใจเหนื่อย`
- `หายใจไม่ทัน`
- `หายใจไม่ออก`
- `หายใจไม่สะดวก`
- `หายใจติด`

After group selection, red/yellow/green still come only from the selected group's Markdown rules.

If `llm_retrieval_assist=true`, Gemini can add extra retrieval topics and query terms before the final candidate list is chosen. This is useful when the user wording is understandable but does not match the extracted Markdown terms exactly. The backend still re-runs deterministic retrieval against `Symptoms/` and validates every candidate group ID.

Multi-group active group:

- If one group is selected, `active_group_id = EMSxx`.
- If multiple groups are selected, `active_group_id = EMS05+EMS01`.
- The engine builds a combined in-memory group with unioned rules, question bank, keywords, and Markdown excerpts.
- Rule dedupe prevents asking the same concept repeatedly across groups.

## Knowledge Retrieved Panel

Every `/api/chat` response includes `knowledge_retrieved`.

Fields:

- `selected_group`: active single or combined group
- `selected_groups`: component groups when multi-group
- `candidate_groups`: deterministic retrieval candidates, including assisted candidates when `llm_retrieval_assist=true`
- `retrieval_assist`: Gemini retrieval topics/query terms and merged candidate data, shown only for engineering debug
- `active_rules`: red/yellow/green rules touched in this turn
- `question_bank`: first question-bank entries from active group
- `detail_questions`: supplemental observation questions planned/asked
- `markdown_excerpt`: short source excerpt for engineer debugging

This panel is for debugging RAG behavior. It is not shown as patient-facing clinical advice.

## State Machine

High-level phases:

```text
empty/new session
  -> daily_checkin
  -> group_selection
  -> red_bundle
  -> yellow_open
  -> yellow_details
  -> complete
```

Important `pending_rule_id` values:

- `DAILY_ABNORMAL`: waiting for daily check-in yes/no
- `RED_BUNDLE`: waiting for red flex button answer
- `YELLOW_SUMMARY`: waiting for open-ended yellow answer covering 1-2 rules
- exact rule ID such as `EMS12_YELLOW_04`: legacy/direct question state
- empty string: no pending rule

Important `flow_phase` values:

- `daily_checkin`: user started with `เช็กอิน`
- `red_bundle`: red bundle question is active
- `yellow_open`: open-ended yellow screening is active
- `yellow_details`: supplemental observation question is active
- `complete`: session is finalized

Topic shift behavior:

- If the user gives a new symptom while answering an open yellow/detail question, the engine checks deterministic retrieval again.
- If the new text maps to a different EMS group, the flow switches focus to that new group and returns to red bundle first.
- Example: while the current question came from headache flow, user says `หายใจเหนื่อย`; backend switches focus to `EMS05` and asks breathing red flags.
- The previous context remains in observations, but patient-facing questions continue from the new active symptom so old pain questions do not leak into the breathing flow.

## Main Chat Flow

For every user message:

1. Load or create `users` row.
2. Load or create active `sessions` row.
3. Decode `state_json`.
4. Load previous session summaries for long-term memory.
5. Load recent chat for short-term memory.
6. Append user chat log.
7. Block general health questions with the refusal message.
8. Handle commands such as `/reset` and `/help`.
9. Route by pending state:
   - red bundle answer
   - yellow detail answer
   - yellow open answer
   - daily check-in answer
   - ordinary symptom report
10. Save assistant response and updated state.
11. Return messages, UI flex messages, alert messages, knowledge snapshot, and debug events.

## Daily Check-in Flow

User starts:

```text
เช็กอิน
```

Backend state:

```json
{
  "pending_rule_id": "DAILY_ABNORMAL",
  "flow_phase": "daily_checkin"
}
```

Bot asks:

```text
วันนี้มีอาการผิดปกติไหม?
ตัวเลือก: มี / ไม่มี
```

If user answers `ไม่มี`:

- risk becomes `green`
- observation is saved as daily check-in no abnormal symptom
- session closes
- no alert is sent

If user answers `มี`:

- bot asks for the main abnormal symptom
- group selection starts after the user describes symptoms

## Symptom Group Selection

When the user reports a symptom directly:

```text
ปวดหัว เวียนหัว
```

The engine:

1. Runs deterministic retrieval against `Symptoms/`.
2. Calls Gemini group selection if `llm_group_selection=true`, or if deterministic retrieval cannot select a group and Gemini is enabled.
3. Validates selected groups.
4. Excludes `EMS11`.
5. Stores:

```json
{
  "active_group_ids": ["EMS12"],
  "active_group_id": "EMS12",
  "observations": [
    {
      "main_symptom_text": "ปวดหัว เวียนหัว",
      "group_ids": ["EMS12"]
    }
  ]
}
```

For multiple symptoms:

```text
ปวดท้องและหายใจขัด
```

Possible state:

```json
{
  "active_group_ids": ["EMS01", "EMS05"],
  "active_group_id": "EMS01+EMS05"
}
```

The combined group is only an internal runtime wrapper. It does not create new Markdown criteria.

## Red Flow

After group selection, red is always checked before yellow.

The engine:

1. Loads red rules from active group or combined groups.
2. Applies self-check-in skip rules.
3. Dedupes overlapping red concepts.
4. Builds one bundled question.
5. Sends a simulated LINE flex message with `ใช่` / `ไม่ใช่`.

Example:

```text
ขอเช็กอาการแจ้งเตือนแดงก่อน
ตอนนี้มีข้อใดข้อหนึ่งต่อไปนี้ไหม?
- หายใจลำบากมากหรือพูดได้แค่สั้น ๆ
- มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติ
- ปวดหัวรุนแรงทันทีร่วมกับตามัว พูดพร่า อ่อนแรง หรืออาเจียน
กดปุ่ม: ใช่ / ไม่ใช่
```

If user answers `ใช่`:

- `risk_level = red`
- create bundle rule such as `EMS12_RED_BUNDLE`
- append matched rule
- record observation
- create caregiver alert if caregiver ID and consent are present
- close session
- stop asking
- show a `ดูประวัติที่ซักถาม` button that sends `/history <session_id>`

Patient-facing red response example:

```text
ประเมินความรุนแรงระดับสีแดงจากข้อมูลที่ตอบ
แนะนำให้ไปโรงพยาบาลทันที หรือโทร 1669 หากต้องการความช่วยเหลือฉุกเฉิน
ระบบส่งแจ้งเตือนไปยังผู้ดูแลแล้ว
กดปุ่มด้านล่างเพื่อดูประวัติที่ระบบซักถาม
```

If user answers `ไม่ใช่`:

- mark `red_bundle_done = true`
- record red denial observation
- continue to yellow flow

Red bundle does not call Gemini.

## Skip Rules

For:

```json
{
  "session_mode": "self_checkin",
  "user_can_chat": true
}
```

The engine skips questions that assume the user cannot answer for themselves, such as:

- not conscious
- not responding
- actively seizing
- cannot answer simple questions

For:

```json
{
  "session_mode": "caregiver_report"
}
```

Questions about response/consciousness may be allowed if they exist in Markdown.

Skipped rule IDs are stored in:

```json
{
  "skip_questions": []
}
```

## Yellow Flow

Yellow starts only after red is denied or no red rule exists.

The engine:

1. Loads yellow rules from active group or combined groups.
2. Removes yellow rules duplicated by already checked red concepts.
3. Removes self-check-in detail-uncertainty rules.
4. Removes context-unrelated rules.
5. Dedupes overlapping yellow concepts across groups.
6. Auto-matches yellow conditions already clearly mentioned by the user.
7. Asks remaining yellow questions in batches of 1-2 topics.

Yellow questions are open-ended and do not show buttons. This is intentional so Gemini/local evaluation can interpret natural replies when configured.

Example after `ปวดหัว เวียนหัว` and red = `ไม่ใช่`:

```text
ขอเช็กต่ออีกนิดนะ อาการปวดหัว เวียนหัวครั้งนี้มีสับสนแต่ยังพูดและเดินได้ไหม และมองเห็นลำบากไหม
```

The engine does not ask:

```text
อาการปวดหัว เวียนหัวครั้งนี้มีเวียนศีรษะไหม
```

because `เวียนหัว` is already auto-matched to `EMS12_YELLOW_04`.

## Yellow Auto-match

Purpose:

- avoid repeated questions
- respect what the user already said
- keep flow more natural

Examples:

| User text | Markdown condition | Result |
|---|---|---|
| `เวียนหัว` | `เวียนศีรษะ` | auto-match yellow |
| `ปวดหัว` | `ปวดศีรษะ` | treated as same symptom phrase |
| `มีอาเจียนด้วย` | `อาเจียน` | can match related yellow condition |
| `ปวดท้อง อาเจียน` | `ปวดร่วมกับอาเจียน` | auto-match if both pain and vomiting are present |
| `ไม่มีเวียนหัว` | `เวียนศีรษะ` | not auto-matched because negated |

Current synonym normalization includes:

- `เวียนหัว`, `หัวหมุน`, `มึนหัว` -> `เวียนศีรษะ`
- `ปวดหัว` -> `ปวดศีรษะ`
- `อ้วก` -> `อาเจียน`
- `หายใจลำบาก`, `หายใจเหนื่อย`, `หายใจไม่ทัน`, `หายใจไม่ออก`, `หอบ`, `เหนื่อยหอบ` -> `หายใจขัด`
- `ตามัว`, `มองไม่ชัด`, `เห็นภาพซ้อน` -> `มองเห็นลำบาก`
- `เจ็บหน้าอก`, `แน่นหน้าอก` -> `เจ็บแน่นทรวงอก`

Auto-match is conservative:

- It only maps to existing yellow rule IDs.
- It records an observation with `type = yellow_context_auto_match`.
- It does not invent new rules.
- It is not used for diagnosis.

## Yellow Answer Evaluation

When the user answers a yellow open-ended question:

1. Explicit `ใช่` / `ไม่ใช่` is interpreted locally.
2. If `llm_first=true`, Gemini can interpret open-ended answers.
3. Gemini output must map to exact supplied rule IDs.
4. If Gemini confidence is too low or rule ID is invalid, the answer is treated as unknown/not matched.
5. Local fallback checks rule keywords and normalized symptom text.

Each answer is stored in:

```json
{
  "yellow_answers": {
    "EMS12_YELLOW_04": {
      "answer": "ปวดหัว เวียนหัว",
      "matched": true,
      "normalized_answer": "yes",
      "confidence": 0.8,
      "reason_for_backend": "user already mentioned this yellow condition before follow-up: dizziness",
      "source_ref": "PDF p.44-45, Module 12, code 12เหลือง5"
    }
  }
}
```

Yellow alert is deferred until all relevant yellow questions and supplemental details are complete.

Patient-facing yellow response after all checks and details are complete:

```text
ประเมินความรุนแรงระดับสีเหลืองจากข้อมูลที่ตอบ
แนะนำให้ไปโรงพยาบาลเพื่อประเมินเพิ่มเติม
ระบบส่งแจ้งเตือนไปยังผู้ดูแลแล้ว
กดปุ่มด้านล่างเพื่อดูประวัติที่ระบบซักถาม
```

The patient-facing message intentionally does not show internal `Rule: EMS...` lines. Rule IDs and source refs remain available in the caregiver alert, `Knowledge Retrieved`, and debug logs.

## Supplemental Detail Flow

Before finalizing yellow or green, the engine asks supplemental observation questions.

These questions are not new risk rules. They are context details for caregiver/backend.

Examples:

- onset from Question Bank: `เริ่มปวดหัวตั้งแต่เมื่อไหร่?`
- vomiting count: `อาเจียนประมาณกี่ครั้งตั้งแต่เริ่มมีอาการ?`
- pain location when not already clear
- pain score 0-10

Pain score flex message:

```text
ตอนนี้ปวดท้องประมาณกี่คะแนน (0-10)?
0 = ไม่ปวดเลย
5 = ปวดพอทนไหว
10 = ปวดมากที่สุดในชีวิต
```

Stored as:

```json
{
  "yellow_details": {
    "pain_score": {
      "type": "scale_0_10",
      "answer": "6",
      "value": 6,
      "note": "supplemental observation only; not a new risk rule"
    }
  }
}
```

If a detail can be inferred from the user's text, it is prefilled and not asked again.

Example:

- User says `ปวดท้อง`
- `pain_location = ท้อง` can be inferred
- bot does not ask `ปวดตรงไหนเป็นหลัก?`

Pain score guard:

- Pain score is asked only when the latest active symptom or matched rule is pain-related.
- If the latest active symptom is breathing-focused, such as `หายใจเหนื่อย`, `เหนื่อย`, or `หอบ`, the engine does not ask `ระดับปวดหัว` just because an older topic in the same session mentioned headache.
- Onset still applies as a general supplemental observation, so breathing flow may ask `เริ่มมีอาการหายใจเหนื่อยตั้งแต่เมื่อไหร่?`.

## Green Flow

Green is reached when:

- red bundle is denied
- all relevant yellow rules are asked or skipped
- no yellow rule matched

The engine:

- sets `risk_level = green`
- records observation
- uses a sourced green rule if the active group has one
- otherwise cites that red/yellow rules were asked from EMS Markdown
- closes session

Green response example:

```text
บันทึกแล้ว: ประเมินความรุนแรงระดับสีเขียวจากข้อมูลที่ตอบ
ยังไม่พบเกณฑ์แจ้งเตือนแดงหรือเหลืองจากชุดคำถามนี้
ระบบจะรอส่งรายงานประจำวันให้ผู้ดูแลตาม config
```

If no sourced green rule exists and the engine cannot safely infer green, it returns `insufficient`.

## Alert Flow

Alerts are simulated as another chat panel, not sent to a real LINE account.

Alert is created only when:

- risk is `red` or final `yellow`
- user has `caregiver_user_id`
- `consent_to_share = true`

If caregiver or consent is missing:

- alert is stored as blocked
- `blocked_reason = missing linked caregiver or consent`

Alert message includes:

- user ID
- risk level
- group ID and group name
- rule ID
- latest answer
- source references
- supplemental details if any
- note that this is check-in alert, not diagnosis

For `red` and final `yellow`, the user also receives a flex button:

```json
{
  "type": "flex",
  "template": "history_button",
  "title": "ประวัติการซักถาม",
  "body": "กดเพื่อดูคำถามและคำตอบที่ระบบเก็บไว้ในรอบนี้",
  "actions": [
    { "label": "ดูประวัติที่ซักถาม", "text": "/history 123" }
  ]
}
```

The session may already be closed when the user presses the button, so the button includes the completed `session_id`.

## Screening History Command

The history button calls:

```text
/history <session_id>
```

The command returns a patient-readable summary:

- symptom originally reported
- latest color level
- red bundle answer
- yellow questions/answers that were asked or auto-matched
- supplemental observations such as onset, vomiting count, pain location, and pain score

It does not diagnose. It is a check-in history only.

## Deduplication Logic

The engine dedupes rules so the user does not get repeated questions.

Risk-family dedupe groups include:

- `breathing`: หายใจขัด, พูดได้แค่สั้น ๆ, นั่งพิง
- `shock`: เหงื่อ, ซีด, เกือบหมดสติ, อ่อนแรงมาก
- `uncontrolled_bleeding`: เลือดห้ามไม่หยุด
- `consciousness`: หมดสติ, ไม่รู้สึกตัว, ไม่ตอบสนอง
- `age_pain`: อายุ + ปวดท้อง/หลัง/ยอดอก

If a yellow rule duplicates a red concept already checked in the red bundle, it is skipped.

Example:

- Red asks severe breathing difficulty.
- Yellow has `หายใจขัด`.
- If the overlap key is considered the same family, redundant yellow asking is skipped.

## Question Style Rules

Patient-facing wording should be:

- short
- LINE-friendly
- one to two questions at a time
- no diagnosis
- no medical advice
- no `คุณเป็นโรค...`
- no `วินิจฉัยว่า...`
- no rigid fallback like `ถ้าไม่มีข้อพวกนี้ พิมพ์ว่า ไม่มี`
- use buttons only for yes/no red confirmation and structured details like choices/scale
- open-ended yellow questions should not have buttons

Preferred wording:

```text
ขอเช็กต่ออีกนิดนะ อาการปวดท้องครั้งนี้มีอาเจียนร่วมด้วยไหม
```

Avoid:

```text
ช่วยเล่าเพิ่มสั้น ๆ เรื่องปวดท้อง: ปวดร่วมกับอาเจียน
ถ้าไม่มีข้อพวกนี้ พิมพ์ว่า ไม่มี
```

## Example Flows

### Example 1: Headache + Dizziness

User:

```text
ปวดหัว เวียนหัว
```

Backend:

- selects `EMS12`
- asks red bundle
- no Gemini call required

User:

```text
ไม่ใช่
```

Backend:

- marks red bundle clear
- auto-matches `EMS12_YELLOW_04` because `เวียนหัว` = `เวียนศีรษะ`
- does not ask duplicate dizziness question
- asks remaining relevant yellow topics

Expected debug:

```text
flow.yellow.context_match
auto_matched_rule_ids: ["EMS12_YELLOW_04"]
```

### Example 2: Abdominal Pain + Vomiting

User:

```text
ปวดท้อง
```

Backend:

- selects abdominal pain group
- asks red bundle first

User:

```text
ไม่ใช่
```

Backend:

- asks yellow open question about vomiting if relevant

User:

```text
มีอาเจียนด้วย
```

Backend:

- matches yellow rule from Markdown
- continues asking remaining yellow checks
- then asks details such as vomiting count, onset, and pain score
- sends yellow alert only after details are collected

### Example 3: Bleeding Arm

User:

```text
เลือดออกที่แขน
```

Backend:

- selects bleeding group
- asks red bundle first
- if red denied, avoids unrelated nosebleed follow-up unless context mentions nose/nosebleed
- asks contextual bleeding follow-up instead

### Example 4: Multi-group Symptom

User:

```text
ปวดท้องและหายใจขัด
```

Backend:

- deterministic or Gemini group selection can select multiple groups
- creates combined active group such as `EMS01+EMS05`
- dedupes overlapping red/yellow rules
- asks one red bundle for combined red rules
- proceeds to yellow only after red denied

## Debug Events

Common event kinds in console:

- `db.user`: user profile loaded
- `memory.long_term`: previous summaries loaded
- `memory.short_term`: recent chat loaded
- `ems.retrieve`: deterministic retrieval candidates
- `ems.groups_selected`: active group IDs selected
- `llm_first.skip`: Gemini-first disabled or unavailable
- `llm_first.result`: Gemini-first result accepted for validation
- `llm.retrieval_assist`: Gemini suggested retrieval topics/query terms
- `ems.retrieve.assisted`: assisted retrieval topics were merged into candidates
- `llm.group_selection`: Gemini selected group IDs
- `flow.red_bundle.ask`: red flex question sent
- `flow.red_bundle.clear`: user denied red flags
- `flow.red_bundle.alert`: user confirmed red flags
- `flow.yellow.context_match`: yellow rule auto-matched from prior user text
- `flow.yellow.ask`: yellow open-ended batch asked
- `flow.yellow.answer`: yellow answer evaluated
- `flow.yellow.detail.ask`: supplemental detail asked
- `flow.yellow.detail.answer`: supplemental detail recorded
- `flow.yellow.alert`: yellow alert sent after complete checks
- `flow.green`: completed green screening
- `safety.refusal`: general health question blocked

Use these events to verify why the bot asked a question or skipped one.

## Runtime Output Contract

Runtime LLM-facing contract should stay compatible with the Markdown files:

```json
{
  "group_id": "EMS12",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```

Backend response contract is broader:

```json
{
  "reply_messages": ["patient-facing text"],
  "ui_messages": [
    {
      "type": "flex",
      "template": "red_bundle_confirm | choice_buttons | scale_0_10 | history_button",
      "title": "string",
      "body": "string",
      "actions": [{ "label": "ใช่", "text": "ใช่" }],
      "metadata": {}
    }
  ],
  "alert_messages": [
    {
      "to": "CAREGIVER_DEMO",
      "delivered": true,
      "blocked_reason": "",
      "message": "simulated caregiver alert"
    }
  ],
  "state": {},
  "knowledge_retrieved": {},
  "debug": {}
}
```

## Safety Boundary

The safety boundary is enforced at multiple layers:

- `prompts/system_prompt.md` instructs LLM not to diagnose or invent criteria.
- `engine.py` blocks general health questions locally.
- Red/yellow/green requires Markdown rule IDs.
- Gemini suggestions are validated against loaded rules.
- Invalid rule IDs are rejected.
- Supplemental details are labeled observation only.
- Alerts say they are check-in alerts, not diagnosis.

The allowed wording is:

```text
ประเมินความรุนแรงระดับสีแดง/สีเหลือง/สีเขียวจากข้อมูลที่ตอบ
เข้าเกณฑ์แจ้งเตือน
```

Avoid:

```text
คุณเป็นโรค...
วินิจฉัยว่า...
ควรกินยา...
ควรรักษา...
```

## Development Notes

### Flow Verification Matrix

Last local smoke check: `2026-05-08`, backend at `http://127.0.0.1:8000`, Gemini disabled.

All checked flows completed with `debug.api_calls_delta = 0`.

| Flow | Input path | Expected result | Checked |
|---|---|---|---|
| General health refusal | `/api/chat` with `ควรกินยาอะไรดี?` | Refusal text, no diagnosis/advice, risk remains `insufficient`. | Pass |
| Daily green | `เช็กอิน` -> `ไม่มี` | Patient-facing green copy and closed session. | Pass |
| Direct red alert | `ปวดหัว เวียนหัว` -> red bundle `ใช่` | Patient-facing red copy, caregiver alert, `history_button`. | Pass |
| Yellow full flow | `ปวดหัว เวียนหัว` -> red `ไม่ใช่` -> yellow/details complete | Patient-facing yellow copy, caregiver alert after details, `history_button`. | Pass |
| History after closed session | Press `ดูประวัติที่ซักถาม` | `/history <session_id>` returns owned session's screening history. | Pass |
| Multi-group selection | `ปวดท้องและหายใจขัด` | Selects multiple groups such as `EMS05, EMS01`, asks one red bundle. | Pass |
| LINE webhook simulation | `/api/line/webhook` with text event `หายใจขัด` | One event result with red bundle flex message. | Pass |

Smoke test script shape:

```powershell
function PostJson($path, $obj) {
  Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000$path" `
    -ContentType 'application/json; charset=utf-8' `
    -Body ($obj | ConvertTo-Json -Depth 20)
}

$user = 'U_SMOKE'
PostJson '/api/chat' @{ user_id=$user; text='ปวดหัว เวียนหัว'; session_mode='self_checkin'; user_can_chat=$true }
PostJson '/api/chat' @{ user_id=$user; text='ไม่ใช่'; session_mode='self_checkin'; user_can_chat=$true }
```

Compile check:

```powershell
python -m py_compile app\engine.py app\db.py app\server.py app\gemini_client.py app\ems_loader.py
```

Restart local server on port 8000:

```powershell
$ErrorActionPreference='SilentlyContinue'
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -match 'python' -and $_.CommandLine -match 'app.server' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 1
Start-Process -FilePath python -ArgumentList @('-B','-m','app.server') -WorkingDirectory (Get-Location) -WindowStyle Hidden
Start-Sleep -Seconds 2
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/health | ConvertTo-Json -Depth 4
```

Manual smoke test:

```powershell
$user = 'U_SMOKE'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/reset `
  -ContentType 'application/json; charset=utf-8' `
  -Body (@{ user_id=$user } | ConvertTo-Json)

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType 'application/json; charset=utf-8' `
  -Body (@{ user_id=$user; text='ปวดหัว เวียนหัว'; session_mode='self_checkin'; user_can_chat=$true } | ConvertTo-Json)

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType 'application/json; charset=utf-8' `
  -Body (@{ user_id=$user; text='ไม่ใช่'; session_mode='self_checkin'; user_can_chat=$true } | ConvertTo-Json)
```

Expected:

- first response contains red flex message
- second response does not ask duplicate dizziness question
- state contains `auto_matched_rule_ids` with `EMS12_YELLOW_04`
- `debug.api_calls_delta` is `0` unless an LLM toggle is enabled

## Current Design Tradeoffs

- The system is optimized for check-in screening, not free medical conversation.
- Yellow flow intentionally asks all relevant yellow checks before final alert so caregiver gets richer context.
- Red is intentionally rigid and button-based to avoid ambiguity.
- Yellow is intentionally open-ended to feel more natural and avoid yes/no fatigue.
- Gemini can make language and selection more flexible, but backend remains the source of truth.
- SQLite uses the `sqlite3` CLI adapter in `app/db.py` because the local Python SQLite binding may be unstable in this environment.
