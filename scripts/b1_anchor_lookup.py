"""B1 anchor itemid resolution. Queries d_items ONLY. No patient rows."""
from google.cloud import bigquery

CONCEPTS = {
    "dobutamine": "dobutamine", "milrinone": "milrinone",
    "IABP": "balloon pump", "Impella": "impella", "ECMO": "ecmo",
    "norepinephrine": "norepinephrine", "epinephrine": "epinephrine",
    "vasopressin": "vasopressin", "dopamine": "dopamine",
    "phenylephrine": "phenylephrine",
}

c = bigquery.Client()
for concept, pattern in CONCEPTS.items():
    q = f"""
    SELECT itemid, label, abbreviation, linksto, category
    FROM `physionet-data.mimiciv_3_1_icu.d_items`
    WHERE linksto IN ('inputevents','procedureevents')
      AND LOWER(label) LIKE '%{pattern}%'
    ORDER BY linksto, label
    """
    rows = list(c.query(q).result())
    print(f"\n=== {concept} ===")
    if not rows:
        print("UNRESOLVED")
    for r in rows:
        print(f"{r.itemid}\t{r.label}\t{r.linksto}\t{r.category}")
