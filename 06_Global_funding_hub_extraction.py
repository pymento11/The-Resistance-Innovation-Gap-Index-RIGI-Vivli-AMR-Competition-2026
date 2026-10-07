import csv
import os
import re
from collections import defaultdict

# Method: rule-based classification of AMR funding-project abstracts.
# Reads a CSV export of the Funding Hub and assigns one organism and one antibiotic label
# per abstract using weighted term matching.
# Produces project-level results, target-category proportions,
# and funding summaries grouped by project start year.


# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
# Set the input/output filenames below. Use the same absolute DATA_DIR path in both configuration sections.
DATA_DIR = "/Users/Documents/global AMR"

INPUT_CSV = "Global AMR R&D Hub Projects.xlsx - data.csv"   # exact CSV filename
OUTPUT_CSV = "method1_results_GLOBALAMR_1.csv"                 # written into DATA_DIR


# =============================================================================
# STEP 0 — GAZETTEERS (organism & antibiotic term lists)
# =============================================================================
ORGANISMS = {
    "Escherichia coli":            [r"escherichia coli", r"e\.?\s?coli"],
    "Klebsiella pneumoniae":       [r"klebsiella pneumoniae", r"k\.?\s?pneumoniae"],
    "Klebsiella":                  [r"klebsiella"],
    "Pseudomonas aeruginosa":      [r"pseudomonas aeruginosa", r"p\.?\s?aeruginosa"],
    "Pseudomonas":                 [r"pseudomonas"],
    "Staphylococcus aureus":       [r"staphylococcus aureus", r"s\.?\s?aureus", r"\bMRSA\b", r"\bMSSA\b"],
    "Staphylococcus":              [r"staphylococc\w+", r"staph\b"],
    "Acinetobacter baumannii":     [r"acinetobacter baumannii", r"a\.?\s?baumannii"],
    "Acinetobacter":               [r"acinetobacter"],
    "Enterococcus faecium":        [r"enterococcus faecium", r"e\.?\s?faecium"],
    "Enterococcus faecalis":       [r"enterococcus faecalis", r"e\.?\s?faecalis"],
    "Enterococcus":                [r"enterococc\w+", r"\bVRE\b"],
    "Streptococcus pneumoniae":    [r"streptococcus pneumoniae", r"s\.?\s?pneumoniae", r"pneumococc\w+"],
    "Streptococcus":               [r"streptococc\w+"],
    "Mycobacterium tuberculosis":  [r"mycobacterium tuberculosis", r"m\.?\s?tuberculosis", r"\bMtb\b",
                                    r"tuberculosis", r"\bTB\b"],
    "Neisseria gonorrhoeae":       [r"neisseria gonorrhoeae", r"n\.?\s?gonorrhoeae", r"gonococc\w+", r"gonorrh\w+"],
    "Neisseria meningitidis":      [r"neisseria meningitidis", r"n\.?\s?meningitidis", r"meningococc\w+"],
    "Salmonella":                  [r"salmonella\w*", r"typhi\w*"],
    "Shigella":                    [r"shigella\w*"],
    "Enterobacter":                [r"enterobacter\b", r"enterobacter cloacae"],
    "Enterobacteriaceae":          [r"enterobacteriaceae", r"enterobacterales", r"enterobacteria\w*"],
    "Clostridioides difficile":    [r"clostridioides difficile", r"clostridium difficile", r"c\.?\s?difficile", r"c\.?\s?diff\b"],
    "Campylobacter":               [r"campylobacter\w*"],
    "Helicobacter pylori":         [r"helicobacter pylori", r"h\.?\s?pylori"],
    "Haemophilus influenzae":      [r"haemophilus influenzae", r"h\.?\s?influenzae"],
    "Stenotrophomonas maltophilia":[r"stenotrophomonas maltophilia", r"s\.?\s?maltophilia", r"stenotrophomonas"],
    "Burkholderia":                [r"burkholderia\w*"],
    "Vibrio cholerae":             [r"vibrio cholerae", r"v\.?\s?cholerae", r"cholera\b"],
    "Proteus":                     [r"proteus\b"],
    "Serratia":                    [r"serratia\w*"],
    "Bacteroides":                 [r"bacteroides\w*"],
    "Candida auris":               [r"candida auris", r"c\.?\s?auris"],
    "Candida albicans":            [r"candida albicans", r"c\.?\s?albicans"],
    "Candida":                     [r"candida\w*"],
    "Aspergillus":                 [r"aspergillus\w*"],
    "Cryptococcus":                [r"cryptococc\w+"],
}

ANTIBIOTICS = {
    "penicillin":       [r"penicillin\w*", r"\bbenzylpenicillin\b"],
    "amoxicillin":      [r"amoxicillin", r"amoxycillin", r"co-amoxiclav", r"amoxicillin[- ]clavulan\w*"],
    "ampicillin":       [r"ampicillin", r"ampicillin[- ]sulbactam"],
    "piperacillin":     [r"piperacillin", r"piperacillin[- ]tazobactam", r"pip[- ]?tazo\w*"],
    "methicillin":      [r"methicillin"],
    "oxacillin":        [r"oxacillin"],
    "ceftriaxone":      [r"ceftriaxone"],
    "cefotaxime":       [r"cefotaxime"],
    "ceftazidime":      [r"ceftazidime", r"ceftazidime[- ]avibactam"],
    "cefepime":         [r"cefepime"],
    "ceftaroline":      [r"ceftaroline"],
    "ceftolozane":      [r"ceftolozane", r"ceftolozane[- ]tazobactam"],
    "cephalosporin":    [r"cephalosporin\w*", r"cefazolin", r"cefuroxime", r"cephalexin", r"ceftazidime",
                         r"cef\w*(?=\b)"],
    "meropenem":        [r"meropenem", r"meropenem[- ]vaborbactam"],
    "imipenem":         [r"imipenem", r"imipenem[- ]cilastatin"],
    "ertapenem":        [r"ertapenem"],
    "carbapenem":       [r"carbapenem\w*", r"\w*penem\b"],
    "aztreonam":        [r"aztreonam"],
    "ciprofloxacin":    [r"ciprofloxacin"],
    "levofloxacin":     [r"levofloxacin"],
    "moxifloxacin":     [r"moxifloxacin"],
    "fluoroquinolone":  [r"fluoroquinolone\w*", r"quinolone\w*", r"\w*floxacin\b"],
    "gentamicin":       [r"gentamicin", r"gentamycin"],
    "amikacin":         [r"amikacin"],
    "tobramycin":       [r"tobramycin"],
    "streptomycin":     [r"streptomycin"],
    "aminoglycoside":   [r"aminoglycosid\w*"],
    "erythromycin":     [r"erythromycin"],
    "azithromycin":     [r"azithromycin"],
    "clarithromycin":   [r"clarithromycin"],
    "macrolide":        [r"macrolid\w*"],
    "vancomycin":       [r"vancomycin"],
    "teicoplanin":      [r"teicoplanin"],
    "glycopeptide":     [r"glycopeptid\w*"],
    "tetracycline":     [r"tetracyclin\w*"],
    "doxycycline":      [r"doxycyclin\w*"],
    "tigecycline":      [r"tigecyclin\w*"],
    "colistin":         [r"colistin", r"polymyxin\s?e"],
    "polymyxin":        [r"polymyxin\w*"],
    "linezolid":        [r"linezolid"],
    "daptomycin":       [r"daptomycin"],
    "trimethoprim":     [r"trimethoprim", r"co-trimoxazole", r"cotrimoxazole", r"trimethoprim[- ]sulfamethoxazole", r"\bTMP[- ]SMX\b"],
    "sulfamethoxazole": [r"sulfamethoxazole", r"sulphamethoxazole"],
    "sulfonamide":      [r"sulfonamid\w*", r"sulphonamid\w*", r"sulfa\b"],
    "metronidazole":    [r"metronidazol\w*"],
    "rifampicin":       [r"rifampicin", r"rifampin", r"rifamycin\w*"],
    "fosfomycin":       [r"fosfomycin"],
    "nitrofurantoin":   [r"nitrofurantoin"],
    "chloramphenicol":  [r"chloramphenicol"],
    "clindamycin":      [r"clindamycin"],
    "isoniazid":        [r"isoniazid"],
    "ethambutol":       [r"ethambutol"],
    "pyrazinamide":     [r"pyrazinamide"],
    "beta-lactam":      [r"beta[- ]?lactam\w*", r"β[- ]?lactam\w*", r"\w*cillin\b"],
}


def _compile(gazetteer):
    """Compile each canonical entry into one combined regex (case-insensitive)."""
    compiled = {}
    for canonical, aliases in gazetteer.items():
        pattern = r"(?<![A-Za-z])(?:" + "|".join(aliases) + r")"
        compiled[canonical] = re.compile(pattern, re.IGNORECASE)
    return compiled


ORG_RE = _compile(ORGANISMS)
ABX_RE = _compile(ANTIBIOTICS)


# =============================================================================
# STEP 1 — DETECT WHETHER AN ABSTRACT IS STRUCTURED
# =============================================================================
SECTION_LABEL_RE = re.compile(
    r"\b(background|introduction|objectives?|aims?|methods?|materials?|"
    r"results?|findings?|conclusions?|discussion|summary)\s*:",
    re.IGNORECASE,
)
DISCARD_SECTIONS = {"background", "introduction", "objective", "objectives", "aim", "aims"}


def is_structured(abstract: str) -> bool:
    return len(SECTION_LABEL_RE.findall(abstract)) >= 2


def keep_only_informative_sections(abstract: str) -> str:
    """
    For a STRUCTURED abstract: Exclude background, introduction, objective, and aim sections; 
    retain other recognized sections (Methods/Results/Conclusion). Return the original abstract if no sections are retained.
    """
    matches = list(SECTION_LABEL_RE.finditer(abstract))
    if not matches:
        return abstract
    kept = []
    for i, m in enumerate(matches):
        label = m.group(1).lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(abstract)
        block = abstract[start:end]
        if label not in DISCARD_SECTIONS:
            kept.append(block)
    return " ".join(kept) if kept else abstract


# =============================================================================
# STEP 2 — SENTENCE SPLITTING + POSITIONAL WEIGHTS (for UNSTRUCTURED abstracts)
# =============================================================================
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def split_sentences(text: str):
    text = text.strip()
    if not text:
        return []
    return [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]


def positional_weights(n_sentences: int):
    """
    Linear ramp: first sentence -> weight 1.0, last sentence -> weight ~3.0.
    Later sentences (Methods/Results/Conclusion) count more than early ones.
    """
    if n_sentences <= 1:
        return [1.0] * n_sentences
    return [1.0 + 2.0 * (i / (n_sentences - 1)) for i in range(n_sentences)]


# =============================================================================
# STEP 3 — SCORE ORGANISMS / ANTIBIOTICS OVER WEIGHTED SENTENCES
# =============================================================================
def score_terms(sentences, weights, compiled_re):
    scores = defaultdict(float)
    for sent, w in zip(sentences, weights):
        for canonical, rx in compiled_re.items():
            hits = len(rx.findall(sent))
            if hits:
                scores[canonical] += hits * w
    return scores


def collapse_genus_species(scores):
    """Return scores unchanged; no genus–species consolidation is applied."""
    return scores


def pick_best(scores):
    if not scores:
        return "", 0.0
    best = max(scores.items(), key=lambda kv: kv[1])
    return best[0], round(best[1], 2)


# =============================================================================
# STEP 4 — DRIVER: run over the whole dataset
# =============================================================================
def process_row(title: str, abstract: str):
    abstract = (abstract or "").strip()
    if not abstract:
        return {"organism": "", "antibiotic": "",
                "organism_score": 0.0, "antibiotic_score": 0.0,
                "mode": "empty-abstract"}

    if is_structured(abstract):
        mode = "structured (dropped background)"
        informative = keep_only_informative_sections(abstract)
        sentences = split_sentences(informative)
        weights = [1.0] * len(sentences)          # Use uniform sentence weights for structured abstracts.
    else:
        mode = "unstructured (position-weighted)"
        sentences = split_sentences(abstract)
        weights = positional_weights(len(sentences))

    org_scores = score_terms(sentences, weights, ORG_RE)
    abx_scores = score_terms(sentences, weights, ABX_RE)

    org, org_s = pick_best(collapse_genus_species(org_scores))
    abx, abx_s = pick_best(abx_scores)
    return {"organism": org, "antibiotic": abx,
            "organism_score": org_s, "antibiotic_score": abx_s,
            "mode": mode}


def main():
    # Resolve the base folder: the script's own folder, or the working
    # directory when __file__ is undefined (e.g. run interactively in RStudio).
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        here = os.getcwd()

    # If DATA_DIR is a full path, use it as-is; otherwise treat it as a
    # subfolder next to the script / working directory.
    data_dir = DATA_DIR if os.path.isabs(DATA_DIR) else os.path.join(here, DATA_DIR)

    in_path = os.path.join(data_dir, INPUT_CSV)
    out_path = os.path.join(data_dir, OUTPUT_CSV)

    if not os.path.exists(in_path):
        raise FileNotFoundError(
            f"Could not find the dataset at:\n  {in_path}\n"
            f"Check that DATA_DIR ({DATA_DIR!r}) and INPUT_CSV ({INPUT_CSV!r}) "
            f"exactly match your folder and file names."
        )

    with open(in_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = []
    for r in rows:
        res = process_row(r.get("Title", ""), r.get("Abstract", ""))
        results.append({
            "Id": r.get("Id", ""),
            "Title": r.get("Title", "")[:120],
            "Predicted_Organism": res["organism"],
            "Organism_Score": res["organism_score"],
            "Predicted_Antibiotic": res["antibiotic"],
            "Antibiotic_Score": res["antibiotic_score"],
            "Mode": res["mode"],
            "Existing_Infectious_Agent": r.get("Infectious Agent", ""),
        })

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    n_org = sum(1 for r in results if r["Predicted_Organism"])
    n_abx = sum(1 for r in results if r["Predicted_Antibiotic"])
    print(f"[Method 1] Wrote {len(results)} rows -> {OUTPUT_CSV}")
    print(f"[Method 1] Organism found in {n_org}/{len(results)} | Antibiotic found in {n_abx}/{len(results)}")


if __name__ == "__main__":
    main()


# =============================================================================
# STEP 5 — SUMMARIZE TARGET CATEGORY PROPORTIONS
# =============================================================================


from collections import Counter

# ---- CONFIG: point these at your Method 1 output ----
DATA_DIR = "/Users/Documents/global AMR"
RESULTS_CSV = OUTPUT_CSV      
SUMMARY_CSV = "method1_target_proportions.csv"     #output

# ---- Target species categories (each predicted name -> its category) ----
TARGET_CATEGORIES = {
    "Escherichia coli":        "Enterobacteriaceae",
    "Klebsiella pneumoniae":   "Enterobacteriaceae",
    "Klebsiella":              "Enterobacteriaceae",
    "Serratia":                "Enterobacteriaceae",
    "Enterobacter":            "Enterobacteriaceae",
    "Enterobacteriaceae":      "Enterobacteriaceae",
    "Proteus":                 "Enterobacteriaceae",
    "Acinetobacter baumannii": "Acinetobacter baumannii",
    "Acinetobacter":           "Acinetobacter baumannii",
    "Pseudomonas aeruginosa":  "Pseudomonas aeruginosa",
    "Pseudomonas":             "Pseudomonas aeruginosa",
}
CATEGORY_ORDER = ["Enterobacteriaceae", "Acinetobacter baumannii", "Pseudomonas aeruginosa"]

# ---- Read the Method 1 results and tally the target categories ----
in_path = os.path.join(DATA_DIR, RESULTS_CSV)
with open(in_path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

n_total = len(rows)
predicted = [r.get("Predicted_Organism", "").strip() for r in rows]
n_detected = sum(1 for p in predicted if p)

counts = Counter()
for p in predicted:
    category = TARGET_CATEGORIES.get(p)
    if category:
        counts[category] += 1

# ---- Print a frequency table and write it to a CSV ----
print(f"Total studies:            {n_total}")
print(f"Studies with an organism: {n_detected}")
print()
print(f"{'Target category':<26}{'Count':>7}{'% of all':>11}{'% of detected':>16}")
print("-" * 60)

summary_rows = []
for category in CATEGORY_ORDER:
    k = counts.get(category, 0)
    pct_all = (k / n_total * 100) if n_total else 0
    pct_det = (k / n_detected * 100) if n_detected else 0
    print(f"{category:<26}{k:>7}{pct_all:>10.1f}%{pct_det:>15.1f}%")
    summary_rows.append([category, k, round(pct_all, 1), round(pct_det, 1)])

total_target = sum(counts.values())
pct_all = (total_target / n_total * 100) if n_total else 0
pct_det = (total_target / n_detected * 100) if n_detected else 0
print("-" * 60)
print(f"{'Any target species':<26}{total_target:>7}{pct_all:>10.1f}%{pct_det:>15.1f}%")
summary_rows.append(["Any target species", total_target, round(pct_all, 1), round(pct_det, 1)])

out_path = os.path.join(DATA_DIR, SUMMARY_CSV)
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Target_Category", "Count", "Percent_of_all_studies", "Percent_of_detected"])
    w.writerows(summary_rows)

print()
print(f"Saved summary -> {SUMMARY_CSV}")

# =============================================================================
# STEP 6 — SUMMARIZE TARGET CATEGORIES BY START YEAR
# =============================================================================

YEAR_COLUMN = "Start Year"                     # column in the ORIGINAL dataset to group by
BY_YEAR_CSV = "method1_target_by_year.csv"     # this section's output

# Build Id -> year from the original input dataset
year_by_id = {}
with open(os.path.join(DATA_DIR, INPUT_CSV), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        year_by_id[row.get("Id", "")] = (row.get(YEAR_COLUMN, "") or "").strip()

# Read the Method 1 results and tally per year
per_year = {}   # year -> {"total": int, "detected": int, "categories": Counter}
with open(os.path.join(DATA_DIR, OUTPUT_CSV), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        year = year_by_id.get(row.get("Id", ""), "") or "(no year)"
        organism = row.get("Predicted_Organism", "").strip()
        bucket = per_year.setdefault(year, {"total": 0, "detected": 0, "categories": Counter()})
        bucket["total"] += 1
        if organism:
            bucket["detected"] += 1
        category = TARGET_CATEGORIES.get(organism)
        if category:
            bucket["categories"][category] += 1

# Sort years numerically, pushing any "(no year)" to the end
def year_sort_key(y):
    return (0, int(y)) if y.isdigit() else (1, 0)

# For each year, show each target's count (n) and % of that year's detected studies
SHORT = {"Enterobacteriaceae": "Entero", "Acinetobacter baumannii": "Acineto",
         "Pseudomonas aeruginosa": "Pseudo"}

print()
print("Target organisms by year (n and % of that year's detected studies)")
header = f"{'Year':<8}{'Studies':>8}{'Detected':>9}"
for cat in CATEGORY_ORDER:
    header += f"{SHORT[cat] + ' n':>11}{SHORT[cat] + ' %':>10}"
print(header)
print("-" * len(header))

csv_header = ["Year", "Studies", "Detected"]
for cat in CATEGORY_ORDER:
    csv_header += [f"{cat} (n)", f"{cat} (% of detected)"]
rows_out = [csv_header]

for year in sorted(per_year, key=year_sort_key):
    b = per_year[year]
    det = b["detected"]
    line = f"{year:<8}{b['total']:>8}{det:>9}"
    csv_row = [year, b["total"], det]
    for cat in CATEGORY_ORDER:
        n = b["categories"].get(cat, 0)
        pct = (n / det * 100) if det else 0
        line += f"{n:>11}{pct:>9.1f}%"
        csv_row += [n, round(pct, 1)]
    print(line)
    rows_out.append(csv_row)

with open(os.path.join(DATA_DIR, BY_YEAR_CSV), "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows_out)

print()
print(f"Saved by-year table -> {BY_YEAR_CSV}")

# =============================================================================
# STEP 7 — SUMMARIZE FUNDING AND PROJECT COUNTS BY START YEAR
# =============================================================================

YEAR_COLUMN = "Start Year"
AMOUNT_COLUMN = "Amount USD"
BY_YEAR_FUNDING_CSV = "method1_target_by_year_funding.csv"

def parse_amount(value):
    value = (value or "").replace(",", "").replace("$", "").strip()
    try:
        return float(value)
    except ValueError:
        return 0.0

# Id -> (year, funding amount) from the original dataset
meta_by_id = {}
with open(os.path.join(DATA_DIR, INPUT_CSV), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        year = (row.get(YEAR_COLUMN, "") or "").strip() or "(no year)"
        meta_by_id[row.get("Id", "")] = (year, parse_amount(row.get(AMOUNT_COLUMN, "")))

# Tally per year (all projects) and per (year, category)
year_projects = defaultdict(int)
year_funding = defaultdict(float)
cat_projects = defaultdict(int)       # (year, category) -> count
cat_funding = defaultdict(float)      # (year, category) -> funding
with open(os.path.join(DATA_DIR, OUTPUT_CSV), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        year, amount = meta_by_id.get(row.get("Id", ""), ("(no year)", 0.0))
        year_projects[year] += 1
        year_funding[year] += amount
        category = TARGET_CATEGORIES.get(row.get("Predicted_Organism", "").strip())
        if category:
            cat_projects[(year, category)] += 1
            cat_funding[(year, category)] += amount

def year_sort_key(y):
    return (0, int(y)) if y.isdigit() else (1, 0)

# Write one row per Year x Category (7 columns, funding first)
header = ["Year", "Category", "category_funding_USD", "total_funding_USD_that_year",
          "share_pct", "n_projects_category", "n_total_projects_that_year"]
rows_out = [header]
for year in sorted(year_projects, key=year_sort_key):
    n_total = year_projects[year]
    total_fund = year_funding[year]
    for category in CATEGORY_ORDER:
        n_cat = cat_projects.get((year, category), 0)
        cat_fund = cat_funding.get((year, category), 0.0)
        share_pct = (cat_fund / total_fund * 100) if total_fund else 0
        rows_out.append([year, category, round(cat_fund, 2), round(total_fund, 2),
                         round(share_pct, 1), n_cat, n_total])

with open(os.path.join(DATA_DIR, BY_YEAR_FUNDING_CSV), "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows_out)

print(f"Wrote {len(rows_out) - 1} rows (Year x Category) -> {BY_YEAR_FUNDING_CSV}")
