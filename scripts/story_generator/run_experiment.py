#!/usr/bin/env python3
"""
Story Generation Experiment Runner

Runs multiple configurations across multiple seeds and produces
blind-testable output for quality comparison.

Usage:
    # Run full experiment (all configs × all seeds)
    python run_experiment.py

    # Run specific configs
    python run_experiment.py --configs A,B,D

    # Run specific seeds
    python run_experiment.py --seeds seed_01,seed_03

    # Quick test (1 config × 1 seed)
    python run_experiment.py --quick
"""

import argparse
import json
import os
import random
import string
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from config import (
    PIPELINE_CONFIGS, TEST_SEEDS, LEVEL_SPECS, STORY_MODES,
    get_api_keys, StorySeed
)
from pipeline import run_pipeline, PipelineResult


# =============================================================================
# EXPERIMENT OUTPUT
# =============================================================================

def generate_blind_id() -> str:
    """Generate a random ID to hide which config produced which story."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def save_experiment_results(
    results: list[PipelineResult],
    output_dir: Path,
    experiment_id: str
):
    """Save results in formats suitable for blind testing."""

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create blind mapping (hidden until evaluation is done)
    blind_mapping = {}
    blind_stories = []

    for result in results:
        blind_id = generate_blind_id()
        blind_mapping[blind_id] = {
            "config": result.config_name,
            "seed": result.seed_id,
            "models": result.model_info,
        }

        blind_stories.append({
            "blind_id": blind_id,
            "seed_id": result.seed_id,
            "level": LEVEL_SPECS[TEST_SEEDS[[s.id for s in TEST_SEEDS].index(result.seed_id)].level].level,
            "mode": TEST_SEEDS[[s.id for s in TEST_SEEDS].index(result.seed_id)].mode,
            "story": result.final,
        })

    # Shuffle so order doesn't reveal anything
    random.shuffle(blind_stories)

    # === OUTPUT 1: Blind evaluation sheet (for human rating) ===
    eval_sheet_path = output_dir / f"{experiment_id}_BLIND_EVAL.md"
    with open(eval_sheet_path, "w") as f:
        f.write(f"# Story Quality Evaluation\n")
        f.write(f"Experiment: {experiment_id}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        f.write("## Instructions\n\n")
        f.write("Rate each story on the criteria below (1-5 scale).\n")
        f.write("Do NOT look at the answer key until all ratings are complete.\n\n")
        f.write("### Rating Scale\n")
        f.write("- **5** = Exceptional - has soul, want to read again\n")
        f.write("- **4** = Good - works well, minor issues\n")
        f.write("- **3** = Adequate - functional but flat\n")
        f.write("- **2** = Weak - noticeable problems\n")
        f.write("- **1** = Poor - doesn't work\n\n")
        f.write("---\n\n")

        for i, story in enumerate(blind_stories, 1):
            f.write(f"## Story {i} — ID: `{story['blind_id']}`\n\n")
            f.write(f"**Level:** {story['level']} | **Mode:** {story['mode']}\n\n")
            f.write("```\n")
            f.write(story['story'])
            f.write("\n```\n\n")
            f.write("### Ratings\n\n")
            f.write("| Criteria | Score (1-5) | Notes |\n")
            f.write("|----------|-------------|-------|\n")
            f.write("| Rhythm & Sound | ___ | |\n")
            f.write("| Sensory Grounding | ___ | |\n")
            f.write("| Emotional Truth | ___ | |\n")
            f.write("| Child Engagement | ___ | |\n")
            f.write("| Show vs Tell | ___ | |\n")
            f.write("| **TOTAL** | ___/25 | |\n\n")
            f.write("**Would you publish this?** [ ] Yes  [ ] With edits  [ ] No\n\n")
            f.write("**Best line:**\n\n")
            f.write("**Worst line:**\n\n")
            f.write("---\n\n")

    print(f"✓ Blind evaluation sheet: {eval_sheet_path}")

    # === OUTPUT 2: Answer key (DO NOT OPEN until eval is done) ===
    answer_key_path = output_dir / f"{experiment_id}_ANSWER_KEY.json"
    with open(answer_key_path, "w") as f:
        json.dump({
            "experiment_id": experiment_id,
            "generated_at": datetime.now().isoformat(),
            "mapping": blind_mapping,
            "config_descriptions": {
                name: config.description
                for name, config in PIPELINE_CONFIGS.items()
            }
        }, f, indent=2)

    print(f"✓ Answer key (DON'T PEEK): {answer_key_path}")

    # === OUTPUT 3: Full results with all artifacts ===
    full_results_path = output_dir / f"{experiment_id}_FULL_RESULTS.json"
    full_data = {
        "experiment_id": experiment_id,
        "generated_at": datetime.now().isoformat(),
        "results": []
    }

    for result in results:
        full_data["results"].append({
            "seed_id": result.seed_id,
            "config_name": result.config_name,
            "models": result.model_info,
            "draft": result.draft,
            "critique": result.critique,
            "final": result.final,
            "decodability": result.decodability,
            "timestamps": result.timestamps,
        })

    with open(full_results_path, "w") as f:
        json.dump(full_data, f, indent=2)

    print(f"✓ Full results: {full_results_path}")

    # === OUTPUT 4: Quick comparison (stories side by side per seed) ===
    comparison_path = output_dir / f"{experiment_id}_COMPARISON.md"
    with open(comparison_path, "w") as f:
        f.write(f"# Story Comparison by Seed\n")
        f.write(f"Experiment: {experiment_id}\n\n")
        f.write("**WARNING: This file reveals which config produced which story.**\n")
        f.write("**Use BLIND_EVAL.md for unbiased evaluation.**\n\n")
        f.write("---\n\n")

        # Group by seed
        by_seed = {}
        for result in results:
            if result.seed_id not in by_seed:
                by_seed[result.seed_id] = []
            by_seed[result.seed_id].append(result)

        for seed_id, seed_results in by_seed.items():
            seed = next(s for s in TEST_SEEDS if s.id == seed_id)
            f.write(f"## {seed_id}\n\n")
            f.write(f"**Setting:** {seed.setting}\n")
            f.write(f"**Anchor:** {seed.anchor}\n")
            f.write(f"**Mode:** {seed.mode}\n\n")

            for result in seed_results:
                config = PIPELINE_CONFIGS[result.config_name]
                f.write(f"### Config {result.config_name}: {config.description}\n\n")
                f.write(f"*Generator: {result.model_info['generator']} | ")
                f.write(f"Critic: {result.model_info['critic']} | ")
                f.write(f"Editor: {result.model_info['editor']}*\n\n")
                f.write(f"**Decodability:** {result.decodability['decodability']:.1%}\n\n")
                f.write("```\n")
                f.write(result.final)
                f.write("\n```\n\n")

            f.write("---\n\n")

    print(f"✓ Comparison view: {comparison_path}")

    return eval_sheet_path


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Run story generation experiment")
    parser.add_argument("--configs", type=str, help="Comma-separated config names (e.g., A,B,D)")
    parser.add_argument("--seeds", type=str, help="Comma-separated seed IDs")
    parser.add_argument("--quick", action="store_true", help="Quick test: 1 config × 1 seed")
    parser.add_argument("--output", type=str, default="experiments", help="Output directory")
    parser.add_argument("--auto-eval", action="store_true", help="Run automatic LLM evaluation after generation")
    parser.add_argument("--eval-model", type=str, default="claude-sonnet", help="Model for auto-evaluation")
    args = parser.parse_args()

    # Load environment
    load_dotenv()
    api_keys = get_api_keys()

    print("\n" + "="*60)
    print("STORY GENERATION EXPERIMENT")
    print("="*60)
    print(f"\nAPI keys: {', '.join(k for k, v in api_keys.items() if v)}")

    # Determine what to run
    if args.quick:
        configs_to_run = ["A"]  # Just Gemini 3 Flash
        seeds_to_run = [TEST_SEEDS[0]]
    else:
        if args.configs:
            configs_to_run = [c.strip() for c in args.configs.split(",")]
        else:
            # Default: run A (cheap), C (mid), D (expensive) for comparison
            configs_to_run = ["A", "C", "D"]

        if args.seeds:
            seed_ids = [s.strip() for s in args.seeds.split(",")]
            seeds_to_run = [s for s in TEST_SEEDS if s.id in seed_ids]
        else:
            # Default: first 2 seeds
            seeds_to_run = TEST_SEEDS[:2]

    # Validate configs
    for c in configs_to_run:
        if c not in PIPELINE_CONFIGS:
            print(f"ERROR: Unknown config '{c}'. Available: {list(PIPELINE_CONFIGS.keys())}")
            return

    print(f"\nConfigs to run: {configs_to_run}")
    print(f"Seeds to run: {[s.id for s in seeds_to_run]}")
    print(f"Total runs: {len(configs_to_run) * len(seeds_to_run)}")

    # Check API keys for required providers
    required_providers = set()
    for config_name in configs_to_run:
        config = PIPELINE_CONFIGS[config_name]
        required_providers.add(config.get_generator().provider)
        required_providers.add(config.get_critic().provider)
        required_providers.add(config.get_editor().provider)

    missing_keys = [p for p in required_providers if not api_keys.get(p)]
    if missing_keys:
        print(f"\nERROR: Missing API keys for: {missing_keys}")
        print("Set these environment variables:")
        for p in missing_keys:
            if p == "google":
                print("  export GOOGLE_AI_API_KEY=your_key")
            elif p == "anthropic":
                print("  export ANTHROPIC_API_KEY=your_key")
            elif p == "openai":
                print("  export OPENAI_API_KEY=your_key")
        return

    # Run experiment
    experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = []

    print(f"\nExperiment ID: {experiment_id}")
    print("\n" + "-"*60)

    for seed in seeds_to_run:
        for config_name in configs_to_run:
            config = PIPELINE_CONFIGS[config_name]
            try:
                result = run_pipeline(seed, config, api_keys, verbose=True)
                results.append(result)
            except Exception as e:
                print(f"\nERROR running {config_name} on {seed.id}: {e}")
                continue

    # Save results
    if results:
        output_dir = Path(args.output)
        eval_path = save_experiment_results(results, output_dir, experiment_id)

        print("\n" + "="*60)
        print("EXPERIMENT COMPLETE")
        print("="*60)
        print(f"\nGenerated {len(results)} stories.")

        # Run auto-evaluation if requested
        if args.auto_eval:
            print("\n" + "-"*60)
            print("RUNNING AUTO-EVALUATION")
            print("-"*60)

            from evaluator import evaluate_experiment_results

            full_results_path = output_dir / f"{experiment_id}_FULL_RESULTS.json"
            eval_output_path = output_dir / f"{experiment_id}_AUTO_EVAL.json"

            summary = evaluate_experiment_results(
                str(full_results_path),
                evaluator_model=args.eval_model,
                output_file=str(eval_output_path),
                verbose=True,
            )

            print("\n" + "="*60)
            print("AUTO-EVALUATION RESULTS")
            print("="*60)
            for config, stats in summary["summary"].items():
                print(f"Config {config}: {stats['avg_score']:.1f}/28 avg")
            print(f"\n🏆 Auto-eval winner: Config {summary['winner']}")

        print(f"\nNEXT STEPS:")
        print(f"1. Open {eval_path}")
        print(f"2. Rate each story blindly (don't peek at answer key!)")
        print(f"3. After rating all, check the answer key to see which config won")
        if args.auto_eval:
            print(f"4. Compare your ratings to auto-eval: {eval_output_path}")
    else:
        print("\nNo results generated.")


if __name__ == "__main__":
    main()
