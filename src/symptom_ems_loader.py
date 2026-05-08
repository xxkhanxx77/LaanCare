import re
from pathlib import Path


RISK_RE = re.compile(r"^\|\s*(EMS\d{2})_(RED|YELLOW|GREEN)_(\d{2})\s*\|")
QUESTION_RE = re.compile(r"^\|\s*(EMS\d{2}_Q\d{2})\s*\|")


def _split_row(line):
    return [c.strip().replace("\\|", "|") for c in line.strip().strip("|").split("|")]


def _frontmatter_value(text, key):
    match = re.search(r"^" + re.escape(key) + r":\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return value


class EmsCorpus:
    def __init__(self, symptom_dir):
        self.symptom_dir = Path(symptom_dir)
        self.groups = {}
        self.index_rows = []
        self.load()

    def load(self):
        self.groups = {}
        for path in sorted(self.symptom_dir.glob("symptom_group_*.md")):
            group = self._load_group(path)
            self.groups[group["group_id"]] = group
        self.index_rows = self._load_index(self.symptom_dir / "symptom_index.md")

    def _load_index(self, path):
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| EMS"):
                continue
            cells = _split_row(line)
            if len(cells) >= 5:
                rows.append(
                    {
                        "group_id": cells[0],
                        "group_name_th": cells[1],
                        "aliases_th": cells[2],
                        "keywords_th": cells[3],
                        "source_ref": cells[4],
                    }
                )
        return rows

    def _load_group(self, path):
        text = path.read_text(encoding="utf-8")
        group_id = _frontmatter_value(text, "group_id")
        name = _frontmatter_value(text, "group_name_th")
        rules = []
        questions = []
        for line in text.splitlines():
            if RISK_RE.match(line):
                cells = _split_row(line)
                if len(cells) >= 5:
                    rule_id = cells[0]
                    level = rule_id.split("_")[1].lower()
                    rule = {
                        "rule_id": rule_id,
                        "level": level,
                        "condition_from_pdf": cells[1],
                        "user_friendly_check": cells[2],
                        "answer_type": cells[3],
                        "source_ref": cells[4],
                        "stop_if_true": cells[5].lower() == "true" if len(cells) > 5 else False,
                    }
                    rules.append(rule)
            elif QUESTION_RE.match(line):
                cells = _split_row(line)
                if len(cells) >= 8:
                    questions.append(
                        {
                            "question_id": cells[0],
                            "question_th": cells[1],
                            "answer_type": cells[2],
                            "choices": cells[3],
                            "ask_when": cells[4],
                            "skip_when": cells[5],
                            "maps_to_rule_id": cells[6],
                            "priority": int(cells[7]) if cells[7].isdigit() else 99,
                        }
                    )
        keywords = self._extract_keywords(text)
        return {
            "path": str(path),
            "group_id": group_id,
            "group_name_th": name,
            "rules": rules,
            "questions": sorted(questions, key=lambda q: q["priority"]),
            "keywords": keywords,
            "markdown_excerpt": text[:6000],
        }

    def _extract_keywords(self, text):
        keywords = []
        for label in ["คำหลัก:", "คำใกล้เคียง:", "คำที่ผู้ใช้ทั่วไปอาจพิมพ์:"]:
            match = re.search(re.escape(label) + r"\s*(.+)", text)
            if match:
                for raw in match.group(1).split(","):
                    value = raw.strip()
                    if value and value != "ไม่พบใน PDF" and value not in keywords:
                        keywords.append(value)
        return keywords

    def get_group(self, group_id):
        return self.groups.get(group_id)

    def symptom_index_for_prompt(self):
        lines = []
        for row in self.index_rows:
            lines.append(
                "{group_id}: {group_name_th}; aliases={aliases_th}; keywords={keywords_th}; source={source_ref}".format(
                    **row
                )
            )
        return "\n".join(lines)

    def deterministic_group_match(self, text):
        normalized = _normalize_search_text(text)
        best = []
        for group in self.groups.values():
            if group["group_id"] == "EMS11":
                continue
            score = 0
            reasons = []
            name = _normalize_search_text(group["group_name_th"])
            for part in re.split(r"[/()\s]+", name):
                if len(part) >= 3 and part in normalized:
                    score += 1
                    reasons.append(part)
            for kw in group["keywords"]:
                kw_l = _normalize_search_text(kw)
                if kw_l and kw_l in normalized:
                    score += 4 if len(kw_l) > 3 else 1
                    reasons.append(kw)
            for token, group_id in FALLBACK_HINTS.items():
                token_l = _normalize_search_text(token)
                if token_l in normalized and group["group_id"] == group_id:
                    score += 3
                    reasons.append(token)
            if score > 0:
                best.append(
                    {
                        "group_id": group["group_id"],
                        "group_name_th": group["group_name_th"],
                        "score": score,
                        "reasons": reasons[:6],
                    }
                )
        best.sort(key=lambda x: x["score"], reverse=True)
        return best[:5]


def _normalize_search_text(text):
    normalized = str(text or "").lower()
    normalized = re.sub(r"\s+", "", normalized)
    replacements = [
        ("หายใจเหนื่อย", "หายใจขัด"),
        ("เหนื่อยหอบ", "หายใจขัด"),
        ("หายใจไม่ทัน", "หายใจขัด"),
        ("หายใจไม่ออก", "หายใจขัด"),
        ("หายใจไม่สะดวก", "หายใจขัด"),
        ("หายใจติด", "หายใจขัด"),
        ("หอบ", "หายใจขัด"),
        ("หายใจยาก", "หายใจลำบาก"),
    ]
    for source, target in replacements:
        normalized = normalized.replace(source, target)
    return normalized


FALLBACK_HINTS = {
    "กัด": "EMS03",
    "ต่อย": "EMS03",
    "แพ้": "EMS02",
    "ลมพิษ": "EMS02",
    "หายใจ": "EMS05",
    "เหนื่อย": "EMS05",
    "เหนื่อยง่าย": "EMS05",
    "เหนื่อยหอบ": "EMS05",
    "หอบ": "EMS05",
    "หายใจเหนื่อย": "EMS05",
    "หายใจไม่ทัน": "EMS05",
    "หายใจไม่ออก": "EMS05",
    "หายใจไม่สะดวก": "EMS05",
    "หายใจติด": "EMS05",
    "เจ็บอก": "EMS07",
    "เจ็บหน้าอก": "EMS07",
    "สำลัก": "EMS08",
    "น้ำตาล": "EMS09",
    "อินซูลิน": "EMS09",
    "ชัก": "EMS16",
    "อ่อนแรง": "EMS18",
    "ปากเบี้ยว": "EMS18",
    "พูดไม่ชัด": "EMS18",
    "หมดสติ": "EMS19",
    "เป็นลม": "EMS19",
    "ตั้งครรภ์": "EMS15",
    "คลอด": "EMS15",
    "จมน้ำ": "EMS23",
    "รถชน": "EMS25",
    "มอไซ": "EMS25",
    "หกล้ม": "EMS24",
    "ตก": "EMS24",
    "ไหม้": "EMS22",
    "ลวก": "EMS22",
    "กินยา": "EMS14",
    "เมา": "EMS14",
    "ทำร้าย": "EMS21",
    "ถูกแทง": "EMS21",
    "ถูกยิง": "EMS21",
}
