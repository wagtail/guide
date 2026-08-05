"""
Aggregate candidates + rules + judge into a single scorecard CSV + console table.

Reads:
    out/candidates/candidates_all.json   (per-segment translations + token usage)
    out/rules/rules_detail.json           (deterministic rule pass/fail per segment)
    out/judge/judge_results.json          (GPT-5.1 scores per labelled candidate)

Writes:
    out/scorecard.csv  (one row per model: avg judge scores, rule pass%, cost, tokens)

Usage:
    docker compose exec -T web python manage.py shell -c \
        "exec(open('scripts/eval/summarize.py').read())"
"""

import csv
import json
import os
from collections import defaultdict

LANG_SLUG = os.environ.get("EVAL_LANG_SLUG", "arabic")

CAND_PATH = f"/app/scripts/eval/out/{LANG_SLUG}/candidates/candidates_all.json"
RULES_PATH = f"/app/scripts/eval/out/{LANG_SLUG}/rules/rules_detail.json"
JUDGE_PATH = f"/app/scripts/eval/out/{LANG_SLUG}/judge/judge_results.json"
OUT_CSV = f"/app/scripts/eval/out/{LANG_SLUG}/scorecard.csv"

# Model pricing (input_per_1M, output_per_1M, currency_symbol) — same as page_cost.py
PRICING = {
    "z-ai/glm-5.2": (1.40, 4.40, "$"),
    "deepseek/deepseek-v4-flash": (0.14, 0.28, "$"),
    "google/gemma-4-26b-a4b-it": (0.07, 0.34, "$"),
}


def _cost(model, in_tok, out_tok):
    rates = PRICING.get(model)
    if not rates or rates[0] is None:
        return None, "$"
    ir, orr, cur = rates
    return (in_tok / 1_000_000 * ir) + (out_tok / 1_000_000 * orr), cur


def main():
    with open(CAND_PATH, encoding="utf-8") as f:
        cand = json.load(f)
    with open(RULES_PATH, encoding="utf-8") as f:
        rules = json.load(f)
    with open(JUDGE_PATH, encoding="utf-8") as f:
        judge = json.load(f)

    models = cand["models"]
    rows = cand["rows"]

    # --- Tokens + cost from candidates ---
    tok = defaultdict(lambda: {"in": 0, "out": 0, "calls": 0})
    for r in rows:
        m = r["model"]
        tok[m]["in"] += r["input_tokens"]
        tok[m]["out"] += r["output_tokens"]
        tok[m]["calls"] += 1

    # --- Rule pass% from rules_detail ---
    rule_agg = defaultdict(lambda: defaultdict(lambda: {"pass": 0, "total": 0}))
    for r in rules["results"]:
        m = r["model"]
        for rule, v in r["checks"].items():
            if v is None:
                continue
            rule_agg[m][rule]["total"] += 1
            if v:
                rule_agg[m][rule]["pass"] += 1

    # --- Judge scores: de-shuffle labels back to models ---
    j_scores = defaultdict(lambda: {"accuracy": [], "fluency": [], "rules": []})
    j_ranks = defaultdict(lambda: defaultdict(int))  # model -> {rank: count}
    for r in judge["results"]:
        l2m = r["label_to_model"]
        j = r["judgement"] or {}
        # Compute ranks from scores: lower sum(accuracy+fluency+rules) = worse rank
        score_sums = {}
        for lab, sc in j.items():
            s = sc.get("accuracy", 0) + sc.get("fluency", 0) + sc.get("rules", 0)
            score_sums[lab] = s
        # rank order: higher sum = better (rank 1); ties share the best rank
        ordered = sorted(score_sums.items(), key=lambda kv: -kv[1])
        rank_nums = {}
        last_sum = None
        last_rank = 0
        for idx, (lab, s) in enumerate(ordered, start=1):
            if s != last_sum:
                last_rank = idx
                last_sum = s
            rank_nums[lab] = last_rank
        for lab, m in l2m.items():
            sc = j.get(lab, {})
            for k in ("accuracy", "fluency", "rules"):
                j_scores[m][k].append(sc.get(k))
            j_ranks[m][rank_nums[lab]] += 1

    # --- Build scorecard ---
    fieldnames = [
        "model",
        "judge_acc_avg",
        "judge_fluency_avg",
        "judge_rules_avg",
        "rank1_count",
        "rank2_count",
        "rank3_count",
        "rules_pass_pct",
        "html_tags_pct",
        "bold_keep_pct",
        "no_trunc_pct",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "est_cost",
        "currency",
        "segments",
    ]
    out_rows = []
    for m in models:
        acc = j_scores[m]["accuracy"]
        flu = j_scores[m]["fluency"]
        rl = j_scores[m]["rules"]

        def avg(xs):
            return round(sum(xs) / len(xs), 2) if xs else "N/A"

        def pass_pct(rule):
            a = rule_agg[m][rule]
            return round(100.0 * a["pass"] / a["total"], 1) if a["total"] else "N/A"

        cost, cur = _cost(m, tok[m]["in"], tok[m]["out"])
        out_rows.append(
            {
                "model": m,
                "judge_acc_avg": avg(acc),
                "judge_fluency_avg": avg(flu),
                "judge_rules_avg": avg(rl),
                "rank1_count": j_ranks[m].get(1, 0),
                "rank2_count": j_ranks[m].get(2, 0),
                "rank3_count": j_ranks[m].get(3, 0),
                "rules_pass_pct": pass_pct("no_bleed")
                if False
                else pass_pct("bold_keep"),
                "html_tags_pct": pass_pct("html_tags"),
                "bold_keep_pct": pass_pct("bold_keep"),
                "no_trunc_pct": pass_pct("no_trunc"),
                "input_tokens": tok[m]["in"],
                "output_tokens": tok[m]["out"],
                "total_tokens": tok[m]["in"] + tok[m]["out"],
                "est_cost": round(cost, 6) if cost is not None else "?",
                "currency": cur,
                "segments": tok[m]["calls"],
            }
        )

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    # --- Console table ---
    print("=" * 90)
    print("SCORECARD (15-segment pilot)")
    print("=" * 90)
    print(
        f"{'model':35s} {'acc':>5} {'flu':>5} {'rul':>5} {'r1':>3} {'r2':>3} {'r3':>3} "
        f"{'html%':>6} {'bold%':>6} {'trunc%':>7} {'tokens':>7} {'cost':>9}"
    )
    for r in out_rows:
        print(
            f"{r['model']:35s} {str(r['judge_acc_avg']):>5} {str(r['judge_fluency_avg']):>5} "
            f"{str(r['judge_rules_avg']):>5} {r['rank1_count']:>3} {r['rank2_count']:>3} "
            f"{r['rank3_count']:>3} {str(r['html_tags_pct']):>6} {str(r['bold_keep_pct']):>6} "
            f"{str(r['no_trunc_pct']):>7} {r['total_tokens']:>7} {r['currency']}{r['est_cost']:>8}"
        )
    print(f"\nScorecard CSV: {OUT_CSV}")

    # --- Show notable judge notes ---
    print("\n" + "-" * 70)
    print("Notable judge notes (non-5 scores):")
    for r in judge["results"]:
        j = r["judgement"] or {}
        l2m = r["label_to_model"]
        for lab, sc in j.items():
            if sc.get("accuracy", 5) < 5 or sc.get("rules", 5) < 5:
                print(
                    f"  page{r['page_id']} [{r['context_path'][:30]:30s}] "
                    f"{l2m[lab][:25]:25s} acc={sc['accuracy']} flu={sc['fluency']} "
                    f"rul={sc['rules']}  -- {sc['notes']}"
                )


main()
