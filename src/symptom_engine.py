import json
import re
from pathlib import Path

try:
    from .symptom_db import utc_now
except ImportError:
    from symptom_db import utc_now


REFUSAL = "ระบบนี้ใช้สำหรับเช็กอินอาการผิดปกติและแจ้งเตือนเท่านั้น ไม่สามารถตอบคำถามสุขภาพหรือวินิจฉัยอาการได้"


def load_system_prompt():
    path = Path(__file__).resolve().parent / "symptom_system_prompt.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "EMS check-in risk screening only. Do not diagnose."


class ChatEngine:
    def __init__(self, db, corpus, llm):
        self.db = db
        self.corpus = corpus
        self.llm = llm
        self.system_prompt = load_system_prompt()

    def handle_message(self, user_id, text, session_mode="self_checkin", user_can_chat=True, raw_payload=None):
        console = []
        usage_delta = {"api_calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        text = (text or "").strip()
        user = self.db.get_or_create_user(user_id)
        console.append(self._event("db.user", "loaded user profile", {"user_id": user_id}))
        session = self.db.get_or_start_session(user_id, session_mode)
        state = self._state(session)
        state["session_mode"] = session_mode
        state["user_can_chat"] = bool(user_can_chat)
        previous = self.db.previous_summaries(user_id, limit=6)
        recent = self.db.recent_chat(session["session_id"], limit=12)
        console.append(self._event("memory.long_term", "loaded previous session summaries", {"count": len(previous)}))
        console.append(self._event("memory.short_term", "loaded recent session chat", {"count": len(recent)}))
        self.db.append_chat(session["session_id"], user_id, "user", text, raw_payload or {"channel": "web"})
        llm_first = None

        if not text:
            reply = "กรุณาพิมพ์อาการหรือพิมพ์ “เช็กอิน”"
            self._save_assistant(session, user_id, reply, state)
            return self._result([reply], [], state, console, usage_delta, session["session_id"])

        command_reply = self._handle_command(text, session, user_id, state, console)
        if command_reply:
            return self._result([command_reply], [], state, console, usage_delta, session["session_id"])

        if self._is_general_health_question(text):
            console.append(self._event("safety.refusal", "blocked general health question", {"text": text[:80]}))
            self._save_assistant(session, user_id, REFUSAL, state)
            return self._result([REFUSAL], [], state, console, usage_delta, session["session_id"])

        if self._is_checkin_start(text):
            state.update(
                {
                    "active_group_id": "",
                    "active_group_ids": [],
                    "risk_level": "insufficient",
                    "pending_rule_id": "DAILY_ABNORMAL",
                    "pending_question": "วันนี้มีอาการผิดปกติไหม?",
                    "asked_rule_ids": [],
                    "matched_rules": [],
                    "red_bundle_done": False,
                    "yellow_done": False,
                    "yellow_answers": {},
                    "yellow_current_rule_ids": [],
                    "yellow_detail_questions": [],
                    "yellow_details": {},
                    "pending_detail_key": "",
                    "flow_phase": "daily_checkin",
                }
            )
            reply = "วันนี้มีอาการผิดปกติไหม?\nตัวเลือก: มี / ไม่มี"
            self._save_assistant(session, user_id, reply, state)
            console.append(self._event("flow.checkin", "started daily check-in", {}))
            return self._result([reply], [], state, console, usage_delta, session["session_id"])

        if state.get("pending_rule_id") == "RED_BUNDLE":
            llm_first = self._llm_first(
                text=text,
                user=user,
                session=session,
                state=state,
                previous=previous,
                recent=recent,
                console=console,
                usage_delta=usage_delta,
            )
            return self._handle_red_bundle_answer(user, session, user_id, text, state, console, usage_delta, llm_first)

        if state.get("flow_phase") == "yellow_details" and state.get("pending_detail_key"):
            return self._handle_yellow_detail_answer(user, session, user_id, text, state, console, usage_delta)

        if state.get("flow_phase") == "yellow_open" and state.get("pending_rule_id"):
            llm_first = self._llm_first(
                text=text,
                user=user,
                session=session,
                state=state,
                previous=previous,
                recent=recent,
                console=console,
                usage_delta=usage_delta,
            )
            return self._handle_yellow_open_answer(user, session, user_id, text, state, console, usage_delta, llm_first)

        if state.get("pending_rule_id") == "DAILY_ABNORMAL":
            if self._is_no(text):
                state["risk_level"] = "green"
                state["pending_rule_id"] = ""
                state["pending_question"] = ""
                state["flow_phase"] = "complete"
                observation = {"type": "daily_checkin", "answer": "no_abnormal_symptom"}
                self.db.record_observation(session["session_id"], user_id, "", "green", observation)
                reply = self._patient_risk_reply("green")
                self._close_with_summary(session, user_id, state, reply, console, usage_delta)
                self._save_assistant(session, user_id, reply, state)
                return self._result([reply], [], state, console, usage_delta, session["session_id"])
            if self._is_yes(text):
                state["pending_rule_id"] = ""
                state["pending_question"] = ""
                reply = "ช่วยพิมพ์อาการผิดปกติหลักสั้น ๆ เช่น “หายใจขัด” หรือ “หมากัด”"
                self._save_assistant(session, user_id, reply, state)
                return self._result([reply], [], state, console, usage_delta, session["session_id"])

        group_id = state.get("active_group_id")
        if group_id and not state.get("red_bundle_done"):
            red_bundle = self._ask_red_bundle(session, user_id, group_id, state, console, usage_delta)
            if red_bundle:
                return red_bundle

        if not group_id:
            group_ids = self._select_groups_for_message(text, user, previous, recent, session, state, console, usage_delta, allow_llm=False)
            if group_ids:
                self._set_active_groups(state, group_ids, text)
                console.append(
                    self._event(
                        "ems.groups_selected",
                        "selected one or more symptom groups",
                        {"group_ids": group_ids, "mode": "llm_or_deterministic"},
                    )
                )
                red_bundle = self._ask_red_bundle(session, user_id, state["active_group_id"], state, console, usage_delta)
                if red_bundle:
                    return red_bundle

        llm_first = self._llm_first(
            text=text,
            user=user,
            session=session,
            state=state,
            previous=previous,
            recent=recent,
            console=console,
            usage_delta=usage_delta,
        )

        if state.get("pending_rule_id") == "DAILY_ABNORMAL":
            daily_answer = self._answer_value(text, llm_first)
            daily_candidates = self.corpus.deterministic_group_match(text)
            llm_candidates = self._extract_group_ids((llm_first or {}).get("candidate_group_ids") or (llm_first or {}).get("group_ids"))
            llm_candidate = (llm_first or {}).get("candidate_group_id") or (llm_first or {}).get("group_id") or (llm_candidates[0] if llm_candidates else "")
            if daily_answer == "no":
                state["risk_level"] = "green"
                state["pending_rule_id"] = ""
                state["pending_question"] = ""
                state["flow_phase"] = "complete"
                observation = {"type": "daily_checkin", "answer": "no_abnormal_symptom"}
                self.db.record_observation(session["session_id"], user_id, "", "green", observation)
                reply = self._patient_risk_reply("green")
                self._close_with_summary(session, user_id, state, reply, console, usage_delta)
                self._save_assistant(session, user_id, reply, state)
                return self._result([reply], [], state, console, usage_delta, session["session_id"])
            state["pending_rule_id"] = ""
            state["pending_question"] = ""
            if daily_answer == "yes" and not daily_candidates and not llm_candidate:
                reply = "ช่วยพิมพ์อาการผิดปกติหลักสั้น ๆ เช่น “หายใจขัด” หรือ “หมากัด”"
                self._save_assistant(session, user_id, reply, state)
                return self._result([reply], [], state, console, usage_delta, session["session_id"])

        if state.get("pending_rule_id"):
            return self._handle_pending_answer(user, session, user_id, text, state, console, usage_delta, llm_first)

        group_id = state.get("active_group_id")
        if not group_id:
            group_ids = self._select_groups_for_message(text, user, previous, recent, session, state, console, usage_delta, llm_first)
            if not group_ids:
                reply = "ยังเลือกกลุ่มอาการไม่ได้\nขออาการหลัก 1 อย่าง เช่น ปวดท้อง / หายใจขัด / ถูกกัด"
                self._save_assistant(session, user_id, reply, state)
                return self._result([reply], [], state, console, usage_delta, session["session_id"])
            self._set_active_groups(state, group_ids, text)
            group_id = state["active_group_id"]
            console.append(self._event("ems.groups_selected", "selected symptom groups", {"group_ids": group_ids}))

        if not state.get("red_bundle_done"):
            red_bundle = self._ask_red_bundle(session, user_id, group_id, state, console, usage_delta)
            if red_bundle:
                return red_bundle

        if not state.get("yellow_done"):
            return self._ask_next_yellow_or_finish(user, session, user_id, state, console, usage_delta)

        return self._finish_yellow_flow(user, session, user_id, state, console, usage_delta)

    def _handle_pending_answer(self, user, session, user_id, text, state, console, usage_delta, llm_first=None):
        rule_id = state.get("pending_rule_id")
        group_id = state.get("active_group_id")
        if not group_id or rule_id == "DAILY_ABNORMAL":
            state["pending_rule_id"] = ""
            state["pending_question"] = ""
            reply = "ขออาการหลักอีกครั้ง เพื่อเลือกกลุ่มอาการจาก EMS Markdown"
            self._save_assistant(session, user_id, reply, state)
            return self._result([reply], [], state, console, usage_delta, session["session_id"])

        group = self._active_group(state)
        rule = self._find_rule(group, rule_id)
        state.setdefault("asked_rule_ids", []).append(rule_id)
        state["pending_rule_id"] = ""
        state["pending_question"] = ""
        answer = self._answer_value(text, llm_first)
        matched = self._answer_matches_rule(answer, rule)
        state["observations"].append(
            {
                "at": utc_now(),
                "rule_id": rule_id,
                "question": rule["user_friendly_check"],
                "answer": text,
                "matched": matched,
            }
        )
        self.db.record_observation(
            session["session_id"],
            user_id,
            group_id,
            rule["level"] if matched else "insufficient",
            state["observations"][-1],
        )
        console.append(
            self._event(
                "flow.answer",
                "evaluated screening answer",
                {"rule_id": rule_id, "answer": answer, "matched": matched},
            )
        )

        if matched and rule["level"] == "red":
            state["risk_level"] = rule["level"]
            state["matched_rules"].append(rule)
            alert = self._make_alert(user, session, group, rule, text, state)
            reply = self._patient_risk_reply("red", alert)
            self._save_assistant(session, user_id, reply, state)
            self._close_with_summary(session, user_id, state, reply, console, usage_delta)
            return self._result(
                [reply],
                [alert],
                state,
                console,
                usage_delta,
                session["session_id"],
                ui_messages=[self._history_flex(session["session_id"], "red")],
            )

        if matched and rule["level"] == "yellow":
            state.setdefault("yellow_answers", {})[rule_id] = {
                "answer": text,
                "matched": True,
                "normalized_answer": answer,
                "confidence": 1,
                "reason_for_backend": "direct answer matched yellow rule; continuing required yellow checks before alert",
                "source_ref": rule.get("source_ref", ""),
            }
            console.append(
                self._event(
                    "flow.yellow.defer_alert",
                    "yellow matched but alert deferred until remaining checks and details are complete",
                    {"rule_id": rule_id},
                )
            )
            return self._ask_next_yellow_or_finish(user, session, user_id, state, console, usage_delta)

        if matched and rule["level"] == "green":
            state["risk_level"] = "green"
            state["matched_rules"].append(rule)
            reply = self._patient_risk_reply("green")
            self._save_assistant(session, user_id, reply, state)
            self._close_with_summary(session, user_id, state, reply, console, usage_delta)
            return self._result([reply], [], state, console, usage_delta, session["session_id"])

        llm_triage = self._apply_llm_triage(user, session, user_id, text, state, console, usage_delta, llm_first)
        if llm_triage:
            return llm_triage

        next_question = self._next_rule_question(group_id, state)
        if next_question:
            state["pending_rule_id"] = next_question["rule_id"]
            state["pending_question"] = next_question["user_friendly_check"]
            reply = self._natural_reply(next_question["user_friendly_check"] + "\nตัวเลือก: ใช่ / ไม่ใช่", llm_first)
            self._save_assistant(session, user_id, reply, state)
            console.append(self._event("flow.ask", "asked next screening rule question", {"rule_id": next_question["rule_id"]}))
            return self._result([reply], [], state, console, usage_delta, session["session_id"])

        return self._finish_no_sourced_match(user, session, user_id, state, console, usage_delta)

    def _select_groups_for_message(self, text, user, previous, recent, session, state, console, usage_delta, llm_first=None, allow_llm=True):
        config = self._config(user)
        candidates = self.corpus.deterministic_group_match(text)
        console.append(self._event("ems.retrieve", "deterministic retrieval from Symptoms markdown", {"candidates": candidates}))
        if allow_llm and self.llm.enabled and config.get("llm_retrieval_assist"):
            assisted = self._assist_retrieval_with_llm(text, user, previous, recent, session, candidates, console, usage_delta)
            if assisted:
                candidates = self._merge_candidates(candidates, assisted.get("candidates", []))
                console.append(
                    self._event(
                        "ems.retrieve.assisted",
                        "merged OpenAI retrieval topics into deterministic candidate list",
                        {
                            "retrieval_topics": assisted.get("retrieval_topics", []),
                            "query_terms": assisted.get("query_terms", []),
                            "candidate_group_ids": assisted.get("candidate_group_ids", []),
                            "merged_candidates": candidates,
                        },
                    )
                )
        deterministic_group_ids = self._context_adjusted_group_ids(text, self._distinct_candidate_group_ids(candidates)[:3], console)
        should_call_group_llm = allow_llm and (bool(config.get("llm_group_selection")) or not deterministic_group_ids)
        if self.llm.enabled and should_call_group_llm:
            group_ids = self._select_groups_with_llm(text, user, previous, recent, session, candidates, console, usage_delta)
            if group_ids:
                return group_ids
        elif should_call_group_llm:
            console.append(
                self._event(
                    "llm.group_selection.unavailable",
                    "OpenAI group selection was needed but OpenAI is disabled",
                    {
                        "llm_group_selection": bool(config.get("llm_group_selection")),
                        "deterministic_group_ids": deterministic_group_ids,
                        "llm_enabled": bool(self.llm.enabled),
                        "api_key_present": bool(getattr(self.llm, "api_key", "")),
                        "disabled_by_env": bool(getattr(self.llm, "disabled_by_env", False)),
                    },
                )
            )
        if allow_llm:
            fallback_group_ids = self._local_group_fallback_ids(text, deterministic_group_ids, console)
            if fallback_group_ids:
                return fallback_group_ids
        if llm_first:
            group_ids = self._extract_group_ids(llm_first.get("candidate_group_ids") or llm_first.get("group_ids"))
            if not group_ids:
                group_id = llm_first.get("candidate_group_id") or llm_first.get("group_id") or ""
                group_ids = [group_id] if group_id else []
            group_ids = self._valid_group_ids(group_ids)
            confidence = float(llm_first.get("confidence", 0) or 0)
            if group_ids and confidence >= 0.55:
                console.append(self._event("llm_first.groups", "used LLM-first candidate groups", {"group_ids": group_ids, "confidence": confidence}))
                return group_ids[:3]
        return deterministic_group_ids

    def _local_group_fallback_ids(self, text, existing_group_ids, console=None):
        if existing_group_ids:
            return []
        raw = str(text or "")
        compact = re.sub(r"\s+", "", raw)
        if "เด็ก" in compact and "ไข้" in compact:
            group_ids = ["EMS20"]
        elif self._fever_without_environment_context(raw):
            group_ids = ["EMS17"]
        else:
            group_ids = []
        if group_ids and console is not None:
            console.append(
                self._event(
                    "ems.group_local_fallback",
                    "selected symptom group from local fallback after retrieval/LLM did not return a usable group",
                    {"group_ids": group_ids, "message": raw[:120]},
                )
            )
        return group_ids

    def _assist_retrieval_with_llm(self, text, user, previous, recent, session, candidates, console, usage_delta):
        payload = {
            "message": text,
            "symptom_index": self.corpus.symptom_index_for_prompt(),
            "deterministic_candidates": candidates,
            "long_term_memory": previous,
            "recent_session_chat": recent[-8:],
            "user_personalized_prompt": user.get("personalized_prompt", ""),
            "instruction": [
                "Help retrieval only. Convert the user's casual Thai wording into EMS retrieval topics and short search terms.",
                "Use only group IDs and labels that exist in symptom_index.",
                "Do not decide risk level, do not diagnose, do not ask questions, do not invent EMS rules.",
                "Return multiple candidate_group_ids only when the text clearly includes multiple distinct symptoms.",
                "Prefer broad symptom topics suitable for retrieving Symptoms markdown, not medical explanations.",
            ],
            "return_json_schema": {
                "retrieval_topics": ["short Thai symptom topic phrases, e.g. หายใจยากลำบาก"],
                "query_terms": ["short Thai aliases/synonyms for deterministic retrieval"],
                "candidate_group_ids": ["EMSxx values from symptom_index only"],
                "confidence": "0.0-1.0",
                "reason_for_backend": "short note, retrieval only, no diagnosis",
            },
        }
        result = self.llm.generate_json(
            self.system_prompt,
            json.dumps(payload, ensure_ascii=False),
            "retrieval_assist",
        )
        self._record_llm(session, user["user_id"], result, "retrieval_assist", console, usage_delta)
        data = result.get("data") or {}
        if not result.get("ok") or not isinstance(data, dict):
            return {}
        confidence = float(data.get("confidence", 0) or 0)
        if confidence < 0.35:
            console.append(
                self._event(
                    "llm.retrieval_assist.low_confidence",
                    "ignored OpenAI retrieval assist because confidence was low",
                    {"confidence": confidence},
                )
            )
            return {}
        topics = self._short_text_list(data.get("retrieval_topics"), limit=5)
        terms = self._short_text_list(data.get("query_terms"), limit=12)
        candidate_group_ids = self._valid_group_ids(self._extract_group_ids(data.get("candidate_group_ids") or data.get("group_ids")))
        query_text = " ".join([text] + topics + terms)
        assisted_candidates = self.corpus.deterministic_group_match(query_text)
        for group_id in candidate_group_ids:
            group = self.corpus.get_group(group_id)
            if not group:
                continue
            assisted_candidates.append(
                {
                    "group_id": group_id,
                    "group_name_th": group.get("group_name_th", ""),
                    "score": 5,
                    "reasons": ["llm_retrieval_assist"] + topics[:2],
                }
            )
        console.append(
            self._event(
                "llm.retrieval_assist",
                "OpenAI suggested retrieval topics and query terms before Markdown retrieval",
                {
                    "retrieval_topics": topics,
                    "query_terms": terms,
                    "candidate_group_ids": candidate_group_ids,
                    "confidence": confidence,
                    "reason_for_backend": data.get("reason_for_backend", ""),
                },
            )
        )
        return {
            "retrieval_topics": topics,
            "query_terms": terms,
            "candidate_group_ids": candidate_group_ids,
            "candidates": assisted_candidates,
        }

    def _merge_candidates(self, primary, secondary):
        merged = []
        by_id = {}
        for candidate in list(primary or []) + list(secondary or []):
            group_id = candidate.get("group_id", "")
            if not group_id:
                continue
            current = by_id.get(group_id)
            if not current:
                copied = dict(candidate)
                copied["reasons"] = list(candidate.get("reasons") or [])
                by_id[group_id] = copied
                merged.append(copied)
                continue
            current["score"] = max(int(current.get("score", 0) or 0), int(candidate.get("score", 0) or 0))
            for reason in candidate.get("reasons") or []:
                if reason not in current["reasons"]:
                    current["reasons"].append(reason)
        merged.sort(key=lambda item: item.get("score", 0), reverse=True)
        return merged[:8]

    def _select_groups_with_llm(self, text, user, previous, recent, session, candidates, console, usage_delta):
        payload = {
            "message": text,
            "symptom_index": self.corpus.symptom_index_for_prompt(),
            "deterministic_candidates": candidates,
            "long_term_memory": previous,
            "recent_session_chat": recent[-8:],
            "user_personalized_prompt": user.get("personalized_prompt", ""),
            "instruction": [
                "Select every EMS group needed for the user's current symptom report.",
                "Return multiple group_ids only when the message contains distinct symptoms or incidents that map to different EMS groups.",
                "EMS10 is for environmental exposure. Do not select EMS10 for fever/chills alone unless heat, cold, smoke, chemical, spray, or heavy exercise exposure is stated.",
                "For adult fever/chills without a more specific EMS group, prefer EMS17 for general/non-specific illness.",
                "Do not diagnose. Use only symptom_index group IDs. Do not include EMS11.",
            ],
            "return_json_schema": {
                "group_ids": ["EMSxx"],
                "primary_group_id": "EMSxx or empty",
                "confidence": "0.0-1.0",
                "symptom_mentions": [
                    {
                        "text": "short symptom phrase from user",
                        "group_id": "EMSxx",
                    }
                ],
                "reason_for_backend": "short note, no diagnosis",
            },
        }
        result = self.llm.generate_json(
            self.system_prompt,
            json.dumps(payload, ensure_ascii=False),
            "group_selection",
        )
        self._record_llm(session, user["user_id"], result, "group_selection", console, usage_delta)
        data = result.get("data") or {}
        if not result.get("ok") or not isinstance(data, dict):
            return []
        group_ids = self._extract_group_ids(data.get("group_ids") or data.get("candidate_group_ids"))
        primary = data.get("primary_group_id") or data.get("candidate_group_id") or data.get("group_id") or ""
        if primary:
            group_ids = [primary] + [group_id for group_id in group_ids if group_id != primary]
        group_ids = self._context_adjusted_group_ids(text, self._valid_group_ids(group_ids), console)
        confidence = float(data.get("confidence", 0) or 0)
        if group_ids and confidence >= 0.45:
            console.append(
                self._event(
                    "llm.group_selection",
                    "OpenAI selected symptom groups after backend validation",
                    {
                        "group_ids": group_ids[:3],
                        "confidence": confidence,
                        "symptom_mentions": data.get("symptom_mentions", []),
                    },
                )
            )
            return group_ids[:3]
        return []

    def _context_adjusted_group_ids(self, text, group_ids, console=None):
        adjusted = list(group_ids or [])
        if "EMS10" not in adjusted:
            return adjusted
        if not self._fever_without_environment_context(text):
            return adjusted
        adjusted = ["EMS17" if group_id == "EMS10" else group_id for group_id in adjusted]
        adjusted = self._valid_group_ids(adjusted)
        if console is not None:
            console.append(
                self._event(
                    "ems.group_context_adjust",
                    "adjusted environmental group to general illness when fever/chills had no environmental exposure context",
                    {"from": "EMS10", "to": "EMS17", "message": str(text or "")[:120]},
                )
            )
        return adjusted

    def _fever_without_environment_context(self, text):
        raw = str(text or "")
        compact = re.sub(r"\s+", "", raw)
        fever_terms = ("ไข้", "ตัวร้อน", "หนาวสั่น")
        if not any(term in compact for term in fever_terms):
            return False
        environment_terms = (
            "ที่ร้อน",
            "ร้อนจัด",
            "แดด",
            "กลางแดด",
            "อากาศร้อน",
            "ความร้อน",
            "ออกกำลังกาย",
            "วิ่ง",
            "ความเย็น",
            "หนาวจัด",
            "เย็นจัด",
            "ควัน",
            "สารเคมี",
            "สเปรย์พริกไทย",
        )
        return not any(term in compact for term in environment_terms)

    def _valid_group_ids(self, group_ids):
        valid = []
        for group_id in group_ids:
            group_id = str(group_id or "").strip().upper()
            if group_id in self.corpus.groups and group_id != "EMS11" and group_id not in valid:
                valid.append(group_id)
        return valid

    def _distinct_candidate_group_ids(self, candidates):
        selected = []
        selected_reasons = []
        for candidate in candidates:
            if candidate.get("score", 0) < 3:
                continue
            reasons = self._candidate_reason_set(candidate)
            if not reasons:
                continue
            is_duplicate = False
            for existing in selected_reasons:
                if reasons <= existing:
                    is_duplicate = True
                    break
            if is_duplicate:
                continue
            group_id = candidate.get("group_id", "")
            if group_id in self.corpus.groups and group_id != "EMS11" and group_id not in selected:
                selected.append(group_id)
                selected_reasons.append(reasons)
        return selected

    def _candidate_reason_set(self, candidate):
        reasons = candidate.get("reasons") or []
        if isinstance(reasons, str):
            reasons = reasons.split()
        return {str(reason).strip().lower() for reason in reasons if str(reason).strip()}

    def _extract_group_ids(self, value):
        if not value:
            return []
        if isinstance(value, str):
            return re.findall(r"EMS\d{2}", value.upper())
        if isinstance(value, list):
            found = []
            for item in value:
                if isinstance(item, dict):
                    found.extend(self._extract_group_ids(item.get("group_id") or item.get("id") or ""))
                else:
                    found.extend(self._extract_group_ids(str(item)))
            return list(dict.fromkeys(found))
        if isinstance(value, dict):
            return self._extract_group_ids(value.get("group_id") or value.get("id") or "")
        return []

    def _short_text_list(self, value, limit=8, item_limit=48):
        if not value:
            return []
        if isinstance(value, str):
            raw_items = re.split(r"[,;\n]+", value)
        elif isinstance(value, list):
            raw_items = value
        else:
            raw_items = [value]
        items = []
        for item in raw_items:
            text = re.sub(r"\s+", " ", str(item or "")).strip()
            if not text:
                continue
            blocked = ("วินิจฉัย", "รักษา", "กินยา", "ควรทำ", "โรค")
            if any(term in text for term in blocked):
                continue
            if len(text) > item_limit:
                text = text[:item_limit].strip()
            if text not in items:
                items.append(text)
            if len(items) >= limit:
                break
        return items

    def _set_active_groups(self, state, group_ids, text):
        group_ids = self._valid_group_ids(group_ids)
        state["active_group_ids"] = group_ids
        state["active_group_id"] = "+".join(group_ids) if len(group_ids) > 1 else (group_ids[0] if group_ids else "")
        state.setdefault("observations", []).append({"at": utc_now(), "main_symptom_text": text, "group_ids": group_ids, "group_id": state["active_group_id"]})

    def _select_group_with_memory(self, text, user, previous, recent, session, console, usage_delta, llm_first=None):
        candidates = self.corpus.deterministic_group_match(text)
        console.append(self._event("ems.retrieve", "deterministic retrieval from Symptoms markdown", {"candidates": candidates}))
        if llm_first:
            group_id = llm_first.get("candidate_group_id") or llm_first.get("group_id") or ""
            confidence = float(llm_first.get("confidence", 0) or 0)
            candidate_ids = {c["group_id"] for c in candidates}
            supported = (not candidates) or (group_id in candidate_ids) or confidence >= 0.75
            if group_id in self.corpus.groups and group_id != "EMS11" and confidence >= 0.55 and supported:
                console.append(
                    self._event(
                        "llm_first.group",
                        "used LLM-first candidate group",
                        {"group_id": group_id, "confidence": confidence},
                    )
                )
                return group_id
        selected = candidates[0]["group_id"] if candidates and candidates[0]["score"] >= 3 else ""
        if self.llm.enabled and self._config(user).get("llm_group_selection"):
            payload = {
                "message": text,
                "symptom_index": self.corpus.symptom_index_for_prompt(),
                "deterministic_candidates": candidates,
                "long_term_memory": previous,
                "recent_session_chat": recent[-8:],
                "user_personalized_prompt": user.get("personalized_prompt", ""),
                "instruction": "Select one EMS group_id from symptom_index or return insufficient. Do not diagnose.",
            }
            result = self.llm.generate_json(
                self.system_prompt,
                json.dumps(payload, ensure_ascii=False),
                "group_selection",
            )
            self._record_llm(session, user["user_id"], result, "group_selection", console, usage_delta)
            data = result.get("data") or {}
            group_id = data.get("group_id", "")
            confidence = float(data.get("confidence", 0) or 0)
            if group_id in self.corpus.groups and group_id != "EMS11" and confidence >= 0.55:
                return group_id
        return selected

    def _select_group_deterministic(self, text, console):
        candidates = self.corpus.deterministic_group_match(text)
        console.append(self._event("ems.retrieve", "deterministic retrieval before OpenAI", {"candidates": candidates}))
        if candidates and candidates[0]["score"] >= 3:
            return candidates[0]["group_id"]
        return ""

    def _active_group(self, state):
        group_ids = self._valid_group_ids(state.get("active_group_ids") or self._extract_group_ids(state.get("active_group_id", "")))
        if not group_ids and state.get("active_group_id") in self.corpus.groups:
            group_ids = [state.get("active_group_id")]
        if not group_ids:
            return None
        if len(group_ids) == 1:
            return self.corpus.get_group(group_ids[0])
        groups = [self.corpus.get_group(group_id) for group_id in group_ids]
        groups = [group for group in groups if group]
        rules = []
        questions = []
        keywords = []
        excerpts = []
        paths = []
        for group in groups:
            rules.extend(group.get("rules", []))
            questions.extend(group.get("questions", []))
            keywords.extend([kw for kw in group.get("keywords", []) if kw not in keywords])
            excerpts.append("<!-- {0} {1} -->\n{2}".format(group["group_id"], group["group_name_th"], group.get("markdown_excerpt", "")[:2500]))
            paths.append(group.get("path", ""))
        return {
            "path": "; ".join(paths),
            "group_id": "+".join([group["group_id"] for group in groups]),
            "group_name_th": " + ".join([group["group_name_th"] for group in groups]),
            "rules": rules,
            "questions": sorted(questions, key=lambda q: q.get("priority", 99)),
            "keywords": keywords,
            "markdown_excerpt": "\n\n".join(excerpts)[:6000],
            "component_groups": groups,
        }

    def _ask_red_bundle(self, session, user_id, group_id, state, console, usage_delta):
        group = self._active_group(state) if "+" in str(group_id) else self.corpus.get_group(group_id)
        rules = self._screening_rules(group, "red", state)
        state["red_bundle_rule_ids"] = [rule["rule_id"] for rule in rules]
        if not rules:
            state["red_bundle_done"] = True
            state["flow_phase"] = "yellow_open"
            return None
        state["pending_rule_id"] = "RED_BUNDLE"
        state["pending_question"] = "มีอาการแจ้งเตือนแดงข้อใดข้อหนึ่งไหม?"
        state["flow_phase"] = "red_bundle"
        reply = self._red_bundle_text(group, rules)
        ui = [self._red_bundle_flex(group, rules)]
        self._save_assistant(session, user_id, reply, state)
        console.append(
            self._event(
                "flow.red_bundle.ask",
                "asked one bundled red-flag flex message",
                {"group_id": group_id, "rule_ids": state["red_bundle_rule_ids"]},
            )
        )
        return self._result([], [], state, console, usage_delta, session["session_id"], ui_messages=ui)

    def _handle_red_bundle_answer(self, user, session, user_id, text, state, console, usage_delta, llm_first=None):
        group = self._active_group(state)
        if not group:
            state["pending_rule_id"] = ""
            state["pending_question"] = ""
            return self._finish_no_sourced_match(user, session, user_id, state, console, usage_delta)
        rules = [self._find_rule_or_none(group, rule_id) for rule_id in state.get("red_bundle_rule_ids", [])]
        rules = [rule for rule in rules if rule]
        answer = self._answer_value(text, llm_first)
        if answer not in ("yes", "no"):
            reply = "กรุณากดปุ่ม ใช่ หรือ ไม่ใช่ สำหรับอาการแจ้งเตือนแดง"
            self._save_assistant(session, user_id, reply, state)
            console.append(self._event("flow.red_bundle.retry", "red bundle answer was unclear", {"answer_text": text}))
            return self._result([reply], [], state, console, usage_delta, session["session_id"], ui_messages=[self._red_bundle_flex(group, rules)])

        state["pending_rule_id"] = ""
        state["pending_question"] = ""
        state["red_bundle_done"] = True
        for rule in rules:
            if rule["rule_id"] not in state.setdefault("red_checked_rule_ids", []):
                state["red_checked_rule_ids"].append(rule["rule_id"])
        observation = {
            "at": utc_now(),
            "type": "red_bundle",
            "answer": answer,
            "rule_ids": [rule["rule_id"] for rule in rules],
        }
        state.setdefault("observations", []).append(observation)
        self.db.record_observation(session["session_id"], user_id, group["group_id"], "red" if answer == "yes" else "insufficient", observation)

        if answer == "yes":
            rule = self._bundle_rule(group, "red", rules, "ผู้ใช้ตอบว่ามีอย่างน้อยหนึ่งอาการแจ้งเตือนแดงในชุดคำถาม")
            state["risk_level"] = "red"
            state["flow_phase"] = "complete"
            state.setdefault("matched_rules", []).append(rule)
            alert = self._make_alert(user, session, group, rule, text, state)
            reply = self._patient_risk_reply("red", alert)
            self._save_assistant(session, user_id, reply, state)
            self._close_with_summary(session, user_id, state, reply, console, usage_delta)
            console.append(self._event("flow.red_bundle.alert", "red bundle confirmed by user", {"rule_id": rule["rule_id"]}))
            return self._result(
                [reply],
                [alert],
                state,
                console,
                usage_delta,
                session["session_id"],
                ui_messages=[self._history_flex(session["session_id"], "red")],
            )

        console.append(self._event("flow.red_bundle.clear", "user denied bundled red flags", {"group_id": group["group_id"]}))
        return self._ask_next_yellow_or_finish(user, session, user_id, state, console, usage_delta)

    def _ask_next_yellow_or_finish(self, user, session, user_id, state, console, usage_delta):
        group = self._active_group(state)
        if not group:
            return self._finish_no_sourced_match(user, session, user_id, state, console, usage_delta)
        state["flow_phase"] = "yellow_open"
        rules = self._screening_rules(group, "yellow", state)
        rules = self._contextual_yellow_rules(rules, state)
        self._auto_match_yellow_from_context(session, user_id, group, rules, state, console)
        answered = set((state.get("yellow_answers") or {}).keys())
        pending_rules = [rule for rule in rules if rule["rule_id"] not in answered]
        batch = pending_rules[:2]
        state["yellow_rule_ids"] = [rule["rule_id"] for rule in rules]
        if batch:
            state["pending_rule_id"] = "YELLOW_SUMMARY"
            state["yellow_current_rule_ids"] = [rule["rule_id"] for rule in batch]
            state["pending_question"] = self._yellow_summary_question(group, batch, state)
            reply = state["pending_question"]
            self._save_assistant(session, user_id, reply, state)
            console.append(
                self._event(
                    "flow.yellow.ask",
                    "asked a small open-ended yellow screening batch",
                    {
                        "group_id": group["group_id"],
                        "rule_ids": state["yellow_current_rule_ids"],
                        "remaining": max(len(pending_rules) - len(batch), 0),
                    },
                )
            )
            return self._result([reply], [], state, console, usage_delta, session["session_id"])
        state["pending_rule_id"] = ""
        state["pending_question"] = ""
        state["yellow_done"] = True
        return self._finish_yellow_flow(user, session, user_id, state, console, usage_delta)

    def _handle_yellow_open_answer(self, user, session, user_id, text, state, console, usage_delta, llm_first=None):
        group = self._active_group(state)
        rule_id = state.get("pending_rule_id")
        if rule_id == "YELLOW_SUMMARY":
            return self._handle_yellow_summary_answer(user, session, user_id, text, state, console, usage_delta)
        rule = self._find_rule_or_none(group, rule_id)
        if not group or not rule:
            state["pending_rule_id"] = ""
            state["pending_question"] = ""
            return self._finish_no_sourced_match(user, session, user_id, state, console, usage_delta)

        evaluation = self._evaluate_yellow_open_answer(user, session, text, rule, state, console, usage_delta, llm_first)
        state.setdefault("asked_rule_ids", []).append(rule_id)
        state.setdefault("yellow_answers", {})[rule_id] = {
            "answer": text,
            "matched": bool(evaluation.get("matched")),
            "normalized_answer": evaluation.get("normalized_answer", "unknown"),
            "confidence": evaluation.get("confidence", 0),
            "reason_for_backend": evaluation.get("reason_for_backend", ""),
            "source_ref": rule.get("source_ref", ""),
        }
        observation = {
            "at": utc_now(),
            "type": "yellow_open_answer",
            "rule_id": rule_id,
            "question": state.get("pending_question", ""),
            "answer": text,
            "matched": bool(evaluation.get("matched")),
            "evaluation": evaluation,
        }
        state.setdefault("observations", []).append(observation)
        self.db.record_observation(
            session["session_id"],
            user_id,
            group["group_id"],
            "yellow" if evaluation.get("matched") else "insufficient",
            observation,
        )
        state["pending_rule_id"] = ""
        state["pending_question"] = ""
        console.append(
            self._event(
                "flow.yellow.answer",
                "evaluated open-ended yellow answer",
                {"rule_id": rule_id, "matched": bool(evaluation.get("matched")), "confidence": evaluation.get("confidence", 0)},
            )
        )
        return self._ask_next_yellow_or_finish(user, session, user_id, state, console, usage_delta)

    def _handle_yellow_summary_answer(self, user, session, user_id, text, state, console, usage_delta):
        group = self._active_group(state)
        if not group:
            state["pending_rule_id"] = ""
            state["pending_question"] = ""
            return self._finish_no_sourced_match(user, session, user_id, state, console, usage_delta)
        redirect = self._redirect_new_symptom_if_needed(session, user_id, text, state, console, usage_delta)
        if redirect:
            return redirect
        rules = [self._find_rule_or_none(group, rule_id) for rule_id in state.get("yellow_current_rule_ids", [])]
        rules = [rule for rule in rules if rule]
        evaluations = self._evaluate_yellow_summary_answer(user, session, text, rules, state, console, usage_delta)
        state.setdefault("yellow_answers", {})
        for rule in rules:
            evaluation = evaluations.get(rule["rule_id"], {})
            state["yellow_answers"][rule["rule_id"]] = {
                "answer": text,
                "matched": bool(evaluation.get("matched")),
                "normalized_answer": evaluation.get("normalized_answer", "unknown"),
                "confidence": evaluation.get("confidence", 0),
                "reason_for_backend": evaluation.get("reason_for_backend", ""),
                "source_ref": rule.get("source_ref", ""),
            }
        state.setdefault("asked_rule_ids", []).extend([rule["rule_id"] for rule in rules])
        state["pending_rule_id"] = ""
        state["pending_question"] = ""
        state["yellow_current_rule_ids"] = []
        observation = {
            "at": utc_now(),
            "type": "yellow_summary_answer",
            "rule_ids": [rule["rule_id"] for rule in rules],
            "answer": text,
            "evaluations": evaluations,
        }
        state.setdefault("observations", []).append(observation)
        matched = any(item.get("matched") for item in evaluations.values())
        self.db.record_observation(
            session["session_id"],
            user_id,
            group["group_id"],
            "yellow" if matched else "insufficient",
            observation,
        )
        console.append(
            self._event(
                "flow.yellow.answer",
                "evaluated one open-ended yellow summary answer",
                {"matched_rule_ids": [rule_id for rule_id, item in evaluations.items() if item.get("matched")]},
            )
        )
        return self._ask_next_yellow_or_finish(user, session, user_id, state, console, usage_delta)

    def _redirect_new_symptom_if_needed(self, session, user_id, text, state, console, usage_delta):
        if self._answer_value(text) in ("yes", "no"):
            return None
        if re.fullmatch(r"[0-9๐-๙]+", text.strip()):
            return None
        candidates = self.corpus.deterministic_group_match(text)
        user = self.db.get_or_create_user(user_id)
        if self.llm.enabled and self._config(user).get("llm_retrieval_assist"):
            previous = self.db.previous_summaries(user_id, limit=6)
            recent = self.db.recent_chat(session["session_id"], limit=12)
            assisted = self._assist_retrieval_with_llm(text, user, previous, recent, session, candidates, console, usage_delta)
            if assisted:
                candidates = self._merge_candidates(candidates, assisted.get("candidates", []))
        candidate_group_ids = self._distinct_candidate_group_ids(candidates)
        active_group_ids = self._valid_group_ids(state.get("active_group_ids") or self._extract_group_ids(state.get("active_group_id", "")))
        new_group_ids = [group_id for group_id in candidate_group_ids if group_id not in active_group_ids]
        if not new_group_ids:
            return None
        merged_group_ids = self._valid_group_ids(new_group_ids[:3])
        if not merged_group_ids:
            return None
        self._set_active_groups(state, merged_group_ids, text)
        state["pending_rule_id"] = ""
        state["pending_question"] = ""
        state["yellow_current_rule_ids"] = []
        state["yellow_answers"] = {}
        state["auto_matched_rule_ids"] = []
        state["yellow_done"] = False
        state["yellow_detail_questions"] = []
        state["yellow_details"] = {}
        state["pending_detail_key"] = ""
        state["red_bundle_done"] = False
        state["red_bundle_rule_ids"] = []
        state["flow_phase"] = "red_bundle"
        console.append(
            self._event(
                "flow.topic_shift",
                "detected a new symptom during screening and redirected to red bundle for the added group",
                {
                    "new_group_ids": new_group_ids,
                    "active_group_ids": merged_group_ids,
                    "candidates": candidates,
                    "text": text[:80],
                },
            )
        )
        return self._ask_red_bundle(session, user_id, state["active_group_id"], state, console, usage_delta)

    def _finish_yellow_flow(self, user, session, user_id, state, console, usage_delta):
        group = self._active_group(state)
        if not group:
            return self._finish_no_sourced_match(user, session, user_id, state, console, usage_delta)
        yellow_answers = state.get("yellow_answers") or {}
        matched_rules = []
        for rule_id, answer in yellow_answers.items():
            if answer.get("matched"):
                rule = self._find_rule_or_none(group, rule_id)
                if rule:
                    matched_rules.append(rule)
        state["pending_rule_id"] = ""
        state["pending_question"] = ""
        state["yellow_done"] = True

        detail_result = self._ask_next_yellow_detail_if_needed(
            user, session, user_id, group, matched_rules, state, console, usage_delta
        )
        if detail_result:
            return detail_result

        if matched_rules:
            state["flow_phase"] = "complete"
            rule = self._bundle_rule(group, "yellow", matched_rules, "พบคำตอบที่เข้าเกณฑ์ yellow หลังถามครบชุด")
            state["risk_level"] = "yellow"
            state.setdefault("matched_rules", []).append(rule)
            alert = self._make_alert(user, session, group, rule, "yellow open-ended answers completed", state)
            reply = self._patient_risk_reply("yellow", alert)
            self._save_assistant(session, user_id, reply, state)
            self._close_with_summary(session, user_id, state, reply, console, usage_delta)
            console.append(
                self._event(
                    "flow.yellow.alert",
                    "yellow detected after completing all yellow questions",
                    {"matched_rule_ids": [rule["rule_id"] for rule in matched_rules]},
                )
            )
            return self._result(
                [reply],
                [alert],
                state,
                console,
                usage_delta,
                session["session_id"],
                ui_messages=[self._history_flex(session["session_id"], "yellow")],
            )

        green_rule = self._first_green_rule(group)
        state["flow_phase"] = "complete"
        state["risk_level"] = "green"
        if green_rule:
            state.setdefault("matched_rules", []).append(green_rule)
            source = green_rule["source_ref"]
        else:
            source = "red bundle + yellow rules asked from EMS Markdown"
        reply = self._patient_risk_reply("green")
        self.db.record_observation(
            session["session_id"],
            user_id,
            group["group_id"],
            "green",
            {"final_state": state, "reason": "red denied and no yellow matched after all yellow questions"},
        )
        self._save_assistant(session, user_id, reply, state)
        self._close_with_summary(session, user_id, state, reply, console, usage_delta)
        console.append(self._event("flow.green", "completed yellow screening with no yellow matches", {"group_id": group["group_id"]}))
        return self._result([reply], [], state, console, usage_delta, session["session_id"])

    def _ask_next_yellow_detail_if_needed(self, user, session, user_id, group, matched_rules, state, console, usage_delta):
        if not state.get("yellow_detail_questions"):
            state["yellow_details"] = state.get("yellow_details") or {}
            state["yellow_detail_questions"] = self._build_yellow_detail_questions(group, matched_rules, state)
            self._prefill_yellow_details(group, state)
        details = state.setdefault("yellow_details", {})
        for question in state.get("yellow_detail_questions", []):
            key = question["key"]
            if key in details:
                continue
            state["flow_phase"] = "yellow_details"
            state["pending_detail_key"] = key
            state["pending_rule_id"] = ""
            state["pending_question"] = question["question"]
            console.append(
                self._event(
                    "flow.yellow.detail.ask",
                    "asked supplemental observation before yellow/green final decision",
                    {
                        "detail_key": key,
                        "detail_type": question["type"],
                        "source_rule_ids": question.get("source_rule_ids", []),
                    },
                )
            )
            if question["type"] == "scale_0_10":
                self._save_assistant(session, user_id, question["body"], state)
                return self._result(
                    [],
                    [],
                    state,
                    console,
                    usage_delta,
                    session["session_id"],
                    ui_messages=[self._scale_flex(question)],
                )
            if question["type"] == "options":
                self._save_assistant(session, user_id, question["body"], state)
                return self._result(
                    [],
                    [],
                    state,
                    console,
                    usage_delta,
                    session["session_id"],
                    ui_messages=[self._choice_flex(question)],
                )
            self._save_assistant(session, user_id, question["question"], state)
            return self._result([question["question"]], [], state, console, usage_delta, session["session_id"])
        state["pending_detail_key"] = ""
        return None

    def _handle_yellow_detail_answer(self, user, session, user_id, text, state, console, usage_delta):
        group = self._active_group(state)
        key = state.get("pending_detail_key", "")
        question = None
        for item in state.get("yellow_detail_questions", []):
            if item.get("key") == key:
                question = item
                break
        if not group or not question:
            state["pending_detail_key"] = ""
            state["flow_phase"] = "yellow_open"
            return self._finish_yellow_flow(user, session, user_id, state, console, usage_delta)
        redirect = self._redirect_new_symptom_if_needed(session, user_id, text, state, console, usage_delta)
        if redirect:
            return redirect

        value = None
        normalized = text.strip()
        if question["type"] == "scale_0_10":
            value = self._extract_first_int(normalized)
            if value is None or value < 0 or value > 10:
                retry = "กดหรือพิมพ์ตัวเลข 0-10 ได้เลย\n0 = ไม่ปวดเลย\n5 = ปวดพอทนไหว\n10 = ปวดมากที่สุดในชีวิต"
                state["pending_question"] = retry
                self._save_assistant(session, user_id, retry, state)
                console.append(self._event("flow.yellow.detail.retry", "pain scale answer was out of range", {"answer": text}))
                return self._result(
                    [],
                    [],
                    state,
                    console,
                    usage_delta,
                    session["session_id"],
                    ui_messages=[self._scale_flex(question, body=retry)],
                )
        elif question["type"] == "count":
            if self._is_no(normalized):
                value = 0
                normalized = "0"
            else:
                value = self._extract_first_int(normalized)
                if value is None:
                    retry = "พิมพ์จำนวนครั้งเป็นตัวเลขได้เลย เช่น 0, 1, 2"
                    state["pending_question"] = retry
                    self._save_assistant(session, user_id, retry, state)
                    console.append(self._event("flow.yellow.detail.retry", "count answer was not numeric", {"answer": text}))
                    return self._result([retry], [], state, console, usage_delta, session["session_id"])
        elif question["type"] == "options":
            value = normalized

        detail = {
            "at": utc_now(),
            "key": key,
            "label": question.get("label", key),
            "question": question["question"],
            "answer": text,
            "value": value,
            "type": question["type"],
            "source_rule_ids": question.get("source_rule_ids", []),
            "note": "supplemental observation only; not a new risk rule",
        }
        state.setdefault("yellow_details", {})[key] = detail
        state.setdefault("observations", []).append({"type": "yellow_detail", **detail})
        self.db.record_observation(session["session_id"], user_id, group["group_id"], "observation", detail)
        state["pending_detail_key"] = ""
        state["pending_question"] = ""
        console.append(
            self._event(
                "flow.yellow.detail.answer",
                "recorded supplemental observation",
                {"detail_key": key, "value": value, "answer": text[:80]},
            )
        )
        return self._finish_yellow_flow(user, session, user_id, state, console, usage_delta)

    def _build_yellow_detail_questions(self, group, matched_rules, state):
        source_rule_ids = [rule["rule_id"] for rule in matched_rules]
        matched_text = " ".join(
            [
                rule.get("condition_from_pdf", "") + " " + rule.get("user_friendly_check", "")
                for rule in matched_rules
            ]
        )
        answer_text = " ".join(
            [
                str(item.get("answer", ""))
                for item in (state.get("yellow_answers") or {}).values()
                if str(item.get("answer", "")).strip()
            ]
        )
        all_main_text = " ".join(
            [
                str(item.get("main_symptom_text", ""))
                for item in state.get("observations", [])
                if item.get("main_symptom_text")
            ]
        )
        main_text = self._last_main_symptom_text(state) or all_main_text
        group_text = "{0} {1}".format(group.get("group_id", ""), group.get("group_name_th", ""))
        matched_context = (matched_text + " " + answer_text).strip()
        symptom_context = (group_text + " " + main_text + " " + answer_text).strip()
        questions = []
        breathing_focus = self._breathing_context_without_pain(main_text)

        if self._group_is_pain_like(group) and not breathing_focus:
            choices = self._pain_location_choices(group)
            if choices:
                questions.append(
                    {
                        "key": "pain_location",
                        "type": "options",
                        "label": "ตำแหน่งอาการ",
                        "question": "ปวดตรงไหนเป็นหลัก?",
                        "body": "ปวดตรงไหนเป็นหลัก?",
                        "choices": choices,
                        "source_rule_ids": [group.get("group_id", "") + "_Q01"],
                    }
                )

        if (
            "อาเจียน" in matched_text
            or self._contains_affirmed_symptom(answer_text, "อาเจียน")
            or self._contains_affirmed_symptom(main_text, "อาเจียน")
        ):
            questions.append(
                {
                    "key": "vomit_count",
                    "type": "count",
                    "label": "จำนวนครั้งที่อาเจียน",
                    "question": "อาเจียนประมาณกี่ครั้งตั้งแต่เริ่มมีอาการ?",
                    "source_rule_ids": source_rule_ids,
                }
            )

        onset_question = self._question_by_text(group, "เริ่มเป็นเมื่อไหร่")
        if onset_question:
            choices = self._parse_choices(onset_question.get("choices", ""))
            onset_body = self._onset_question_text(group, main_text)
            questions.append(
                {
                    "key": "onset",
                    "type": "options",
                    "label": "เวลาเริ่มอาการ",
                    "question": onset_body,
                    "body": onset_body,
                    "choices": choices or ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"],
                    "source_rule_ids": [onset_question.get("question_id", "")],
                }
            )

        explicit_pain_detail = (
            "ปวด" in matched_text
            or "เจ็บ" in matched_text
            or (not breathing_focus and self._contains_affirmed_symptom(answer_text, "ปวด"))
            or (not breathing_focus and self._contains_affirmed_symptom(answer_text, "เจ็บ"))
            or self._contains_affirmed_symptom(main_text, "ปวด")
            or self._contains_affirmed_symptom(main_text, "เจ็บ")
        )
        has_pain_detail = (
            explicit_pain_detail
            or (self._group_is_pain_like(group) and not breathing_focus)
        )
        pain_label = ""
        if has_pain_detail:
            pain_context = (main_text + " " + answer_text + " " + (matched_text if explicit_pain_detail else "")).strip()
            pain_label = self._pain_detail_label(group, pain_context)
        if pain_label and has_pain_detail:
            questions.append(
                {
                    "key": "pain_score",
                    "type": "scale_0_10",
                    "label": "ระดับ" + pain_label,
                    "question": "ตอนนี้{0}ประมาณกี่คะแนน (0-10)?".format(pain_label),
                    "body": "ตอนนี้{0}ประมาณกี่คะแนน (0-10)?\n0 = ไม่ปวดเลย\n5 = ปวดพอทนไหว\n10 = ปวดมากที่สุดในชีวิต".format(pain_label),
                    "source_rule_ids": source_rule_ids,
                }
            )

        unique = []
        seen = set()
        for question in questions:
            if question["key"] in seen:
                continue
            seen.add(question["key"])
            unique.append(question)
        return unique

    def _pain_detail_label(self, group, text):
        raw = text or ""
        if "ศีรษะ" in raw or "ปวดหัว" in raw:
            return "ปวดหัว"
        if "หลัง" in raw and "ปวด" in raw:
            return "ปวดหลัง"
        if "เชิงกราน" in raw:
            return "ปวดเชิงกราน"
        if "ขาหนีบ" in raw:
            return "ปวดขาหนีบ"
        if "หน้าอก" in raw or "ยอดอก" in raw:
            return "เจ็บหรือแน่นหน้าอก"
        if "ท้อง" in raw:
            return "ปวดท้อง"
        combined = group.get("group_name_th", "")
        if "ศีรษะ" in combined or "ปวดหัว" in combined:
            return "ปวดหัว"
        if "หลัง" in combined:
            return "ปวดหลัง"
        if "เชิงกราน" in combined:
            return "ปวดเชิงกราน"
        if "ขาหนีบ" in combined:
            return "ปวดขาหนีบ"
        if "ท้อง" in combined:
            return "ปวดท้อง"
        if "หน้าอก" in combined or "ยอดอก" in combined:
            return "เจ็บหรือแน่นหน้าอก"
        if "ปวด" in combined or "เจ็บ" in combined or "ปวด" in raw or "เจ็บ" in raw:
            return "ความปวด"
        return ""

    def _breathing_context_without_pain(self, text):
        raw = str(text or "")
        if self._contains_affirmed_symptom(raw, "ปวด") or self._contains_affirmed_symptom(raw, "เจ็บ"):
            return False
        normalized = self._normalized_symptom_text(raw)
        return any(term in normalized for term in ("หายใจขัด", "หายใจ", "เหนื่อย"))

    def _group_is_pain_like(self, group):
        name = group.get("group_name_th", "")
        return any(term in name for term in ("ปวด", "เจ็บ", "ท้อง", "ศีรษะ", "หลัง", "หน้าอก", "เชิงกราน", "ขาหนีบ"))

    def _pain_location_choices(self, group):
        name = group.get("group_name_th", "") + " " + " ".join(group.get("keywords", []))
        choices = []
        for label in ("ท้อง", "หลัง", "เชิงกราน", "ขาหนีบ", "ยอดอก/ท้องบน"):
            if any(part in name for part in label.split("/")) and label not in choices:
                choices.append(label)
        if choices:
            choices.append("อื่น ๆ")
        return choices[:6]

    def _question_by_text(self, group, text):
        for question in group.get("questions", []):
            if text in question.get("question_th", ""):
                return question
        return None

    def _parse_choices(self, value):
        raw = (value or "").strip()
        if not raw or raw == "[]":
            return []
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(item) for item in data if str(item).strip()]
        except Exception:
            pass
        return [item.strip().strip('"') for item in raw.strip("[]").split(",") if item.strip()]

    def _contains_affirmed_symptom(self, text, term):
        raw = str(text or "")
        if term not in raw:
            return False
        compact = re.sub(r"\s+", "", raw)
        negative_patterns = [
            "ไม่มี" + term,
            "ไม่" + term,
            "ไม่ได้" + term,
            "ไม่มีอาการ" + term,
        ]
        return not any(pattern in compact for pattern in negative_patterns)

    def _extract_first_int(self, text):
        translated = str(text).translate(str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789"))
        match = re.search(r"\d+", translated)
        if not match:
            return None
        return int(match.group(0))

    def _prefill_yellow_details(self, group, state):
        details = state.setdefault("yellow_details", {})
        questions = state.get("yellow_detail_questions", [])
        question_by_key = {question["key"]: question for question in questions}
        if "pain_location" not in details and "pain_location" in question_by_key:
            inferred = self._infer_pain_location(state, question_by_key["pain_location"].get("choices", []))
            if inferred:
                question = question_by_key["pain_location"]
                details["pain_location"] = {
                    "at": utc_now(),
                    "key": "pain_location",
                    "label": question.get("label", "ตำแหน่งอาการ"),
                    "question": question["question"],
                    "answer": inferred,
                    "value": inferred,
                    "type": "inferred",
                    "source_rule_ids": question.get("source_rule_ids", []),
                    "note": "inferred from user's symptom text; supplemental observation only",
                }

    def _infer_pain_location(self, state, choices):
        text = self._conversation_context_text(state)
        mapping = [
            ("ยอดอก/ท้องบน", ("ยอดอก", "ท้องบน", "จุกยอดอก")),
            ("เชิงกราน", ("เชิงกราน",)),
            ("ขาหนีบ", ("ขาหนีบ",)),
            ("ท้อง", ("ปวดท้อง", "ท้อง")),
            ("หลัง", ("ปวดหลัง", "หลัง", "บั้นเอว")),
        ]
        for choice, terms in mapping:
            if choice in choices and any(term in text for term in terms):
                return choice
        return ""

    def _onset_question_text(self, group, main_text):
        if main_text:
            if self._contains_affirmed_symptom(main_text, "ปวด") or self._contains_affirmed_symptom(main_text, "เจ็บ"):
                pain_label = self._pain_detail_label(group, main_text)
                if pain_label:
                    return "เริ่ม{0}ตั้งแต่เมื่อไหร่?".format(pain_label)
            symptom = self._followup_context_label({"observations": [{"main_symptom_text": main_text}]})
            if symptom:
                return "เริ่มมีอาการ{0}ตั้งแต่เมื่อไหร่?".format(symptom)
        pain_label = self._pain_detail_label(group, "")
        if pain_label and not self._breathing_context_without_pain(group.get("group_name_th", "")):
            return "เริ่ม{0}ตั้งแต่เมื่อไหร่?".format(pain_label)
        symptom = self._followup_context_label({"observations": [{"main_symptom_text": main_text}]})
        if symptom:
            return "เริ่มมีอาการ{0}ตั้งแต่เมื่อไหร่?".format(symptom)
        return "เริ่มเป็นเมื่อไหร่?"

    def _scale_flex(self, question, body=None):
        return {
            "type": "flex",
            "template": "scale_0_10",
            "title": question.get("label", "ระดับอาการ"),
            "body": body or question.get("body") or question["question"],
            "actions": [{"label": str(i), "text": str(i)} for i in range(0, 11)],
            "metadata": {
                "detail_key": question.get("key", ""),
                "source_rule_ids": question.get("source_rule_ids", []),
            },
        }

    def _choice_flex(self, question):
        return {
            "type": "flex",
            "template": "choice_buttons",
            "title": question.get("label", "เลือกคำตอบ"),
            "body": question.get("body") or question["question"],
            "actions": [{"label": choice, "text": choice} for choice in question.get("choices", [])],
            "metadata": {
                "detail_key": question.get("key", ""),
                "source_rule_ids": question.get("source_rule_ids", []),
            },
        }

    def _screening_rules(self, group, level, state):
        if not group:
            return []
        rules = []
        red_rules = []
        if level == "yellow" and state.get("red_bundle_done"):
            red_rules = [
                self._find_rule_or_none(group, rule_id)
                for rule_id in state.get("red_bundle_rule_ids", [])
            ]
            red_rules = [rule for rule in red_rules if rule]
        for rule in group.get("rules", []):
            if rule.get("level") != level:
                continue
            if level == "red" and rule.get("rule_id") in set(state.get("red_checked_rule_ids") or []):
                continue
            if level == "red" and self._skip_rule_for_self_checkin(rule, state):
                state.setdefault("skip_questions", []).append(rule["rule_id"])
                continue
            if level == "yellow" and self._skip_uncertain_detail_rule_for_self_checkin(rule, state):
                state.setdefault("skip_questions", []).append(rule["rule_id"])
                continue
            if level == "yellow" and self._yellow_duplicates_checked_red(rule, red_rules):
                state.setdefault("skip_questions", []).append(rule["rule_id"])
                continue
            if not rule.get("user_friendly_check"):
                continue
            rules.append(rule)
        return self._dedupe_screening_rules(rules, level, state)

    def _dedupe_screening_rules(self, rules, level, state):
        deduped = []
        seen = set()
        for rule in rules:
            key = self._rule_overlap_key(rule, level)
            if key in seen:
                state.setdefault("skip_questions", []).append(rule["rule_id"])
                continue
            seen.add(key)
            deduped.append(rule)
        return deduped

    def _rule_overlap_key(self, rule, level):
        families = sorted(self._risk_families(rule))
        if families:
            return level + ":family:" + ",".join(families)
        text = self._question_to_statement(rule.get("user_friendly_check", "") or rule.get("condition_from_pdf", ""))
        text = re.sub(r"\s+", "", text.lower())
        text = text.replace("ใช่", "").replace("หรือไม่", "").replace("ไหม", "")
        return level + ":text:" + text

    def _skip_uncertain_detail_rule_for_self_checkin(self, rule, state):
        if state.get("session_mode") != "self_checkin" or not state.get("user_can_chat", True):
            return False
        text = (rule.get("condition_from_pdf") or "") + " " + (rule.get("user_friendly_check") or "")
        blocked_fragments = (
            "ยืนยันรายละเอียด",
            "ผู้แจ้งยืนยัน",
            "หน่วยงาน",
            "องค์กร/ผู้เฝ้าระวัง",
            "ผู้เฝ้าระวังสุขภาพ",
            "อาจวิกฤต",
            "ตาม PDF",
        )
        return any(fragment in text for fragment in blocked_fragments)

    def _contextual_yellow_rules(self, rules, state):
        context = self._conversation_context_text(state)
        if not context:
            return rules
        normalized_context = self._normalized_symptom_text(context)
        filtered = []
        for rule in rules:
            if self._yellow_rule_unrelated_to_context(rule, normalized_context):
                state.setdefault("skip_questions", []).append(rule["rule_id"])
                continue
            filtered.append(rule)
        if not filtered:
            return rules
        return sorted(filtered, key=lambda rule: self._yellow_context_score(rule, normalized_context), reverse=True)

    def _auto_match_yellow_from_context(self, session, user_id, group, rules, state, console):
        context = self._conversation_context_text(state)
        if not context:
            return
        state.setdefault("yellow_answers", {})
        matched_rule_ids = []
        for rule in rules:
            rule_id = rule.get("rule_id", "")
            if not rule_id or rule_id in state["yellow_answers"]:
                continue
            reason = self._yellow_context_match_reason(rule, context)
            if not reason:
                continue
            context_answer = self._last_main_symptom_text(state) or self._context_excerpt(context)
            state["yellow_answers"][rule_id] = {
                "answer": context_answer,
                "matched": True,
                "normalized_answer": "yes",
                "confidence": 0.8,
                "reason_for_backend": "user already mentioned this yellow condition before follow-up: " + reason,
                "source_ref": rule.get("source_ref", ""),
            }
            if rule_id not in state.setdefault("auto_matched_rule_ids", []):
                state["auto_matched_rule_ids"].append(rule_id)
            observation = {
                "at": utc_now(),
                "type": "yellow_context_auto_match",
                "rule_id": rule_id,
                "matched": True,
                "reason": reason,
                "context_excerpt": context_answer,
            }
            state.setdefault("observations", []).append(observation)
            self.db.record_observation(
                session["session_id"],
                user_id,
                group.get("group_id", ""),
                "yellow",
                observation,
            )
            matched_rule_ids.append(rule_id)
        if matched_rule_ids:
            console.append(
                self._event(
                    "flow.yellow.context_match",
                    "auto-matched yellow rules already stated by the user, avoiding repeated questions",
                    {"rule_ids": matched_rule_ids},
                )
            )

    def _yellow_context_match_reason(self, rule, context):
        rule_text = " ".join([rule.get("condition_from_pdf", ""), rule.get("user_friendly_check", "")])
        normalized_rule = self._normalized_symptom_text(rule_text)

        if "ยืนยันรายละเอียด" in rule_text or "ผู้แจ้งยืนยัน" in rule_text:
            return ""

        def rule_has_any(terms):
            return any(self._normalized_symptom_text(term) in normalized_rule for term in terms)

        def context_has_any(terms):
            return self._context_has_any_affirmed(context, terms)

        pain_terms = ["ปวด", "เจ็บ", "ปวดท้อง", "ปวดหลัง", "ปวดหัว", "ปวดศีรษะ"]
        if rule_has_any(["ปวดร่วมกับอาเจียน"]) or (rule_has_any(["ปวด"]) and rule_has_any(["อาเจียน"])):
            if context_has_any(pain_terms) and context_has_any(["อาเจียน", "อ้วก"]):
                return "pain_and_vomiting"
            return ""

        matchers = [
            ("dizziness", ["เวียนศีรษะ", "เวียนหัว", "หัวหมุน", "มึนหัว"]),
            ("breathing_discomfort", ["หายใจขัด", "หายใจลำบาก", "หายใจเหนื่อย", "หายใจไม่ทัน", "หายใจไม่ออก", "หอบ", "เหนื่อยหอบ", "เหนื่อย"]),
            ("vision_difficulty", ["มองเห็นลำบาก", "เห็นภาพซ้อน", "ตามัว", "มองไม่ชัด"]),
            ("confusion", ["สับสน", "ตอบไม่ตรง", "พูดไม่ปะติดปะต่อ", "พูดลำบาก"]),
            ("weakness_or_numbness", ["อ่อนแรง", "ชา", "ซ่า"]),
            ("fatigue", ["เพลียมาก", "อ่อนเพลีย"]),
            ("fainting", ["หมดสติ", "วูบ", "เกือบหมดสติ"]),
            ("bleeding", ["เลือดออก"]),
            ("nosebleed", ["เลือดกำเดา", "กำเดา"]),
            ("chest_tightness", ["เจ็บแน่นทรวงอก", "แน่นหน้าอก", "เจ็บหน้าอก", "จุกเสียดลิ้นปี่"]),
            ("palpitation", ["ใจสั่น", "หัวใจเต้นเร็ว"]),
            ("vomiting", ["อาเจียน", "อ้วก"]),
        ]
        for reason, terms in matchers:
            if rule_has_any(terms) and context_has_any(terms):
                return reason
        return ""

    def _yellow_rule_unrelated_to_context(self, rule, context):
        text = " ".join([rule.get("condition_from_pdf", ""), rule.get("user_friendly_check", "")])
        if any(fragment in text for fragment in ("หน่วยงาน", "องค์กร/ผู้เฝ้าระวัง", "ผู้เฝ้าระวังสุขภาพ", "อาจวิกฤต", "ตาม PDF")):
            return True
        if ("หน้า" in text or "ลำคอ" in text or "คอ" in text) and "กัด" in text:
            return not any(term in context for term in ("หน้า", "ใบหน้า", "คอ", "ลำคอ"))
        checks = [
            ("เลือดกำเดา", ("เลือดกำเดา", "กำเดา", "จมูก")),
            ("ช่องคลอด", ("ช่องคลอด", "ประจำเดือน", "ตั้งครรภ์", "ครรภ์")),
        ]
        for marker, allowed_terms in checks:
            if marker in text and not any(term in context for term in allowed_terms):
                return True
        return False

    def _yellow_context_score(self, rule, context):
        text = " ".join([rule.get("condition_from_pdf", ""), rule.get("user_friendly_check", "")])
        score = 0
        for keyword in self._rule_keywords(rule):
            if self._normalized_symptom_text(keyword) in context:
                score += 3
        for term in ("เลือด", "เลือดออก", "ปวด", "อาเจียน", "หายใจ", "อ่อนแรง", "เพลีย", "หมดสติ"):
            if term in text and term in context:
                score += 2
        return score

    def _conversation_context_text(self, state):
        parts = []
        for item in state.get("observations", []):
            for key in ("main_symptom_text", "answer"):
                value = str(item.get(key, "")).strip()
                if value:
                    parts.append(value)
        for answer in (state.get("yellow_answers") or {}).values():
            value = str(answer.get("answer", "")).strip()
            if value:
                parts.append(value)
        return " ".join(parts)

    def _normalized_symptom_text(self, text):
        normalized = str(text or "").lower()
        normalized = re.sub(r"\s+", "", normalized)
        replacements = [
            ("เวียนหัว", "เวียนศีรษะ"),
            ("หัวหมุน", "เวียนศีรษะ"),
            ("มึนหัว", "เวียนศีรษะ"),
            ("ปวดหัว", "ปวดศีรษะ"),
            ("อ้วก", "อาเจียน"),
            ("หายใจเหนื่อย", "หายใจขัด"),
            ("เหนื่อยหอบ", "หายใจขัด"),
            ("หายใจไม่ทัน", "หายใจขัด"),
            ("หายใจไม่ออก", "หายใจขัด"),
            ("หายใจไม่สะดวก", "หายใจขัด"),
            ("หายใจติด", "หายใจขัด"),
            ("หอบ", "หายใจขัด"),
            ("หายใจลำบาก", "หายใจขัด"),
            ("มองไม่ชัด", "มองเห็นลำบาก"),
            ("ตามัว", "มองเห็นลำบาก"),
            ("เห็นภาพซ้อน", "มองเห็นลำบาก"),
            ("เจ็บหน้าอก", "เจ็บแน่นทรวงอก"),
            ("แน่นหน้าอก", "เจ็บแน่นทรวงอก"),
            ("วูบ", "หมดสติชั่ววูบ"),
        ]
        for source, target in replacements:
            normalized = normalized.replace(source, target)
        return normalized

    def _context_has_any_affirmed(self, context, terms):
        for term in terms:
            for variant in self._symptom_variants(term):
                if self._contains_affirmed_symptom(context, variant):
                    return True
        normalized_context = self._normalized_symptom_text(context)
        for term in terms:
            normalized_term = self._normalized_symptom_text(term)
            if normalized_term and normalized_term in normalized_context and not self._normalized_negates_term(normalized_context, normalized_term):
                return True
        return False

    def _normalized_negates_term(self, normalized_context, normalized_term):
        negative_patterns = [
            "ไม่มี" + normalized_term,
            "ไม่" + normalized_term,
            "ไม่ได้" + normalized_term,
            "ไม่มีอาการ" + normalized_term,
        ]
        return any(pattern in normalized_context for pattern in negative_patterns)

    def _symptom_variants(self, term):
        term = str(term or "").strip()
        families = [
            ["เวียนศีรษะ", "เวียนหัว", "หัวหมุน", "มึนหัว"],
            ["ปวดศีรษะ", "ปวดหัว"],
            ["อาเจียน", "อ้วก"],
            ["หายใจขัด", "หายใจลำบาก", "หายใจเหนื่อย", "หายใจไม่ทัน", "หายใจไม่ออก", "หายใจไม่สะดวก", "หายใจติด", "หอบ", "เหนื่อยหอบ", "เหนื่อย"],
            ["มองเห็นลำบาก", "มองไม่ชัด", "ตามัว", "เห็นภาพซ้อน"],
            ["เจ็บแน่นทรวงอก", "แน่นหน้าอก", "เจ็บหน้าอก"],
            ["หมดสติ", "วูบ", "เกือบหมดสติ", "หมดสติชั่ววูบ"],
        ]
        variants = [term] if term else []
        for family in families:
            if term in family:
                variants.extend(family)
                break
        return list(dict.fromkeys([item for item in variants if item]))

    def _context_excerpt(self, context, limit=120):
        text = re.sub(r"\s+", " ", str(context or "")).strip()
        if len(text) <= limit:
            return text
        return text[:limit].strip()

    def _yellow_duplicates_checked_red(self, yellow_rule, red_rules):
        yellow_families = self._risk_families(yellow_rule)
        if not yellow_families:
            return False
        for red_rule in red_rules:
            red_families = self._risk_families(red_rule)
            if yellow_families & red_families:
                return True
        return False

    def _risk_families(self, rule):
        text = " ".join(
            [
                rule.get("condition_from_pdf", ""),
                rule.get("user_friendly_check", ""),
            ]
        )
        families = set()
        if "หายใจ" in text or "พูดได้แค่" in text or "นั่งพิง" in text:
            families.add("breathing")
        if "ช็อก" in text or "เหงื่อ" in text or "ซีด" in text or "เกือบหมดสติ" in text or "อ่อนแรงมาก" in text:
            families.add("shock")
        if "ห้ามไม่หยุด" in text or "เลือดห้ามไม่หยุด" in text:
            families.add("uncontrolled_bleeding")
        if "หมดสติ" in text or "ไม่รู้สึกตัว" in text or "ไม่ตอบสนอง" in text:
            families.add("consciousness")
        if "อายุ" in text and ("ปวดท้อง" in text or "ปวดหลัง" in text or "ท้องบน" in text or "ยอดอก" in text):
            families.add("age_pain")
        return families

    def _red_bundle_text(self, group, rules):
        lines = [
            "ขอเช็กอาการแจ้งเตือนแดงก่อน",
            "ตอนนี้มีข้อใดข้อหนึ่งต่อไปนี้ไหม?",
        ]
        for rule in rules:
            lines.append("- " + self._question_to_statement(rule["user_friendly_check"]))
        lines.append("กดปุ่ม: ใช่ / ไม่ใช่")
        return "\n".join(lines)

    def _red_bundle_flex(self, group, rules):
        return {
            "type": "flex",
            "template": "red_bundle_confirm",
            "title": "เช็กอาการแดง",
            "body": self._red_bundle_text(group, rules),
            "actions": [
                {"label": "ใช่", "text": "ใช่"},
                {"label": "ไม่ใช่", "text": "ไม่ใช่"},
            ],
            "metadata": {
                "group_id": group.get("group_id", ""),
                "rule_ids": [rule["rule_id"] for rule in rules],
            },
        }

    def _history_flex(self, session_id, risk_level):
        return {
            "type": "flex",
            "template": "history_button",
            "title": "ประวัติการซักถาม",
            "body": "กดเพื่อดูคำถามและคำตอบที่ระบบเก็บไว้ในรอบนี้",
            "actions": [
                {"label": "ดูประวัติที่ซักถาม", "text": "/history {0}".format(int(session_id))},
            ],
            "metadata": {
                "session_id": int(session_id),
                "risk_level": risk_level,
            },
        }

    def _patient_risk_reply(self, risk_level, alert=None):
        alert_line = self._patient_alert_line(alert)
        if risk_level == "red":
            return "\n".join(
                [
                    "ประเมินความรุนแรงระดับสีแดงจากข้อมูลที่ตอบ",
                    "แนะนำให้ไปโรงพยาบาลทันที หรือโทร 1669 หากต้องการความช่วยเหลือฉุกเฉิน",
                    alert_line,
                    "กดปุ่มด้านล่างเพื่อดูประวัติที่ระบบซักถาม",
                ]
            )
        if risk_level == "yellow":
            return "\n".join(
                [
                    "ประเมินความรุนแรงระดับสีเหลืองจากข้อมูลที่ตอบ",
                    "แนะนำให้ไปโรงพยาบาลเพื่อประเมินเพิ่มเติม",
                    alert_line,
                    "กดปุ่มด้านล่างเพื่อดูประวัติที่ระบบซักถาม",
                ]
            )
        if risk_level == "green":
            return "\n".join(
                [
                    "บันทึกแล้ว: ประเมินความรุนแรงระดับสีเขียวจากข้อมูลที่ตอบ",
                    "ยังไม่พบเกณฑ์แจ้งเตือนแดงหรือเหลืองจากชุดคำถามนี้",
                    "ระบบจะรอส่งรายงานประจำวันให้ผู้ดูแลตาม config",
                ]
            )
        return "ยังมีข้อมูลไม่พอสำหรับสรุประดับความเสี่ยงจากข้อมูลที่ตอบ"

    def _patient_alert_line(self, alert):
        if not alert:
            return "ระบบเข้าสู่ alert flow แล้ว"
        if alert.get("delivered"):
            return "ระบบส่งแจ้งเตือนไปยังผู้ดูแลแล้ว"
        return "ระบบบันทึก alert แล้ว แต่ยังส่งถึงผู้ดูแลไม่ได้ เพราะยังไม่ได้ผูกผู้ดูแลหรือยังไม่มี consent"

    def _yellow_open_question(self, rule):
        clause = self._yellow_topic_clause(self._yellow_topic(rule), {})
        if clause:
            return "ขอเช็กต่ออีกนิดนะ {0}".format(clause)
        return "ขอเช็กต่ออีกนิดนะ เล่าอาการส่วนนี้ให้ฟังสั้น ๆ ได้เลย"

    def _yellow_summary_question(self, group, rules, state=None):
        state = state or {}
        clauses = [
            self._yellow_topic_clause(self._contextual_yellow_topic(self._yellow_topic(rule), state), state)
            for rule in rules
        ]
        clauses = [clause for index, clause in enumerate(clauses) if clause and clause not in clauses[:index]]
        context_label = self._followup_context_label(state)
        if not clauses:
            if context_label:
                return "ขอเช็กต่ออีกนิดนะ ตอนนี้อาการ{0}เป็นอย่างไรบ้าง".format(context_label)
            return "ขอเช็กต่ออีกนิดนะ ตอนนี้อาการเป็นอย่างไรบ้าง"
        clause_text = self._join_yellow_clauses(clauses)
        if context_label and not clauses[0].startswith("เลือดที่"):
            return "ขอเช็กต่ออีกนิดนะ อาการ{0}ครั้งนี้{1}".format(context_label, clause_text)
        return "ขอเช็กต่ออีกนิดนะ {0}".format(clause_text)

    def _join_yellow_clauses(self, clauses):
        if len(clauses) == 1:
            return clauses[0]
        if len(clauses) == 2:
            return clauses[0] + " และ" + clauses[1]
        return ", ".join(clauses[:-1]) + " และ" + clauses[-1]

    def _yellow_topic_clause(self, topic, state):
        topic = (topic or "").strip()
        if not topic:
            return ""
        if topic == "ปวดร่วมกับอาเจียน":
            return "มีอาเจียนร่วมด้วยไหม"
        if topic == "หายใจขัด":
            return "หายใจขัดร่วมด้วยไหม"
        if topic == "อ่อนแรงหรือเพลียมาก":
            return "มีอ่อนแรงหรือเพลียมากร่วมด้วยไหม"
        if topic == "เวียนศีรษะ":
            return "เวียนหัวร่วมด้วยไหม"
        if topic == "มองเห็นลำบาก":
            return "มองเห็นลำบากไหม"
        if topic == "วันนี้หมดสติหรือเกือบหมดสติหลายครั้ง":
            return "วันนี้มีหมดสติหรือเกือบหมดสติหลายครั้งไหม"
        if topic.startswith("เลือดที่"):
            return topic
        if topic.endswith("ไหม"):
            return topic
        if topic.endswith("อยู่"):
            return topic + "ไหม"
        if topic.startswith(("มี", "ยัง", "เคย", "ก่อน", "ตอนนี้", "เด็ก")):
            return topic + "ไหม"
        return "มี{0}ไหม".format(topic)

    def _contextual_yellow_topic(self, topic, state):
        location = self._bleeding_location(state)
        if location and topic == "มีเลือดออกจากร่างกายส่วนใดอยู่":
            return "เลือดที่{0}ยังออกอยู่แค่ไหน".format(location)
        return topic

    def _followup_context_label(self, state):
        text = self._last_main_symptom_text(state)
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 40:
            text = text[:40].strip()
        return text

    def _last_main_symptom_text(self, state):
        for item in reversed(state.get("observations", [])):
            value = str(item.get("main_symptom_text", "")).strip()
            if value:
                return value
        return ""

    def _bleeding_location(self, state):
        text = self._last_main_symptom_text(state)
        if "เลือด" not in text:
            return ""
        for location in ("แขน", "ขา", "มือ", "เท้า", "นิ้ว", "หน้า", "ใบหน้า", "คอ", "ลำคอ", "หัว", "ศีรษะ", "จมูก"):
            if location in text:
                return location
        return ""

    def _yellow_topic(self, rule):
        text = self._question_to_statement(rule.get("user_friendly_check", ""))
        replacements = {
            "ถูกกัดที่หน้า หรือคอ แต่เลือดหยุดแล้ว": "แผลอยู่แถวหน้า/คอแต่เลือดหยุดแล้ว",
            "หายใจขัด": "หายใจขัด",
            "เวียนศีรษะหรือทรงตัวผิดปกติ": "เวียนหัวหรือทรงตัวไม่ค่อยไหว",
            "อ่อนแรงหรือเจ็บปวดทั่วร่างกาย": "อ่อนแรงมากหรือปวดเมื่อยทั้งตัว",
            "ยืนยันรายละเอียดอาการไม่ได้ใช่": "ยังไม่แน่ใจรายละเอียดอาการ",
            "ยืนยันรายละเอียดอาการไม่ได้": "ยังไม่แน่ใจรายละเอียดอาการ",
        }
        return replacements.get(text, text)

    def _evaluate_yellow_summary_answer(self, user, session, text, rules, state, console, usage_delta):
        local_answer = self._answer_value(text)
        if local_answer == "no":
            return {
                rule["rule_id"]: {
                    "matched": False,
                    "normalized_answer": "no",
                    "confidence": 1,
                    "reason_for_backend": "explicit no for yellow summary",
                }
                for rule in rules
            }
        if local_answer == "yes":
            return {
                rule["rule_id"]: {
                    "matched": True,
                    "normalized_answer": "yes",
                    "confidence": 0.65,
                    "reason_for_backend": "explicit yes to yellow summary question",
                }
                for rule in rules
            }
        if self.llm.enabled and self._config(user).get("llm_first"):
            payload = {
                "purpose": "yellow_summary_eval",
                "message": text,
                "session_state": state,
                "rules": [
                    {
                        "rule_id": rule.get("rule_id", ""),
                        "risk_level": rule.get("level", ""),
                        "condition_from_pdf": rule.get("condition_from_pdf", ""),
                        "user_friendly_check": rule.get("user_friendly_check", ""),
                        "source_ref": rule.get("source_ref", ""),
                    }
                    for rule in rules
                ],
                "return_json_schema": {
                    "matched_rule_ids": ["exact yellow rule IDs from supplied rules only"],
                    "rule_evaluations": [
                        {
                            "rule_id": "exact rule_id",
                            "matched": "true only if answer clearly satisfies this exact yellow rule",
                            "confidence": "0.0-1.0",
                            "reason_for_backend": "short rule-id based note, no diagnosis",
                        }
                    ],
                },
                "hard_rules": [
                    "Use only the supplied yellow rules and the user's answer.",
                    "Do not diagnose.",
                    "Do not add medical knowledge.",
                    "If unclear, do not match the rule.",
                ],
            }
            result = self.llm.generate_json(
                self.system_prompt,
                json.dumps(payload, ensure_ascii=False),
                "yellow_summary_eval",
            )
            self._record_llm(session, user["user_id"], result, "yellow_summary_eval", console, usage_delta)
            data = result.get("data") or {}
            if result.get("ok") and isinstance(data, dict):
                by_id = {}
                for item in data.get("rule_evaluations") or []:
                    if not isinstance(item, dict):
                        continue
                    rule_id = item.get("rule_id", "")
                    if not self._find_rule_or_none({"rules": rules}, rule_id):
                        continue
                    confidence = float(item.get("confidence", 0) or 0)
                    by_id[rule_id] = {
                        "matched": bool(item.get("matched")) and confidence >= 0.45,
                        "normalized_answer": "yes" if item.get("matched") else "no",
                        "confidence": confidence,
                        "reason_for_backend": item.get("reason_for_backend", ""),
                    }
                matched_ids = set(self._extract_rule_ids(data.get("matched_rule_ids")))
                for rule in rules:
                    if rule["rule_id"] not in by_id:
                        by_id[rule["rule_id"]] = {
                            "matched": rule["rule_id"] in matched_ids,
                            "normalized_answer": "yes" if rule["rule_id"] in matched_ids else "unknown",
                            "confidence": 0.55 if rule["rule_id"] in matched_ids else 0,
                            "reason_for_backend": "matched_rule_ids fallback",
                        }
                return by_id
        return self._evaluate_yellow_summary_locally(text, rules)

    def _evaluate_yellow_summary_locally(self, text, rules):
        normalized = text.lower()
        normalized_symptom_text = self._normalized_symptom_text(text)
        result = {}
        for rule in rules:
            keywords = self._rule_keywords(rule)
            matched = any(
                keyword
                and (
                    keyword in normalized
                    or self._normalized_symptom_text(keyword) in normalized_symptom_text
                )
                for keyword in keywords
            )
            result[rule["rule_id"]] = {
                "matched": matched,
                "normalized_answer": "yes" if matched else "unknown",
                "confidence": 0.6 if matched else 0,
                "reason_for_backend": "local keyword match for yellow summary",
            }
        return result

    def _rule_keywords(self, rule):
        text = " ".join([rule.get("condition_from_pdf", ""), rule.get("user_friendly_check", "")]).lower()
        for connector in ["ร่วมกับ", "หรือ", "และ", "แต่", "อย่างน้อย", "แม้เพียงข้อเดียว", "ใช่ไหม", "ไหม"]:
            text = text.replace(connector, " ")
        text = text.replace("/", " ")
        raw = re.split(r"[\s/,()]+", text)
        stop = {
            "มี",
            "หรือ",
            "และ",
            "แต่",
            "ปวด",
            "ร่วมกับ",
            "อย่างไร",
            "อย่างน้อย",
            "ใช่ไหม",
            "ไหม",
            "ไม่ได้",
            "ผู้แจ้ง",
            "รายละเอียด",
            "อาการ",
        }
        keywords = []
        for item in raw:
            token = item.strip(" ?")
            if len(token) < 3 or token in stop:
                continue
            keywords.append(token)
        return keywords

    def _evaluate_yellow_open_answer(self, user, session, text, rule, state, console, usage_delta, llm_first=None):
        local_answer = self._answer_value(text, llm_first)
        if local_answer in ("yes", "no"):
            return {
                "matched": local_answer == "yes",
                "normalized_answer": local_answer,
                "confidence": 1,
                "reason_for_backend": "local explicit yes/no answer for open-ended yellow question",
            }
        if self.llm.enabled and self._config(user).get("llm_first"):
            payload = {
                "purpose": "yellow_answer_eval",
                "message": text,
                "session_state": state,
                "rule": {
                    "rule_id": rule.get("rule_id", ""),
                    "risk_level": rule.get("level", ""),
                    "condition_from_pdf": rule.get("condition_from_pdf", ""),
                    "user_friendly_check": rule.get("user_friendly_check", ""),
                    "source_ref": rule.get("source_ref", ""),
                },
                "return_json_schema": {
                    "matched": "true only if the answer clearly satisfies this exact yellow rule",
                    "normalized_answer": "yes | no | unknown",
                    "confidence": "0.0-1.0",
                    "reason_for_backend": "short rule-id based note, no diagnosis",
                },
                "hard_rules": [
                    "Use only this exact rule and the user's answer.",
                    "Do not diagnose.",
                    "Do not add medical knowledge.",
                    "If unclear, return matched=false and normalized_answer=unknown.",
                ],
            }
            result = self.llm.generate_json(
                self.system_prompt,
                json.dumps(payload, ensure_ascii=False),
                "yellow_answer_eval",
            )
            self._record_llm(session, user["user_id"], result, "yellow_answer_eval", console, usage_delta)
            data = result.get("data") or {}
            if result.get("ok") and isinstance(data, dict):
                matched = bool(data.get("matched")) and rule.get("level") == "yellow"
                confidence = float(data.get("confidence", 0) or 0)
                if confidence < 0.45:
                    matched = False
                return {
                    "matched": matched,
                    "normalized_answer": data.get("normalized_answer") or ("yes" if matched else local_answer),
                    "confidence": confidence,
                    "reason_for_backend": data.get("reason_for_backend", ""),
                }
        return {
            "matched": False,
            "normalized_answer": "unknown",
            "confidence": 0,
            "reason_for_backend": "local fallback could not interpret open-ended yellow answer",
        }

    def _bundle_rule(self, group, level, rules, condition):
        source_refs = self._source_refs(rules)
        bundle_group_id = group["group_id"].replace("+", "_")
        return {
            "rule_id": "{0}_{1}_BUNDLE".format(bundle_group_id, level.upper()),
            "level": level,
            "condition_from_pdf": condition,
            "user_friendly_check": condition,
            "answer_type": "bundle",
            "source_ref": source_refs,
            "stop_if_true": level in ("red", "yellow"),
        }

    def _source_refs(self, rules):
        refs = []
        for rule in rules:
            ref = rule.get("source_ref", "")
            if ref and ref not in refs:
                refs.append(ref)
        return "; ".join(refs)

    def _first_green_rule(self, group):
        for rule in (group or {}).get("rules", []):
            if rule.get("level") == "green":
                return rule
        return None

    def _question_to_statement(self, question):
        text = (question or "").strip()
        for suffix in ("ใช่ไหม?", "ใช่ไหม", "ไหม?", "ไหม", "?"):
            if text.endswith(suffix):
                text = text[: -len(suffix)].strip()
                break
        return text or question

    def _apply_llm_triage(self, user, session, user_id, text, state, console, usage_delta, llm_first):
        if not llm_first:
            return None
        group_id = self._llm_group_id(llm_first, state)
        group = self._active_group(state) if "+" in str(group_id) else self.corpus.get_group(group_id)
        if not group or group_id == "EMS11":
            return None
        if not state.get("active_group_id"):
            state["active_group_id"] = group_id
            state.setdefault("observations", []).append({"at": utc_now(), "main_symptom_text": text, "group_id": group_id})
            console.append(self._event("ems.group_selected", "selected symptom group from LLM triage", {"group_id": group_id}))

        matched_rules = self._validated_llm_matched_rules(group, llm_first, console)
        if matched_rules:
            rule = self._highest_severity_rule(matched_rules)
            state["pending_rule_id"] = ""
            state["pending_question"] = ""
            state["risk_level"] = rule["level"]
            if rule["rule_id"] not in [r.get("rule_id") for r in state.get("matched_rules", [])]:
                state.setdefault("matched_rules", []).append(rule)
            observation = {
                "at": utc_now(),
                "source": "llm_first_validated",
                "rule_id": rule["rule_id"],
                "answer": text,
                "matched": True,
                "llm_reason": llm_first.get("reason_for_backend", ""),
            }
            state.setdefault("observations", []).append(observation)
            self.db.record_observation(session["session_id"], user_id, group_id, rule["level"], observation)
            console.append(
                self._event(
                    "llm_triage.rule_match",
                    "accepted OpenAI rule match after Markdown validation",
                    {"group_id": group_id, "rule_id": rule["rule_id"], "risk_level": rule["level"]},
                )
            )
            if rule["level"] == "red":
                alert = self._make_alert(user, session, group, rule, text, state)
                reply = self._patient_risk_reply("red", alert)
                self._save_assistant(session, user_id, reply, state)
                self._close_with_summary(session, user_id, state, reply, console, usage_delta)
                return self._result(
                    [reply],
                    [alert],
                    state,
                    console,
                    usage_delta,
                    session["session_id"],
                    ui_messages=[self._history_flex(session["session_id"], "red")],
                )
            if rule["level"] == "yellow":
                state["risk_level"] = "insufficient"
                state.setdefault("yellow_answers", {})[rule["rule_id"]] = {
                    "answer": text,
                    "matched": True,
                    "normalized_answer": "yes",
                    "confidence": float(llm_first.get("confidence", 0) or 0),
                    "reason_for_backend": "OpenAI matched yellow rule after Markdown validation; alert deferred until remaining checks complete",
                    "source_ref": rule.get("source_ref", ""),
                }
                console.append(
                    self._event(
                        "llm_triage.yellow.defer_alert",
                        "accepted yellow rule but deferred alert until remaining checks and details are complete",
                        {"group_id": group_id, "rule_id": rule["rule_id"]},
                    )
                )
                return self._ask_next_yellow_or_finish(user, session, user_id, state, console, usage_delta)
            if rule["level"] == "green":
                reply = self._patient_risk_reply("green")
                self._save_assistant(session, user_id, reply, state)
                self._close_with_summary(session, user_id, state, reply, console, usage_delta)
                return self._result([reply], [], state, console, usage_delta, session["session_id"])

        planned = self._validated_llm_question(group, llm_first, state, console)
        if planned:
            state["pending_rule_id"] = planned["rule"]["rule_id"]
            state["pending_question"] = planned["question"]
            reply = self._natural_reply(planned["question"] + self._choices_line(planned["rule"]), llm_first)
            self._save_assistant(session, user_id, reply, state)
            console.append(
                self._event(
                    "llm_triage.ask",
                    "asked OpenAI-selected Markdown-backed question",
                    {"rule_id": planned["rule"]["rule_id"]},
                )
            )
            return self._result([reply], [], state, console, usage_delta, session["session_id"])
        return None

    def _llm_group_id(self, llm_first, state):
        active = state.get("active_group_id") or ""
        if "+" in active and state.get("active_group_ids"):
            return active
        if active in self.corpus.groups and active != "EMS11":
            return active
        for key in ("candidate_group_id", "group_id"):
            group_id = str(llm_first.get(key) or "").strip()
            if group_id in self.corpus.groups and group_id != "EMS11":
                return group_id
        return ""

    def _validated_llm_matched_rules(self, group, llm_first, console):
        rule_ids = self._extract_rule_ids(llm_first.get("matched_rule_ids"))
        if not rule_ids:
            rule_ids = self._extract_rule_ids(llm_first.get("matched_rules"))
        rules = []
        for rule_id in rule_ids:
            rule = self._find_rule_or_none(group, rule_id)
            if rule:
                rules.append(rule)
            else:
                console.append(
                    self._event(
                        "llm_triage.reject_rule",
                        "rejected OpenAI rule because it is not in active EMS Markdown group",
                        {"group_id": group["group_id"], "rule_id": rule_id},
                    )
                )
        return rules

    def _validated_llm_question(self, group, llm_first, state, console):
        questions = llm_first.get("questions_to_ask_next") or []
        if isinstance(questions, (str, dict)):
            questions = [questions]
        asked = set(state.get("asked_rule_ids") or [])
        pending = state.get("pending_rule_id") or ""
        for item in questions[:2]:
            if isinstance(item, dict):
                question = str(item.get("question_th") or item.get("question") or "").strip()
                rule_id = str(item.get("maps_to_rule_id") or item.get("rule_id") or "").strip()
            else:
                question = str(item or "").strip()
                ids = self._extract_rule_ids(question)
                rule_id = ids[0] if ids else ""
            rule = self._find_rule_or_none(group, rule_id)
            if not rule:
                console.append(
                    self._event(
                        "llm_triage.reject_question",
                        "rejected OpenAI question because maps_to_rule_id is missing or invalid",
                        {"group_id": group["group_id"], "maps_to_rule_id": rule_id},
                    )
                )
                continue
            if rule["rule_id"] in asked or rule["rule_id"] == pending:
                continue
            if self._skip_rule_for_self_checkin(rule, state):
                state.setdefault("skip_questions", []).append(rule["rule_id"])
                state.setdefault("asked_rule_ids", []).append(rule["rule_id"])
                console.append(
                    self._event(
                        "llm_triage.skip_question",
                        "skipped OpenAI question by self-check-in skip rule",
                        {"rule_id": rule["rule_id"]},
                    )
                )
                continue
            return {"rule": rule, "question": self._safe_llm_question(question, rule)}
        return None

    def _extract_rule_ids(self, value):
        if not value:
            return []
        found = []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    found.extend(self._extract_rule_ids(item.get("rule_id") or item.get("id") or ""))
                else:
                    found.extend(self._extract_rule_ids(str(item)))
            return list(dict.fromkeys(found))
        if isinstance(value, dict):
            return self._extract_rule_ids(value.get("rule_id") or value.get("id") or "")
        text = str(value)
        for rule_id in re.findall(r"EMS\d{2}_(?:RED|YELLOW|GREEN)_\d{2}", text):
            found.append(rule_id)
        return list(dict.fromkeys(found))

    def _find_rule_or_none(self, group, rule_id):
        if not group or not rule_id:
            return None
        for rule in group.get("rules", []):
            if rule.get("rule_id") == rule_id:
                return rule
        return None

    def _highest_severity_rule(self, rules):
        rank = {"red": 0, "yellow": 1, "green": 2}
        return sorted(rules, key=lambda rule: rank.get(rule.get("level"), 9))[0]

    def _safe_llm_question(self, question, rule):
        question = question.strip().strip('"').strip("'")
        blocked = ["ยา", "รักษา", "วินิจฉัย", "โรค", "ควรทำ", "กินอะไร", "ทำอย่างไรให้หาย"]
        if not question or len(question) > 160 or any(term in question for term in blocked):
            return rule["user_friendly_check"]
        return question

    def _choices_line(self, rule):
        if rule.get("answer_type") == "yes_no":
            return "\nตัวเลือก: ใช่ / ไม่ใช่"
        return ""

    def _next_rule_question(self, group_id, state):
        group = self.corpus.get_group(group_id)
        if not group:
            return None
        asked = set(state.get("asked_rule_ids") or [])
        ordered = [r for r in group["rules"] if r["level"] == "red"]
        ordered += [r for r in group["rules"] if r["level"] == "yellow"]
        ordered += [r for r in group["rules"] if r["level"] == "green"]
        for rule in ordered:
            if rule["rule_id"] in asked:
                continue
            if self._skip_rule_for_self_checkin(rule, state):
                asked.add(rule["rule_id"])
                state.setdefault("asked_rule_ids", []).append(rule["rule_id"])
                state.setdefault("skip_questions", []).append(rule["rule_id"])
                continue
            if not rule.get("user_friendly_check"):
                continue
            return rule
        return None

    def _skip_rule_for_self_checkin(self, rule, state):
        if state.get("session_mode") != "self_checkin" or not state.get("user_can_chat", True):
            return False
        text = (rule.get("user_friendly_check") or "") + " " + (rule.get("condition_from_pdf") or "")
        skip_terms = ["ไม่รู้สึกตัว", "ไม่ตอบสนอง", "กำลังชัก", "ไม่หายใจหลังหยุดชัก", "ตอบคำถามง่าย"]
        return any(term in text for term in skip_terms)

    def _finish_no_sourced_match(self, user, session, user_id, state, console, usage_delta):
        group = self._active_group(state)
        green_rules = [r for r in (group or {}).get("rules", []) if r["level"] == "green"]
        if green_rules:
            rule = green_rules[0]
            state["risk_level"] = "green"
            state["matched_rules"].append(rule)
            reply = self._patient_risk_reply("green")
        else:
            state["risk_level"] = "insufficient"
            reply = (
                "ยังไม่พบเกณฑ์ red/yellow จากคำตอบตอนนี้\n"
                "แต่ Markdown ไม่มีเกณฑ์ green ที่ชัดเจนสำหรับกลุ่มนี้ จึงบันทึกเป็น insufficient"
            )
        self.db.record_observation(
            session["session_id"],
            user_id,
            state.get("active_group_id", ""),
            state["risk_level"],
            {"final_state": state},
        )
        self._save_assistant(session, user_id, reply, state)
        self._close_with_summary(session, user_id, state, reply, console, usage_delta)
        return self._result([reply], [], state, console, usage_delta, session["session_id"])

    def _make_alert(self, user, session, group, rule, answer, state):
        caregiver = user.get("caregiver_user_id") or ""
        consent = bool(user.get("consent_to_share"))
        detail_block = self._alert_detail_block(state)
        message = (
            "[SIMULATED CAREGIVER ALERT]\n"
            "ผู้ใช้: {user_id}\n"
            "ระดับความเสี่ยงจากข้อมูลที่ตอบ: {risk}\n"
            "กลุ่ม: {group_id} {group_name}\n"
            "Rule: {rule_id}\n"
            "คำตอบล่าสุด: {answer}\n"
            "อ้างอิง: {source}\n"
            "{details}"
            "หมายเหตุ: เป็น alert จากเกณฑ์ check-in ไม่ใช่การวินิจฉัย"
        ).format(
            user_id=user["user_id"],
            risk=rule["level"],
            group_id=group["group_id"],
            group_name=group["group_name_th"],
            rule_id=rule["rule_id"],
            answer=answer,
            source=rule["source_ref"],
            details=detail_block,
        )
        delivered = bool(caregiver and consent)
        blocked_reason = "" if delivered else "missing linked caregiver or consent"
        self.db.record_alert(
            session["session_id"],
            user["user_id"],
            caregiver,
            rule["level"],
            group["group_id"],
            message,
            delivered,
            blocked_reason,
        )
        return {
            "to": caregiver if delivered else "",
            "delivered": delivered,
            "blocked_reason": blocked_reason,
            "message": message if delivered else "[BLOCKED] " + blocked_reason,
        }

    def _alert_detail_block(self, state):
        details = state.get("yellow_details") or {}
        lines = []
        for detail in details.values():
            label = detail.get("label") or detail.get("key") or "รายละเอียด"
            answer = detail.get("answer", "")
            if answer == "":
                continue
            lines.append("- {0}: {1}".format(label, answer))
        if not lines:
            return ""
        return "รายละเอียดเพิ่มเติม:\n{0}\n".format("\n".join(lines[:4]))

    def _close_with_summary(self, session, user_id, state, fallback_summary, console, usage_delta):
        short = self._short_summary(state, fallback_summary)
        long = ""
        status = "local_only"
        user = self.db.get_or_create_user(user_id)
        if self.llm.enabled and self._config(user).get("llm_session_summary"):
            raw = self.db.raw_chatlog(session["session_id"])
            payload = {
                "state": state,
                "chat_log": raw,
                "instruction": "Create short_conclusion and long_conclusion for future memory. No diagnosis.",
            }
            result = self.llm.generate_json(
                self.system_prompt,
                json.dumps(payload, ensure_ascii=False),
                "session_summary",
            )
            self._record_llm(session, user_id, result, "session_summary", console, usage_delta)
            data = result.get("data") or {}
            short = data.get("short_conclusion") or short
            long = data.get("long_conclusion") or ""
            status = "llm_ok" if result.get("ok") else "llm_failed"
        self.db.close_session(session["session_id"], short, long, status)

    def _llm_first(self, text, user, session, state, previous, recent, console, usage_delta):
        config = self._config(user)
        if not (self.llm.enabled and config.get("llm_first")):
            console.append(
                self._event(
                    "llm_first.skip",
                    "LLM-first disabled or OpenAI unavailable",
                    {"enabled": bool(config.get("llm_first")), "llm_enabled": self.llm.enabled},
                )
            )
            return None
        group = self._active_group(state)
        candidates = self.corpus.deterministic_group_match(text)
        candidate_group_rules = self._candidate_group_rules_for_prompt(state.get("active_group_id", ""), candidates)
        all_group_rule_index = [] if candidate_group_rules else self._all_group_rule_index_for_prompt()
        payload = {
            "purpose": "triage_planner",
            "message": text,
            "session_state": state,
            "active_group_markdown": (group or {}).get("markdown_excerpt", ""),
            "candidate_group_rules": candidate_group_rules,
            "all_group_rule_index": all_group_rule_index,
            "symptom_index": self.corpus.symptom_index_for_prompt(),
            "deterministic_candidates": candidates,
            "long_term_memory": previous,
            "recent_session_chat": recent[-10:],
            "user_personalized_prompt": user.get("personalized_prompt", ""),
            "task_instruction": [
                "Return every key in return_json_schema. Do not omit risk_level, matched_rule_ids, questions_to_ask_next, or source_refs.",
                "First compare the user's message with all_group_rule_index and candidate_group_rules.",
                "If the message already satisfies a red/yellow/green rule from the supplied context, put that exact rule_id in matched_rule_ids and set risk_level to that rule's risk_level.",
                "When the message contains both an incident/cause and a symptom, prefer a specific rule that contains both over a broad symptom-only group.",
                "If no exact rule is satisfied, set risk_level to insufficient and return one short question mapped to the most useful exact rule_id.",
            ],
            "return_json_schema": {
                "intent": "symptom_report | answer | daily_checkin | general_health | other",
                "normalized_answer": "yes | no | unknown",
                "candidate_group_id": "EMSxx or empty",
                "candidate_group_ids": ["EMSxx values for multiple distinct symptoms, or empty"],
                "confidence": "0.0-1.0",
                "risk_level": "red | yellow | green | insufficient",
                "matched_rule_ids": ["exact EMSxx_RED_yy/EMSxx_YELLOW_yy/EMSxx_GREEN_yy only, or empty"],
                "questions_to_ask_next": [
                    {
                        "question_th": "short Thai LINE-style question, max 1 question preferred",
                        "maps_to_rule_id": "exact rule_id from candidate_group_rules",
                    }
                ],
                "source_refs": ["source_ref values from matched rules, or empty"],
                "natural_prefix_th": "optional Thai prefix, max 18 words, no medical advice, no diagnosis",
                "reason_for_backend": "short engineering note",
            },
            "hard_rules": [
                "Do not diagnose.",
                "Do not invent red/yellow/green criteria.",
                "You may set red/yellow/green only when matched_rule_ids contains exact rule IDs from candidate_group_rules, all_group_rule_index, or active_group_markdown.",
                "If no exact rule ID matches the user's message, use risk_level insufficient.",
                "Always include every JSON key from return_json_schema.",
                "Ask only 1-2 short questions and each question must map to an exact rule_id.",
                "Use candidate_group_id only if supported by symptom_index or active_group_markdown.",
                "Use candidate_group_ids when the message clearly contains multiple distinct symptoms that map to different EMS groups.",
                "natural_prefix_th must not ask a new medical question and must not include advice.",
            ],
        }
        result = self.llm.generate_json(
            self.system_prompt,
            json.dumps(payload, ensure_ascii=False),
            "triage_planner",
        )
        self._record_llm(session, user["user_id"], result, "triage_planner", console, usage_delta)
        data = result.get("data") or {}
        if not result.get("ok"):
            return None
        if not isinstance(data, dict):
            return None
        if not data.get("candidate_group_id") and data.get("group_id"):
            data["candidate_group_id"] = data.get("group_id")
        if not data.get("candidate_group_ids") and data.get("group_ids"):
            data["candidate_group_ids"] = self._extract_group_ids(data.get("group_ids"))
        if not data.get("matched_rule_ids") and data.get("matched_rules"):
            data["matched_rule_ids"] = self._extract_rule_ids(data.get("matched_rules"))
        if not data.get("questions_to_ask_next"):
            data["questions_to_ask_next"] = data.get("next_questions") or []
        if not data.get("confidence") and data.get("candidate_group_id") in self.corpus.groups:
            data["confidence"] = 0.65
        if not data.get("natural_prefix_th"):
            data["natural_prefix_th"] = ""
        state["llm_first_last"] = {
            "intent": data.get("intent", ""),
            "normalized_answer": data.get("normalized_answer", ""),
            "candidate_group_id": data.get("candidate_group_id", ""),
            "candidate_group_ids": self._extract_group_ids(data.get("candidate_group_ids")),
            "confidence": data.get("confidence", 0),
            "risk_level": data.get("risk_level", ""),
            "matched_rule_ids": self._extract_rule_ids(data.get("matched_rule_ids")),
            "question_count": len(data.get("questions_to_ask_next") or []),
            "reason_for_backend": data.get("reason_for_backend", ""),
        }
        console.append(self._event("llm_first.result", "OpenAI interpreted current turn before deterministic flow", state["llm_first_last"]))
        return data

    def _candidate_group_rules_for_prompt(self, active_group_id, candidates):
        group_ids = []
        if active_group_id:
            group_ids.extend(self._extract_group_ids(active_group_id) or [active_group_id])
        for candidate in candidates[:3]:
            group_id = candidate.get("group_id")
            if group_id and group_id not in group_ids:
                group_ids.append(group_id)
        payload = {}
        for group_id in group_ids[:4]:
            group = self.corpus.get_group(group_id)
            if not group or group_id == "EMS11":
                continue
            payload[group_id] = {
                "group_name_th": group.get("group_name_th", ""),
                "rules": [
                    {
                        "rule_id": rule.get("rule_id", ""),
                        "risk_level": rule.get("level", ""),
                        "condition_from_pdf": rule.get("condition_from_pdf", ""),
                        "user_friendly_check": rule.get("user_friendly_check", ""),
                        "answer_type": rule.get("answer_type", ""),
                        "source_ref": rule.get("source_ref", ""),
                    }
                    for rule in group.get("rules", [])
                ],
                "question_bank": group.get("questions", [])[:8],
            }
        return payload

    def _all_group_rule_index_for_prompt(self):
        rows = []
        for group_id in sorted(self.corpus.groups):
            if group_id == "EMS11":
                continue
            group = self.corpus.groups[group_id]
            for rule in group.get("rules", []):
                rows.append(
                    {
                        "group_id": group_id,
                        "group_name_th": group.get("group_name_th", ""),
                        "rule_id": rule.get("rule_id", ""),
                        "risk_level": rule.get("level", ""),
                        "condition_from_pdf": rule.get("condition_from_pdf", ""),
                        "user_friendly_check": rule.get("user_friendly_check", ""),
                        "source_ref": rule.get("source_ref", ""),
                    }
                )
        return rows

    def _short_summary(self, state, fallback):
        group_id = state.get("active_group_id") or "daily_checkin"
        risk = state.get("risk_level") or "insufficient"
        rules = [r.get("rule_id") for r in state.get("matched_rules", [])]
        return "group={0}; risk={1}; matched_rules={2}; note={3}".format(
            group_id, risk, ",".join(rules), fallback[:160].replace("\n", " ")
        )

    def _record_llm(self, session, user_id, result, purpose, console, usage_delta):
        usage = result.get("usage") or {}
        if not result.get("skipped"):
            usage_delta["api_calls"] += 1
        usage_delta["prompt_tokens"] += int(usage.get("prompt_tokens", 0))
        usage_delta["completion_tokens"] += int(usage.get("completion_tokens", 0))
        usage_delta["total_tokens"] += int(usage.get("total_tokens", 0))
        self.db.record_llm_call(
            session["session_id"],
            user_id,
            "openai",
            self.llm.model,
            purpose,
            usage,
            purpose,
            result.get("raw_text", ""),
            result.get("error", ""),
        )
        console.append(
            self._event(
                "llm." + purpose,
                "OpenAI call " + ("skipped" if result.get("skipped") else "completed"),
                {
                    "ok": result.get("ok"),
                    "error": result.get("error"),
                    "usage": usage,
                    "latency_ms": result.get("latency_ms", 0),
                },
            )
        )

    def _config(self, user):
        defaults = {
            "daily_summary": True,
            "line_simulation": True,
            "llm_retrieval_assist": True,
            "llm_first": True,
            "llm_group_selection": True,
            "llm_session_summary": True,
        }
        try:
            config = json.loads(user.get("config_json") or "{}")
        except Exception:
            config = {}
        defaults.update(config)
        return defaults

    def _natural_reply(self, reply, llm_first):
        if not llm_first:
            return reply
        prefix = (llm_first.get("natural_prefix_th") or "").strip()
        if not prefix:
            return reply
        blocked = ["ยา", "รักษา", "วินิจฉัย", "โรค", "ควรทำ", "?", "ไหม", "มั้ย", "หรือไม่", "หรือเปล่า", "ใช่ไหม"]
        if any(term in prefix for term in blocked):
            return reply
        if len(prefix) > 120:
            prefix = prefix[:120].strip()
        return prefix + "\n" + reply

    def _handle_command(self, text, session, user_id, state, console):
        lowered = text.lower()
        history_match = re.match(r"^(?:/history|history|ดูประวัติ(?:ที่ซักถาม)?)(?:\s+(\d+))?$", lowered)
        if history_match:
            session_id = int(history_match.group(1) or session["session_id"])
            target = self.db.get_session(session_id)
            if not target or target.get("user_id") != user_id:
                console.append(self._event("flow.history.blocked", "history request was not owned by this user", {"session_id": session_id}))
                return "ไม่สามารถแสดงประวัติรอบนี้ได้"
            console.append(self._event("flow.history", "returned screening history for session", {"session_id": session_id}))
            return self._screening_history_text(target)
        if lowered in ("/reset", "reset", "เริ่มใหม่"):
            self.db.close_session(session["session_id"], "manual reset", "", "manual")
            new_session = self.db.start_session(user_id, state.get("session_mode", "self_checkin"))
            new_state = self._state(new_session)
            state.clear()
            state.update(new_state)
            console.append(self._event("flow.reset", "closed current session and started new session", {}))
            return "เริ่ม session ใหม่แล้ว\nพิมพ์ “เช็กอิน” หรืออาการหลักได้เลย"
        if lowered in ("/help", "help"):
            return "พิมพ์ “เช็กอิน” เพื่อเริ่ม หรือพิมพ์อาการผิดปกติ เช่น “หายใจขัด”\nระบบนี้ไม่วินิจฉัยและไม่ตอบคำถามสุขภาพทั่วไป"
        return ""

    def _screening_history_text(self, session):
        history_state = self._state(session)
        group = self._active_group(history_state)
        lines = ["ประวัติการซักถามรอบนี้"]
        main_symptom = self._last_main_symptom_text(history_state)
        if main_symptom:
            lines.append("- อาการที่แจ้ง: {0}".format(main_symptom))
        risk = history_state.get("risk_level") or "insufficient"
        lines.append("- ผลประเมินล่าสุด: {0}".format(self._risk_label_th(risk)))

        asked_lines = self._screening_history_answer_lines(history_state, group)
        if asked_lines:
            lines.append("")
            lines.append("คำถามและคำตอบที่เก็บไว้:")
            lines.extend(asked_lines[:12])

        detail_lines = self._screening_history_detail_lines(history_state)
        if detail_lines:
            lines.append("")
            lines.append("รายละเอียดเพิ่มเติม:")
            lines.extend(detail_lines[:8])

        lines.append("")
        lines.append("หมายเหตุ: เป็นประวัติ check-in และ alert เท่านั้น ไม่ใช่การวินิจฉัย")
        return "\n".join(lines)

    def _screening_history_answer_lines(self, state, group):
        lines = []
        for item in state.get("observations", []) or []:
            if item.get("type") == "red_bundle":
                answer = "ใช่" if item.get("answer") == "yes" else "ไม่ใช่"
                lines.append("- เช็กอาการแดงรวม: {0}".format(answer))
                break
        yellow_answers = state.get("yellow_answers") or {}
        for rule_id, answer in yellow_answers.items():
            rule = self._find_rule_or_none(group, rule_id) if group else None
            label = self._question_to_statement((rule or {}).get("user_friendly_check", "")) or rule_id
            user_answer = self._clean_history_answer(answer.get("answer", "")) or "-"
            matched = "พบจากคำตอบ" if answer.get("matched") else "ไม่พบจากคำตอบ"
            lines.append("- {0}: {1} ({2})".format(label, user_answer, matched))
        return lines

    def _screening_history_detail_lines(self, state):
        lines = []
        for detail in (state.get("yellow_details") or {}).values():
            label = detail.get("label") or detail.get("key") or "รายละเอียด"
            answer = detail.get("answer", "")
            if answer == "":
                continue
            lines.append("- {0}: {1}".format(label, answer))
        return lines

    def _clean_history_answer(self, answer):
        text = re.sub(r"\s+", " ", str(answer or "")).strip()
        text = re.sub(r"\s+(?:yes|no)$", "", text, flags=re.IGNORECASE).strip()
        return text

    def _risk_label_th(self, risk):
        labels = {
            "red": "สีแดง",
            "yellow": "สีเหลือง",
            "green": "สีเขียว",
            "insufficient": "ข้อมูลยังไม่พอ",
        }
        return labels.get(risk, risk or "ข้อมูลยังไม่พอ")

    def _save_assistant(self, session, user_id, reply, state):
        self.db.update_session_state(session["session_id"], state)
        self.db.append_chat(session["session_id"], user_id, "assistant", reply, {"channel": "backend"})

    def _state(self, session):
        try:
            state = json.loads(session.get("state_json") or "{}")
        except Exception:
            state = {}
        state.setdefault("asked_rule_ids", [])
        state.setdefault("active_group_ids", self._extract_group_ids(state.get("active_group_id", "")))
        state.setdefault("matched_rules", [])
        state.setdefault("observations", [])
        state.setdefault("skip_questions", [])
        state.setdefault("red_bundle_done", False)
        state.setdefault("red_checked_rule_ids", [])
        state.setdefault("yellow_done", False)
        state.setdefault("yellow_answers", {})
        state.setdefault("yellow_current_rule_ids", [])
        state.setdefault("yellow_detail_questions", [])
        state.setdefault("yellow_details", {})
        state.setdefault("pending_detail_key", "")
        state.setdefault("flow_phase", "")
        return state

    def _find_rule(self, group, rule_id):
        for rule in group.get("rules", []):
            if rule["rule_id"] == rule_id:
                return rule
        raise KeyError("Unknown rule_id: " + rule_id)

    def _answer_matches_rule(self, answer, rule):
        question = rule.get("user_friendly_check", "")
        condition = rule.get("condition_from_pdf", "")
        inverted_terms = [
            "ตอบสนองและหายใจอยู่ไหม",
            "ตอบคำถามง่าย ๆ ได้ปกติไหม",
            "ยังพูดและเดินได้ไหม",
            "ยังตอบสนองได้",
        ]
        is_inverted = any(term in question for term in inverted_terms)
        if is_inverted:
            return answer == "no"
        if "ไม่รู้สึกตัวหรือไม่หายใจ" in condition and "ตอบสนอง" in question:
            return answer == "no"
        return answer == "yes"

    def _answer_value(self, text, llm_first=None):
        if llm_first:
            normalized = (llm_first.get("normalized_answer") or "").strip().lower()
            if normalized in ("yes", "no"):
                return normalized
        t = text.strip().lower()
        if self._is_yes(t):
            return "yes"
        if self._is_no(t):
            return "no"
        return "unknown"

    def _is_yes(self, text):
        t = text.strip().lower()
        return t in ("ใช่", "มี", "yes", "y", "ถูก", "ครับ", "ค่ะ") or t.startswith("ใช่")

    def _is_no(self, text):
        t = text.strip().lower()
        return t in ("ไม่", "ไม่มี", "ไม่ใช่", "no", "n", "ยัง", "เปล่า") or t.startswith("ไม่")

    def _is_checkin_start(self, text):
        t = text.strip().lower()
        return t in ("เช็กอิน", "เช็คอิน", "checkin", "check-in", "start", "เริ่ม")

    def _is_general_health_question(self, text):
        t = text.lower()
        if not ("?" in t or "ไหม" in t or "มั้ย" in t or "หรือ" in t or "ควร" in t):
            return False
        blocked = [
            "กินยา",
            "ยาอะไร",
            "รักษา",
            "ทำยังไงให้หาย",
            "เป็นโรค",
            "โรคอะไร",
            "วินิจฉัย",
            "สาเหตุ",
            "อาหารเสริม",
            "ควรกิน",
            "ควรทำอะไร",
        ]
        return any(term in t for term in blocked)

    def _event(self, kind, message, data):
        return {"at": utc_now(), "kind": kind, "message": message, "data": data or {}}

    def _knowledge_snapshot(self, state, console):
        group_id = state.get("active_group_id", "")
        group = self._active_group(state) if group_id else None
        selected_groups = []
        for selected_id in state.get("active_group_ids", []) or self._extract_group_ids(group_id):
            selected = self.corpus.get_group(selected_id)
            if selected:
                selected_groups.append(
                    {
                        "group_id": selected.get("group_id", ""),
                        "group_name_th": selected.get("group_name_th", ""),
                        "source_path": selected.get("path", ""),
                    }
                )
        retrieve_events = [event for event in console if event.get("kind") in ("ems.retrieve", "ems.retrieve.assisted")]
        candidate_groups = []
        for event in retrieve_events:
            data = event.get("data") or {}
            candidates = data.get("candidates", []) or data.get("merged_candidates", []) or []
            for candidate in candidates:
                candidate_groups.append(candidate)

        retrieval_assist = []
        for event in console:
            if event.get("kind") in ("llm.retrieval_assist", "llm.retrieval_assist.low_confidence", "ems.retrieve.assisted"):
                retrieval_assist.append(
                    {
                        "kind": event.get("kind", ""),
                        "message": event.get("message", ""),
                        "data": event.get("data") or {},
                    }
                )

        active_rule_ids = []
        for key in ("red_bundle_rule_ids", "yellow_current_rule_ids", "yellow_rule_ids", "asked_rule_ids", "skip_questions"):
            for rule_id in state.get(key, []) or []:
                if rule_id and rule_id not in active_rule_ids:
                    active_rule_ids.append(rule_id)
        for item in state.get("matched_rules", []) or []:
            rule_id = item.get("rule_id", "")
            if rule_id and rule_id not in active_rule_ids and not rule_id.endswith("_BUNDLE"):
                active_rule_ids.append(rule_id)

        rules = []
        if group:
            for rule in group.get("rules", []):
                if rule["rule_id"] in active_rule_ids:
                    rules.append(
                        {
                            "rule_id": rule.get("rule_id", ""),
                            "level": rule.get("level", ""),
                            "condition_from_pdf": rule.get("condition_from_pdf", ""),
                            "user_friendly_check": rule.get("user_friendly_check", ""),
                            "answer_type": rule.get("answer_type", ""),
                            "source_ref": rule.get("source_ref", ""),
                        }
                    )

        detail_questions = [
            {
                "key": item.get("key", ""),
                "type": item.get("type", ""),
                "question": item.get("question", ""),
                "choices": item.get("choices", []),
                "source_rule_ids": item.get("source_rule_ids", []),
            }
            for item in state.get("yellow_detail_questions", []) or []
        ]

        if not group:
            return {
                "selected_group": None,
                "selected_groups": selected_groups,
                "candidate_groups": candidate_groups,
                "retrieval_assist": retrieval_assist,
                "active_rules": [],
                "question_bank": [],
                "detail_questions": detail_questions,
                "markdown_excerpt": "",
            }

        return {
            "selected_group": {
                "group_id": group.get("group_id", ""),
                "group_name_th": group.get("group_name_th", ""),
                "source_path": group.get("path", ""),
            },
            "selected_groups": selected_groups,
            "candidate_groups": candidate_groups,
            "retrieval_assist": retrieval_assist,
            "active_rules": rules,
            "question_bank": group.get("questions", [])[:8],
            "detail_questions": detail_questions,
            "markdown_excerpt": group.get("markdown_excerpt", "")[:2500],
        }

    def _result(self, replies, alerts, state, console, usage_delta, session_id, ui_messages=None):
        stats = self.db.llm_stats(session_id)
        knowledge = self._knowledge_snapshot(state, console)
        return {
            "reply_messages": replies,
            "alert_messages": alerts,
            "ui_messages": ui_messages or [],
            "state": state,
            "knowledge_retrieved": knowledge,
            "debug": {
                "events": console,
                "api_calls_delta": usage_delta["api_calls"],
                "token_delta": usage_delta,
                "session_llm_totals": stats,
            },
        }
