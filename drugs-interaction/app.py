from __future__ import annotations

import csv
import math
import re
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MEDICATIONS_CSV = BASE_DIR / "medications_database.csv"
INTERACTIONS_CSV = BASE_DIR / "high_risk_medication_group_interactions.csv"

TOKEN_RE = re.compile(r"[a-z0-9]+")
K1 = 1.5
B = 0.75
TOP_K_RETRIEVE = 15


@dataclass
class MedicationRecord:
    generic_name: str
    medication_group: str
    normalized_name: str
    tokens: List[str]


@dataclass
class InteractionRecord:
    group_1: str
    group_2: str
    interaction_severity: str
    possible_symptoms: str
    interaction_risk: str
    norm_1: str
    norm_2: str


def normalize_text(text: str) -> str:
    return " ".join(TOKEN_RE.findall(text.lower()))


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def parse_drug_input(text: str) -> List[str]:
    raw_parts = re.split(r"[,\n;]+", text)
    cleaned = [part.strip() for part in raw_parts if part.strip()]

    deduped: List[str] = []
    seen = set()
    for item in cleaned:
        marker = item.lower()
        if marker not in seen:
            seen.add(marker)
            deduped.append(item)
    return deduped


class MedicationSearchEngine:
    def __init__(self, medications: List[MedicationRecord]) -> None:
        self.medications = medications
        self._doc_freq: Dict[str, int] = {}
        self._doc_lens: List[int] = []
        self._avg_doc_len = 0.0
        self._build_index()

    def _build_index(self) -> None:
        doc_freq: Dict[str, int] = {}
        doc_lens: List[int] = []

        for med in self.medications:
            tokens = med.tokens
            doc_lens.append(len(tokens))
            for token in set(tokens):
                doc_freq[token] = doc_freq.get(token, 0) + 1

        self._doc_freq = doc_freq
        self._doc_lens = doc_lens
        self._avg_doc_len = sum(doc_lens) / len(doc_lens) if doc_lens else 0.0

    def _idf(self, token: str) -> float:
        n_docs = len(self.medications)
        df = self._doc_freq.get(token, 0)
        return math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)

    def bm25_score(self, query_tokens: List[str], med: MedicationRecord, doc_len: int) -> float:
        if not query_tokens:
            return 0.0

        frequencies = Counter(med.tokens)
        score = 0.0
        for token in query_tokens:
            tf = frequencies.get(token, 0)
            if tf == 0:
                continue
            idf = self._idf(token)
            denom = tf + K1 * (1.0 - B + B * (doc_len / (self._avg_doc_len or 1.0)))
            score += idf * ((tf * (K1 + 1.0)) / denom)
        return score

    def match(self, query: str, threshold: float) -> Dict[str, object]:
        normalized_query = normalize_text(query)
        query_tokens = tokenize(normalized_query)

        if not normalized_query:
            return {
                "input": query,
                "matched": False,
                "selected": None,
                "candidates": [],
                "reason": "Empty drug name",
            }

        scored = []
        similarity_scored = []
        for idx, med in enumerate(self.medications):
            bm25 = self.bm25_score(query_tokens, med, self._doc_lens[idx])
            similarity = SequenceMatcher(None, normalized_query, med.normalized_name).ratio() * 100.0
            scored.append((idx, med, bm25))
            similarity_scored.append((idx, med, similarity))

        scored.sort(key=lambda item: item[2], reverse=True)
        similarity_scored.sort(key=lambda item: item[2], reverse=True)

        candidate_pool = {}
        for idx, med, bm25 in scored[:TOP_K_RETRIEVE]:
            candidate_pool[idx] = (med, bm25)
        for idx, med, _ in similarity_scored[:TOP_K_RETRIEVE]:
            if idx not in candidate_pool:
                candidate_pool[idx] = (med, self.bm25_score(query_tokens, med, self._doc_lens[idx]))

        top_bm25 = scored[0][2] if scored else 0.0
        candidates = []
        for idx, (med, bm25) in candidate_pool.items():
            similarity = SequenceMatcher(None, normalized_query, med.normalized_name).ratio() * 100.0
            bm25_percent = 0.0 if top_bm25 == 0 else (bm25 / top_bm25) * 100.0

            # Hybrid ranking: lexical retrieval (BM25) + fuzzy rerank to recover misspellings.
            weighted_confidence = 0.35 * bm25_percent + 0.65 * similarity
            confidence = max(similarity, weighted_confidence)

            candidates.append(
                {
                    "generic_name": med.generic_name,
                    "medication_group": med.medication_group,
                    "confidence": round(confidence, 2),
                    "similarity": round(similarity, 2),
                    "bm25_percent": round(bm25_percent, 2),
                }
            )

        candidates.sort(key=lambda c: c["confidence"], reverse=True)
        selected = candidates[0] if candidates else None

        if not selected or selected["confidence"] < threshold:
            return {
                "input": query,
                "matched": False,
                "selected": selected,
                "candidates": candidates[:5],
                "reason": f"Best candidate is below threshold {threshold:.0f}%",
            }

        return {
            "input": query,
            "matched": True,
            "selected": selected,
            "candidates": candidates[:5],
            "reason": None,
        }


def csv_value(row: Dict[str, str], key: str) -> str:
    normalized_key = key.strip().lower()
    for row_key, value in row.items():
        clean_row_key = str(row_key).replace("\ufeff", "").strip().lower()
        if clean_row_key == normalized_key:
            return (value or "").strip()
    return ""


def load_medications() -> List[MedicationRecord]:
    meds: List[MedicationRecord] = []
    with MEDICATIONS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            generic_name = csv_value(row, "generic_name")
            medication_group = csv_value(row, "medication_group")
            if not generic_name or not medication_group:
                continue
            norm_name = normalize_text(generic_name)
            meds.append(
                MedicationRecord(
                    generic_name=generic_name,
                    medication_group=medication_group,
                    normalized_name=norm_name,
                    tokens=tokenize(norm_name),
                )
            )
    return meds


def load_interactions() -> List[InteractionRecord]:
    interactions: List[InteractionRecord] = []
    with INTERACTIONS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            g1 = csv_value(row, "group_1")
            g2 = csv_value(row, "group_2")
            sev = csv_value(row, "interaction_severity")
            sym = csv_value(row, "possible_symptoms")
            risk = csv_value(row, "interaction_risk")
            if not g1 or not g2:
                continue
            interactions.append(
                InteractionRecord(
                    group_1=g1,
                    group_2=g2,
                    interaction_severity=sev,
                    possible_symptoms=sym,
                    interaction_risk=risk,
                    norm_1=normalize_text(g1),
                    norm_2=normalize_text(g2),
                )
            )
    return interactions


def find_interactions(matches: List[Dict[str, object]], interactions: List[InteractionRecord]) -> List[Dict[str, str]]:
    accepted = [m for m in matches if m.get("matched") and m.get("selected")]

    mapped_drugs = set()
    mapped_groups = set()
    drug_to_group: Dict[str, str] = {}
    for item in accepted:
        selected = item["selected"]
        drug_key = normalize_text(str(selected["generic_name"]))
        group_key = normalize_text(str(selected["medication_group"]))
        mapped_drugs.add(drug_key)
        mapped_groups.add(group_key)
        drug_to_group[drug_key] = group_key

    findings: List[Dict[str, str]] = []
    seen_keys = set()

    for row in interactions:
        a = row.norm_1
        b = row.norm_2

        matched_by = None
        if a in mapped_drugs and b in mapped_drugs:
            matched_by = "drug-drug"
        elif a in mapped_groups and b in mapped_groups:
            matched_by = "group-group"
        elif (a in mapped_drugs and b in mapped_groups) or (a in mapped_groups and b in mapped_drugs):
            matched_by = "drug-group"

        if not matched_by:
            continue

        key = "|".join(sorted([a, b])) + f"|{row.interaction_risk.lower()}"
        if key in seen_keys:
            continue
        seen_keys.add(key)

        findings.append(
            {
                "norm_1": a,
                "norm_2": b,
                "group_1": row.group_1,
                "group_2": row.group_2,
                "interaction_severity": row.interaction_severity,
                "possible_symptoms": row.possible_symptoms,
                "interaction_risk": row.interaction_risk,
                "matched_by": matched_by,
            }
        )

    covered_group_pairs = set()
    for finding in findings:
        if finding["matched_by"] != "drug-drug":
            continue

        group_a = drug_to_group.get(finding["norm_1"])
        group_b = drug_to_group.get(finding["norm_2"])
        if not group_a or not group_b:
            continue

        covered_group_pairs.add("|".join(sorted([group_a, group_b])))

    filtered_findings: List[Dict[str, str]] = []
    for finding in findings:
        if finding["matched_by"] == "group-group":
            group_pair_key = "|".join(sorted([finding["norm_1"], finding["norm_2"]]))
            if group_pair_key in covered_group_pairs:
                continue

        filtered_findings.append(
            {
                "group_1": finding["group_1"],
                "group_2": finding["group_2"],
                "interaction_severity": finding["interaction_severity"],
                "possible_symptoms": finding["possible_symptoms"],
                "interaction_risk": finding["interaction_risk"],
                "matched_by": finding["matched_by"],
            }
        )

    return filtered_findings


app = Flask(__name__)
MEDICATIONS = load_medications()
INTERACTIONS = load_interactions()
SEARCH_ENGINE = MedicationSearchEngine(MEDICATIONS)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze() -> object:
    payload = request.get_json(silent=True) or {}
    drug_text = str(payload.get("drugs", ""))

    threshold_raw = payload.get("threshold", 80)
    try:
        threshold = float(threshold_raw)
    except (TypeError, ValueError):
        threshold = 80.0

    threshold = max(0.0, min(100.0, threshold))
    input_drugs = parse_drug_input(drug_text)

    if not input_drugs:
        return jsonify({"error": "Please provide at least one medication name."}), 400

    matches = [SEARCH_ENGINE.match(drug, threshold) for drug in input_drugs]
    interactions = find_interactions(matches, INTERACTIONS)

    return jsonify(
        {
            "threshold": threshold,
            "input_count": len(input_drugs),
            "matched_count": len([m for m in matches if m.get("matched")]),
            "matches": matches,
            "interactions": interactions,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
