#!/usr/bin/env python3
"""
Analyze Experiment Results

After completing blind evaluation, use this script to:
1. Enter your ratings
2. Reveal which config produced which story
3. See aggregate scores and winner

Usage:
    python analyze_results.py experiments/exp_20260118_123456_ANSWER_KEY.json
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(description="Analyze experiment results")
    parser.add_argument("answer_key", type=str, help="Path to ANSWER_KEY.json file")
    parser.add_argument("--ratings", type=str, help="Path to ratings JSON file (optional)")
    args = parser.parse_args()

    # Load answer key
    with open(args.answer_key) as f:
        answer_key = json.load(f)

    mapping = answer_key["mapping"]
    config_descriptions = answer_key["config_descriptions"]

    print("\n" + "="*60)
    print("EXPERIMENT RESULTS ANALYZER")
    print("="*60)
    print(f"\nExperiment: {answer_key['experiment_id']}")
    print(f"Stories generated: {len(mapping)}")

    # If ratings file provided, load it
    if args.ratings:
        with open(args.ratings) as f:
            ratings = json.load(f)
    else:
        # Interactive rating entry
        print("\n" + "-"*60)
        print("Enter your ratings from the blind evaluation sheet.")
        print("For each story ID, enter the TOTAL score (out of 25).")
        print("Type 'done' when finished.")
        print("-"*60 + "\n")

        ratings = {}
        for blind_id in mapping.keys():
            while True:
                try:
                    score = input(f"Story {blind_id} total score (0-25): ").strip()
                    if score.lower() == 'done':
                        break
                    score = int(score)
                    if 0 <= score <= 25:
                        ratings[blind_id] = score
                        break
                    else:
                        print("Score must be 0-25")
                except ValueError:
                    print("Enter a number 0-25")

            if score == 'done':
                break

    # Analyze results
    print("\n" + "="*60)
    print("RESULTS REVEAL")
    print("="*60)

    # Show each story's true identity
    print("\n### Story Identity Reveal\n")
    print(f"{'Blind ID':<10} {'Score':>6} {'Config':>8} {'Seed':<12} {'Models'}")
    print("-"*70)

    for blind_id, info in mapping.items():
        score = ratings.get(blind_id, "N/A")
        models = f"{info['models']['generator']} → {info['models']['editor']}"
        print(f"{blind_id:<10} {str(score):>6} {info['config']:>8} {info['seed']:<12} {models}")

    # Aggregate by config
    print("\n" + "="*60)
    print("AGGREGATE SCORES BY CONFIG")
    print("="*60)

    config_scores = defaultdict(list)
    for blind_id, info in mapping.items():
        if blind_id in ratings:
            config_scores[info['config']].append(ratings[blind_id])

    print(f"\n{'Config':<8} {'Avg Score':>10} {'Stories':>10} {'Description'}")
    print("-"*70)

    results = []
    for config, scores in sorted(config_scores.items()):
        avg = sum(scores) / len(scores) if scores else 0
        desc = config_descriptions.get(config, "")
        results.append((config, avg, len(scores), desc))
        print(f"{config:<8} {avg:>10.1f} {len(scores):>10} {desc}")

    # Winner
    if results:
        winner = max(results, key=lambda x: x[1])
        print("\n" + "="*60)
        print(f"🏆 WINNER: Config {winner[0]} — {winner[3]}")
        print(f"   Average score: {winner[1]:.1f}/25")
        print("="*60)

    # Aggregate by seed (to see if some prompts are harder)
    print("\n" + "-"*60)
    print("SCORES BY SEED (prompt difficulty check)")
    print("-"*60)

    seed_scores = defaultdict(list)
    for blind_id, info in mapping.items():
        if blind_id in ratings:
            seed_scores[info['seed']].append(ratings[blind_id])

    for seed, scores in sorted(seed_scores.items()):
        avg = sum(scores) / len(scores) if scores else 0
        print(f"{seed}: {avg:.1f}/25 avg (n={len(scores)})")

    # Cost analysis (rough estimates)
    print("\n" + "-"*60)
    print("COST ESTIMATE (per story)")
    print("-"*60)

    # Very rough: ~500 tokens in, ~500 tokens out per step, 3 steps
    cost_estimates = {
        "gemini-3-flash": 0.50 / 1_000_000 * 500 + 3.00 / 1_000_000 * 500,  # per step
        "gemini-2.5-flash": 0.30 / 1_000_000 * 500 + 2.50 / 1_000_000 * 500,
        "claude-haiku": 0.25 / 1_000_000 * 500 + 1.25 / 1_000_000 * 500,
        "claude-sonnet": 3.00 / 1_000_000 * 500 + 15.00 / 1_000_000 * 500,
        "claude-opus": 15.00 / 1_000_000 * 500 + 75.00 / 1_000_000 * 500,
    }

    for config_name, desc in config_descriptions.items():
        # Rough estimate based on config
        if "Gemini 3 Flash" in desc or "cheapest" in desc.lower():
            est = cost_estimates["gemini-3-flash"] * 3
        elif "Gemini 2.5" in desc:
            est = cost_estimates["gemini-2.5-flash"] * 3
        elif "Opus" in desc:
            est = (cost_estimates["claude-opus"] * 2 + cost_estimates["claude-sonnet"])
        elif "Sonnet" in desc:
            est = (cost_estimates["claude-sonnet"] * 2 + cost_estimates["claude-haiku"])
        else:
            est = cost_estimates["gemini-3-flash"] * 3

        print(f"Config {config_name}: ~${est:.4f} per story — {desc}")

    # Save ratings for future reference
    if not args.ratings and ratings:
        ratings_path = Path(args.answer_key).parent / f"{answer_key['experiment_id']}_RATINGS.json"
        with open(ratings_path, "w") as f:
            json.dump(ratings, f, indent=2)
        print(f"\nRatings saved to: {ratings_path}")


if __name__ == "__main__":
    main()
