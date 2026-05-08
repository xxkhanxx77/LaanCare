# Drug Interaction Web UI

This project is a local Flask web application for checking medication interactions from free-text drug input.

It is designed to do four things:

1. Accept multiple medication names in one request.
2. Map each input to the closest generic drug in the medication database.
3. Accept a match only if the score is above a configurable threshold, default `80%`.
4. Check for high-risk interactions using the interaction dataset.

The application is intended for data workflows and prototyping. It is not a clinical decision support system.

## Project Files

- `app.py`: Flask backend, CSV loading, search logic, and interaction detection.
- `templates/index.html`: main web UI.
- `static/styles.css`: page styling.
- `medications_database.csv`: generic medication list with medication groups.
- `high_risk_medication_group_interactions.csv`: interaction reference table.
- `requirements.txt`: Python dependencies.

## Data Structure

### Medication Database

`medications_database.csv` contains:

- `generic_name`
- `medication_group`

Example:

```csv
generic_name,medication_group
warfarin,Anticoagulants
ibuprofen,NSAIDs
lisinopril,ACE inhibitors
```

### Interaction Database

`high_risk_medication_group_interactions.csv` contains:

- `group_1`
- `group_2`
- `interaction_severity`
- `possible_symptoms`
- `interaction_risk`

Important: despite the column names `group_1` and `group_2`, the file currently contains a mix of:

- medication-group pairs such as `Anticoagulants` + `NSAIDs`
- drug-drug pairs such as `warfarin` + `ibuprofen`
- drug-group pairs when needed

The backend supports all three cases.

## How The Logic Works

### 1. Input Parsing

The API accepts a free-text list of drugs from the UI or direct API call.

Input can be separated by:

- commas
- semicolons
- new lines

The parser then:

- trims whitespace
- removes empty values
- deduplicates repeated inputs case-insensitively

Example input:

```text
warfarin, ibuprofenn
lisinopril; spironolactone
```

becomes four distinct query terms.

### 2. Text Normalization

Before matching, the backend normalizes text by:

- lowercasing
- removing non-alphanumeric characters
- tokenizing into words

This helps match inputs consistently against CSV values.

### 3. Drug Mapping: BM25 + Fuzzy Matching

The search pipeline is hybrid.

#### BM25 Retrieval

The application builds a lightweight BM25-style index over all generic medication names.

BM25 is used to retrieve likely candidates from the medication list based on token overlap and term rarity.

This is useful for:

- exact matches
- partial lexical overlap
- multi-token medication names

#### Fuzzy Similarity Reranking

The app also computes string similarity using `SequenceMatcher` from Python standard library.

This is useful for:

- misspellings
- near matches
- small typographical errors

Example:

- input: `ibuprofenn`
- matched drug: `ibuprofen`

#### Candidate Pool

The app combines:

- the top BM25 candidates
- the top fuzzy-similarity candidates

This avoids the common failure where a misspelled drug has no BM25 token overlap but is still an obvious fuzzy match.

#### Confidence Score

For each candidate, the backend computes:

- `similarity`: fuzzy string similarity percentage
- `bm25_percent`: BM25 score normalized against the best BM25 candidate
- `weighted_confidence = 0.35 * bm25_percent + 0.65 * similarity`
- `confidence = max(similarity, weighted_confidence)`

That final rule is intentional. It allows strong typo matches to pass even when BM25 contributes little or nothing.

### 4. Threshold Filtering

Only the best candidate is selected for each input.

The match is accepted only when:

```text
confidence >= threshold
```

Default threshold:

```text
80
```

If the best candidate is below threshold:

- the input is marked as unmatched
- candidate suggestions are still returned in the API response
- unmatched entries are excluded from interaction detection

### 5. Interaction Detection

After matching, the backend collects the accepted results and builds two lookup sets:

- matched drug names
- matched medication groups

Each interaction row is then checked against those sets.

The app supports three interaction types:

- `drug-drug`: both sides match selected generic drugs
- `group-group`: both sides match selected medication groups
- `drug-group`: one side matches a drug and the other matches a medication group

### 6. Duplicate Interaction Cleanup

The interaction file contains some overlapping entries, for example:

- a class-level interaction such as `Anticoagulants` + `NSAIDs`
- a more specific drug-level interaction such as `warfarin` + `ibuprofen`

The backend now prefers the more specific `drug-drug` interaction when both represent the same selected medication groups.

That means:

- if only a group-level rule exists, it is returned
- if both group-level and drug-level rules exist for the same selected pair, the drug-level rule is kept and the broader duplicate is removed

## API

### Endpoint

`POST /api/analyze`

### Request Body

```json
{
  "drugs": "warfarin, ibuprofen, clarithromycin",
  "threshold": 80
}
```

### Request Fields

- `drugs`: required free-text medication list
- `threshold`: optional numeric value from `0` to `100`

If `threshold` is missing or invalid, the backend defaults to `80`.

### Response Shape

The response contains:

- `threshold`: applied threshold value
- `input_count`: number of unique parsed input terms
- `matched_count`: number of accepted mapped drugs
- `matches`: per-input match result with top candidates
- `interactions`: detected high-risk interaction list

Example response:

```json
{
  "threshold": 80.0,
  "input_count": 2,
  "matched_count": 2,
  "matches": [
    {
      "input": "ibuprofenn",
      "matched": true,
      "selected": {
        "generic_name": "ibuprofen",
        "medication_group": "NSAIDs",
        "confidence": 94.74,
        "similarity": 94.74,
        "bm25_percent": 0.0
      },
      "candidates": []
    }
  ],
  "interactions": []
}
```

### Error Response

If no valid medication names are submitted, the API returns:

```json
{
  "error": "Please provide at least one medication name."
}
```

with HTTP status `400`.

## Running The App

### Requirements

- Python 3.8+
- Flask

### Install Dependencies

On Windows, use the Python interpreter explicitly if `pip` fails in the terminal:

```powershell
python -m pip install -r requirements.txt
```

If your environment requires a specific interpreter, use:

```powershell
C:/Users/win25/anaconda3/python.exe -m pip install -r requirements.txt
```

### Start The Server

```powershell
python app.py
```

If needed:

```powershell
C:/Users/win25/anaconda3/python.exe app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## UI Behavior

The web UI provides:

- a multi-drug text area
- a threshold input field
- a summary panel
- a mapped-medications table
- a detected-interactions table

The UI sends a JSON request to `/api/analyze` and renders:

- accepted matches
- unmatched inputs with reason
- detected interactions
- match source type such as `drug-drug` or `group-group`

## Current Limitations

- The medication database is generic-name only. Brand-name mapping is not implemented.
- The interaction file is manually curated and not exhaustive.
- Severity filtering is not configurable in the UI because the current dataset is focused on high-risk interactions.
- The interaction CSV uses historical column names `group_1` and `group_2` even though some rows are not pure group-group rows.
- This project does not provide dosing logic, contraindication timing, renal adjustment, or patient-specific clinical context.

## Safety Notice

- This project is a technical prototype for search and interaction-checking workflows.
- It should not be used as the sole basis for prescribing or patient-care decisions.
- Always verify results with authoritative clinical references before real-world use.
