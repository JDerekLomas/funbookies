#!/usr/bin/env python3
"""
Book Generation Experiment

Generate poetic and narrative books at 2 reading levels.
Tests the complete pipeline with story + reference prompt output.

Usage:
    python run_book_experiment.py
    python run_book_experiment.py --config D  # Use Claude Opus
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from config import (
    PIPELINE_CONFIGS, LEVEL_SPECS, STORY_MODES, StorySeed, get_api_keys
)
from book_generator import generate_complete_book
from evaluator import evaluate_story


# =============================================================================
# EXPERIMENT SEEDS
# =============================================================================

EXPERIMENT_SEEDS = [
    # Level B1 (CVC Short a, i) - 3 stories
    StorySeed(
        id="b1_cat_narrative",
        level="B1",
        mode="narrative",
        setting="A sunny kitchen, a cat on a mat, a girl named Pam",
        anchor="How cats choose their favorite napping spots based on warmth and safety",
        notes="Short a focus: cat, mat, sat, nap, lap, Pam, hat. Simple actions, warm feeling.",
    ),
    StorySeed(
        id="b1_pig_narrative",
        level="B1",
        mode="narrative",
        setting="A muddy farm, a pig pen, a boy named Tim",
        anchor="Why pigs roll in mud to cool down (they can't sweat)",
        notes="Short i focus: pig, big, dig, Tim, him, sit, did, mud. Playful energy.",
    ),
    StorySeed(
        id="b1_mix_poem",
        level="B1",
        mode="poem",
        setting="A child's bedroom, toys scattered, time for bed",
        anchor="The rhythm of tidying up - putting things in their spots",
        notes="Mix of short a and i: hat, bat, cat, sat, fit, bit, pit, sit. Rhythmic, simple.",
    ),
]


# =============================================================================
# WEB EXPERIMENT SAVING
# =============================================================================

def get_web_experiments_path():
    """Get path to public/experiments folder."""
    # Navigate up from scripts/story_generator to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    return project_root / "public" / "experiments"


def save_to_web_experiments(experiment_id, config_name, pipeline_config, results, evaluations):
    """Save experiment to public/experiments for web UI."""
    experiments_path = get_web_experiments_path()
    experiments_path.mkdir(parents=True, exist_ok=True)

    # Create experiment data for web UI
    experiment_data = {
        "id": experiment_id,
        "description": f"{config_name}: {pipeline_config.description}",
        "pipeline": config_name,
        "pipeline_description": pipeline_config.description,
        "timestamp": datetime.now().isoformat(),
        "story_count": len(results),
        "stories": [
            {
                "id": result.seed.id,
                "title": result.title,
                "level": result.seed.level,
                "mode": result.seed.mode,
                "story": result.story,
                "reference_prompt": result.reference_prompt,
                "setting": result.seed.setting,
                "anchor": result.seed.anchor,
            }
            for result in results
        ]
    }

    # Save experiment JSON
    exp_file = experiments_path / f"{experiment_id}.json"
    with open(exp_file, "w") as f:
        json.dump(experiment_data, f, indent=2)

    # Update index.json
    index_file = experiments_path / "index.json"
    if index_file.exists():
        with open(index_file) as f:
            index_data = json.load(f)
    else:
        index_data = {"experiments": []}

    # Add new experiment to index (at beginning)
    index_data["experiments"].insert(0, {
        "id": experiment_id,
        "description": f"{config_name}: {pipeline_config.description}",
        "pipeline": config_name,
        "timestamp": datetime.now().isoformat(),
        "story_count": len(results),
    })

    with open(index_file, "w") as f:
        json.dump(index_data, f, indent=2)

    print(f"\n[+] Saved to web experiments: {exp_file}")


# =============================================================================
# EXPERIMENT RUNNER
# =============================================================================

def run_experiment(config_name: str = "C", output_dir: str = "book_experiment"):
    """Run the book generation experiment."""

    load_dotenv()
    api_keys = get_api_keys()

    pipeline_config = PIPELINE_CONFIGS[config_name]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    experiment_id = f"books_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("\n" + "="*70)
    print("BOOK GENERATION EXPERIMENT")
    print("="*70)
    print(f"\nExperiment ID: {experiment_id}")
    print(f"Pipeline: {config_name} - {pipeline_config.description}")
    print(f"Books to generate: {len(EXPERIMENT_SEEDS)}")
    print(f"Output: {output_path}")
    print("\n" + "-"*70)

    results = []
    evaluations = []

    for seed in EXPERIMENT_SEEDS:
        print(f"\n{'='*70}")
        print(f"GENERATING: {seed.id}")
        print(f"Level: {seed.level} | Mode: {seed.mode}")
        print(f"Setting: {seed.setting[:60]}...")
        print(f"Anchor: {seed.anchor[:60]}...")
        print("="*70)

        # Generate title based on seed
        titles = {
            # B1 (CVC Short a, i)
            "b1_cat_narrative": "Cat on the Mat",
            "b1_pig_narrative": "The Big Pig",
            "b1_mix_poem": "Fit It In",
            # B3 (Final Blends)
            "b3_poem": "Splash and Stomp",
            "b3_narrative": "Ox and the Big Hip",
            # B4 (Initial Blends)
            "b4_frog_narrative": "Frog on the Log",
            "b4_sled_poem": "Sled Run",
            "b4_crab_narrative": "Crab Grab",
            # B5 (Digraphs)
            "b5_poem": "The Shimmer and the Shell",
            "b5_narrative": "The Shell Switch",
            # B6 (Magic E)
            "b6_a_e_narrative": "Jake's Lake",
            "b6_a_e_poem": "Bake Day",
            "b6_i_e_narrative": "Mike's Bike Ride",
            "b6_o_e_narrative": "A Home for Mole",
            # B7 (Vowel Teams)
            "b7_snail_narrative": "Snail Mail",
            "b7_boat_poem": "Sail Away",
            "b7_bee_narrative": "Bee's Big Day",
        }
        title = titles.get(seed.id, f"{seed.level} {seed.mode.title()}")

        try:
            # Generate complete book
            book_result = generate_complete_book(
                seed=seed,
                pipeline_config=pipeline_config,
                title=title,
                api_keys=api_keys,
                verbose=True,
            )

            # Evaluate the result
            print(f"\n[+] Evaluating story...")
            level_spec = LEVEL_SPECS[seed.level]
            # Use claude-haiku for evaluation if available, else gemini
            eval_model = "claude-haiku" if api_keys.get("anthropic") else "gemini-3-flash"
            evaluation = evaluate_story(
                story=book_result.story,
                level_spec=level_spec,
                mode=seed.mode,
                evaluator_model=eval_model,
                api_keys=api_keys,
                verbose=True,
            )

            results.append(book_result)
            evaluations.append({
                "seed_id": seed.id,
                "title": title,
                "level": seed.level,
                "mode": seed.mode,
                "story": book_result.story,  # Include story text for blind eval
                "curricular_total": evaluation.curricular_total,
                "creative_total": evaluation.creative_total,
                "final_score": evaluation.final_score,
                "best_line": evaluation.best_line,
                "worst_line": evaluation.worst_line,
                "hardest_word": evaluation.hardest_word,
                "pattern_words": evaluation.pattern_words_found,
                "curricular_verdict": evaluation.curricular_verdict,
                "creative_verdict": evaluation.creative_verdict,
                "ready": evaluation.ready_for_instruction,
            })

            print(f"\n   ✓ Curricular: {evaluation.curricular_total:.1f}/25")
            print(f"   ✓ Creative: {evaluation.creative_total:.1f}/25")
            print(f"   ✓ Final: {evaluation.final_score:.1f}/30")
            print(f"   ✓ Ready: {evaluation.ready_for_instruction}")

            # Save individual book files
            book_dir = output_path / seed.id
            book_dir.mkdir(exist_ok=True)

            # Save book JSON
            with open(book_dir / "book.json", "w") as f:
                json.dump(book_result.book_json, f, indent=2)

            # Save story
            with open(book_dir / "story.txt", "w") as f:
                f.write(f"# {title}\n")
                f.write(f"Level: {seed.level} | Mode: {seed.mode}\n\n")
                f.write(book_result.story)

            # Save reference prompt
            with open(book_dir / "reference_prompt.txt", "w") as f:
                f.write(book_result.reference_prompt)

            # Save artifacts
            with open(book_dir / "artifacts.json", "w") as f:
                json.dump({
                    "draft": book_result.draft,
                    "critique": book_result.critique,
                }, f, indent=2)

            print(f"\n   ✓ Files saved to: {book_dir}")

        except Exception as e:
            print(f"\n   ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Save experiment summary
    summary = {
        "experiment_id": experiment_id,
        "pipeline": config_name,
        "pipeline_description": pipeline_config.description,
        "generated_at": datetime.now().isoformat(),
        "books_generated": len(results),
        "evaluations": evaluations,
    }

    with open(output_path / f"{experiment_id}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Create readable report
    report_path = output_path / f"{experiment_id}_REPORT.md"
    with open(report_path, "w") as f:
        f.write(f"# Book Generation Experiment Report\n\n")
        f.write(f"**Experiment ID:** {experiment_id}\n")
        f.write(f"**Pipeline:** {config_name} - {pipeline_config.description}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")

        for result, eval_data in zip(results, evaluations):
            f.write(f"## {result.title}\n\n")
            f.write(f"**Level:** {result.seed.level} | **Mode:** {result.seed.mode}\n")
            f.write(f"**Setting:** {result.seed.setting}\n")
            f.write(f"**Anchor:** {result.seed.anchor}\n\n")

            f.write("### Scores\n\n")
            f.write(f"| Metric | Score |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Curricular | {eval_data['curricular_total']:.1f}/25 |\n")
            f.write(f"| Creative | {eval_data['creative_total']:.1f}/25 |\n")
            f.write(f"| **Final** | **{eval_data['final_score']:.1f}/30** |\n")
            f.write(f"| Ready for Instruction | {eval_data['ready']} |\n\n")

            f.write("### Verdicts\n\n")
            f.write(f"- **Curricular:** {eval_data['curricular_verdict']}\n")
            f.write(f"- **Creative:** {eval_data['creative_verdict']}\n\n")

            f.write("### Key Lines\n\n")
            f.write(f"- **Best:** {eval_data['best_line']}\n")
            f.write(f"- **Worst:** {eval_data['worst_line']}\n")
            f.write(f"- **Hardest word:** {eval_data['hardest_word']}\n\n")

            f.write("### Pattern Words Found\n\n")
            f.write(f"{', '.join(eval_data['pattern_words'][:15])}\n\n")

            f.write("### Story\n\n")
            f.write("```\n")
            f.write(result.story)
            f.write("\n```\n\n")

            f.write("### Reference Prompt\n\n")
            f.write("```\n")
            f.write(result.reference_prompt)
            f.write("\n```\n\n")

            f.write("---\n\n")

    # Save to public/experiments for web UI
    save_to_web_experiments(experiment_id, config_name, pipeline_config, results, evaluations)

    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    print(f"\nBooks generated: {len(results)}")
    print(f"\nResults saved to: {output_path}")
    print(f"Report: {report_path}")
    print(f"\nWeb UI: https://funbookies.com/experiments/")

    # Print summary table
    print("\n" + "-"*70)
    print("SUMMARY")
    print("-"*70)
    print(f"\n{'Title':<30} {'Level':<6} {'Mode':<10} {'Curr':>6} {'Creat':>6} {'Final':>6} {'Ready':<8}")
    print("-"*80)
    for result, eval_data in zip(results, evaluations):
        print(f"{result.title:<30} {eval_data['level']:<6} {eval_data['mode']:<10} "
              f"{eval_data['curricular_total']:>6.1f} {eval_data['creative_total']:>6.1f} "
              f"{eval_data['final_score']:>6.1f} {eval_data['ready']:<8}")


def main():
    parser = argparse.ArgumentParser(description="Run book generation experiment")
    parser.add_argument("--config", default="C", help="Pipeline config (A-F)")
    parser.add_argument("--output", default="book_experiment", help="Output directory")
    args = parser.parse_args()

    run_experiment(config_name=args.config, output_dir=args.output)


if __name__ == "__main__":
    main()
