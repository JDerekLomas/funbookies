#!/usr/bin/env python3
"""
FunBookies Quality Evaluation System

Provides both automated and manual quality evaluation for:
- Generated images (consistency, style, appropriateness)
- Story text (reading level accuracy, engagement, decodability)
- Overall book quality

Uses Claude Vision for automated image analysis.
"""

import json
import os
import base64
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import anthropic

# Evaluation criteria with scoring rubrics
IMAGE_CRITERIA = {
    "character_consistency": {
        "description": "Does the character look consistent with other pages?",
        "weight": 0.25,
        "rubric": {
            5: "Perfect match - same colors, proportions, features",
            4: "Minor variations but clearly same character",
            3: "Recognizable but noticeable differences",
            2: "Significant inconsistencies",
            1: "Barely recognizable as same character"
        }
    },
    "style_consistency": {
        "description": "Does the art style match the book's aesthetic?",
        "weight": 0.20,
        "rubric": {
            5: "Perfect style match - cohesive with other pages",
            4: "Very similar style with minor variations",
            3: "Same general style but some differences",
            2: "Noticeably different style",
            1: "Completely different style"
        }
    },
    "text_illustration_match": {
        "description": "Does the image accurately depict the page text?",
        "weight": 0.25,
        "rubric": {
            5: "Perfect match - illustrates text exactly",
            4: "Closely matches with minor additions",
            3: "Generally matches but some elements off",
            2: "Loosely related to text",
            1: "Does not match text at all"
        }
    },
    "child_appropriate": {
        "description": "Is the image appropriate for young children?",
        "weight": 0.15,
        "rubric": {
            5: "Perfect - warm, friendly, engaging for children",
            4: "Very appropriate with minor concerns",
            3: "Acceptable but could be improved",
            2: "Some concerning elements",
            1: "Not appropriate for children"
        }
    },
    "visual_clarity": {
        "description": "Is the image clear and easy to understand?",
        "weight": 0.15,
        "rubric": {
            5: "Crystal clear - easy to understand at a glance",
            4: "Clear with good composition",
            3: "Understandable but somewhat cluttered",
            2: "Confusing or unclear",
            1: "Very difficult to understand"
        }
    }
}

TEXT_CRITERIA = {
    "reading_level_accuracy": {
        "description": "Does the text match the target reading level?",
        "weight": 0.30,
        "rubric": {
            5: "Perfect - all words appropriate for level",
            4: "Very good - 1-2 slightly challenging words",
            3: "Acceptable - a few words above level",
            2: "Too difficult - many words above level",
            1: "Way too difficult for target level"
        }
    },
    "decodability": {
        "description": "Can all words be decoded using target phonics skills?",
        "weight": 0.30,
        "rubric": {
            5: "All words fully decodable or proper sight words",
            4: "Nearly all words decodable",
            3: "Most words decodable",
            2: "Many words not decodable",
            1: "Most words cannot be decoded at this level"
        }
    },
    "engagement": {
        "description": "Is the story engaging for young readers?",
        "weight": 0.20,
        "rubric": {
            5: "Highly engaging - clear arc, emotional resonance",
            4: "Engaging with good story flow",
            3: "Moderately engaging",
            2: "Somewhat boring or confusing",
            1: "Not engaging at all"
        }
    },
    "sentence_structure": {
        "description": "Are sentences appropriately structured for the level?",
        "weight": 0.20,
        "rubric": {
            5: "Perfect sentence length and structure",
            4: "Appropriate with minor variations",
            3: "Some sentences too long or complex",
            2: "Many sentences inappropriate",
            1: "Sentence structure too advanced"
        }
    }
}


@dataclass
class ImageEvaluation:
    """Evaluation result for a single image"""
    page_id: str
    image_path: str
    scores: dict = field(default_factory=dict)
    overall_score: float = 0.0
    feedback: str = ""
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TextEvaluation:
    """Evaluation result for story text"""
    page_id: str
    text: str
    target_level: int
    scores: dict = field(default_factory=dict)
    overall_score: float = 0.0
    word_analysis: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)


@dataclass
class BookEvaluation:
    """Complete book evaluation"""
    book_slug: str
    title: str
    level: int
    image_evaluations: list = field(default_factory=list)
    text_evaluation: Optional[TextEvaluation] = None
    overall_image_score: float = 0.0
    overall_text_score: float = 0.0
    overall_score: float = 0.0
    summary: str = ""
    recommendations: list = field(default_factory=list)
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class QualityEvaluator:
    """Evaluate book quality using Claude Vision and text analysis"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.books_dir = self.project_root / "public" / "books"
        self.client = anthropic.Anthropic()

    def _load_image_base64(self, image_path: str) -> Optional[str]:
        """Load image and convert to base64"""
        full_path = self.books_dir / image_path
        if not full_path.exists():
            return None

        with open(full_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def _get_media_type(self, image_path: str) -> str:
        """Get media type from file extension"""
        ext = Path(image_path).suffix.lower()
        return {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }.get(ext, "image/png")

    def evaluate_image(
        self,
        image_path: str,
        page_text: str,
        character_description: str,
        reference_image_path: Optional[str] = None
    ) -> ImageEvaluation:
        """Evaluate a single image using Claude Vision"""

        image_b64 = self._load_image_base64(image_path)
        if not image_b64:
            return ImageEvaluation(
                page_id=Path(image_path).stem,
                image_path=image_path,
                overall_score=0.0,
                feedback="Image file not found",
                issues=["Image file does not exist"]
            )

        # Build evaluation prompt
        criteria_text = "\n".join([
            f"- {name}: {info['description']} (Weight: {info['weight']*100}%)"
            for name, info in IMAGE_CRITERIA.items()
        ])

        prompt = f"""Evaluate this children's book illustration. Score each criterion 1-5.

## PAGE TEXT
"{page_text}"

## CHARACTER DESCRIPTION
{character_description}

## EVALUATION CRITERIA
{criteria_text}

## INSTRUCTIONS
1. Examine the image carefully
2. Score each criterion from 1 (poor) to 5 (excellent)
3. Provide specific feedback
4. List any issues that need fixing
5. Suggest improvements

## OUTPUT FORMAT (JSON)
{{
  "scores": {{
    "character_consistency": 4,
    "style_consistency": 5,
    "text_illustration_match": 4,
    "child_appropriate": 5,
    "visual_clarity": 4
  }},
  "feedback": "Overall assessment in 2-3 sentences",
  "issues": ["List of specific issues"],
  "suggestions": ["List of improvement suggestions"]
}}

Return ONLY the JSON."""

        # Build message with image
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": self._get_media_type(image_path),
                    "data": image_b64
                }
            },
            {"type": "text", "text": prompt}
        ]

        # Add reference image if provided
        if reference_image_path:
            ref_b64 = self._load_image_base64(reference_image_path)
            if ref_b64:
                content.insert(0, {
                    "type": "text",
                    "text": "Reference image for character/style consistency:"
                })
                content.insert(1, {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": self._get_media_type(reference_image_path),
                        "data": ref_b64
                    }
                })

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": content}]
            )

            response_text = message.content[0].text

            # Parse JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text)

            # Calculate weighted overall score
            overall = sum(
                result["scores"].get(name, 3) * info["weight"]
                for name, info in IMAGE_CRITERIA.items()
            )

            return ImageEvaluation(
                page_id=Path(image_path).stem,
                image_path=image_path,
                scores=result["scores"],
                overall_score=round(overall, 2),
                feedback=result.get("feedback", ""),
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", [])
            )

        except Exception as e:
            return ImageEvaluation(
                page_id=Path(image_path).stem,
                image_path=image_path,
                overall_score=0.0,
                feedback=f"Evaluation failed: {str(e)}",
                issues=[f"Error during evaluation: {str(e)}"]
            )

    def evaluate_text(self, book_data: dict) -> TextEvaluation:
        """Evaluate story text for reading level accuracy"""

        # Extract all story text
        story_pages = [p for p in book_data["pages"] if p.get("type") == "story"]
        full_text = " ".join([p.get("text", "") for p in story_pages])

        level = book_data.get("level", 2)
        word_list = book_data.get("word_list", {})

        prompt = f"""Evaluate this children's leveled reader text for reading level accuracy.

## TARGET READING LEVEL: {level}
- Expected skill: {book_data.get('skill', 'Unknown')}
- Description: {book_data.get('skill_description', 'Unknown')}

## INTENDED WORD LISTS
- Sound-out words: {', '.join(word_list.get('sound_out', []))}
- Sight words: {', '.join(word_list.get('sight', []))}
- New vocabulary: {', '.join(word_list.get('new', []))}

## STORY TEXT
{full_text}

## EVALUATION CRITERIA
1. Reading Level Accuracy (30%): Are all words appropriate for level {level}?
2. Decodability (30%): Can words be decoded using target phonics skills?
3. Engagement (20%): Is the story engaging with emotional arc?
4. Sentence Structure (20%): Appropriate length and complexity?

## INSTRUCTIONS
1. Analyze each word for decodability at level {level}
2. Score each criterion 1-5
3. Identify any words that are too difficult
4. Suggest replacements for problematic words

## OUTPUT FORMAT (JSON)
{{
  "scores": {{
    "reading_level_accuracy": 4,
    "decodability": 4,
    "engagement": 5,
    "sentence_structure": 4
  }},
  "word_analysis": {{
    "total_unique_words": 50,
    "decodable_words": 45,
    "sight_words": 10,
    "problematic_words": ["word1", "word2"]
  }},
  "issues": ["List of specific issues"],
  "suggestions": ["List of improvements with word replacements"]
}}

Return ONLY the JSON."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = json.loads(response_text)

            # Calculate weighted overall score
            overall = sum(
                result["scores"].get(name, 3) * info["weight"]
                for name, info in TEXT_CRITERIA.items()
            )

            return TextEvaluation(
                page_id="full_text",
                text=full_text,
                target_level=level,
                scores=result["scores"],
                overall_score=round(overall, 2),
                word_analysis=result.get("word_analysis", {}),
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", [])
            )

        except Exception as e:
            return TextEvaluation(
                page_id="full_text",
                text=full_text,
                target_level=level,
                overall_score=0.0,
                issues=[f"Evaluation failed: {str(e)}"]
            )

    def evaluate_book(
        self,
        book_slug: str,
        evaluate_images: bool = True,
        evaluate_text: bool = True,
        sample_images: int = 5
    ) -> BookEvaluation:
        """Perform complete book evaluation"""

        # Load book data
        book_path = self.books_dir / f"{book_slug}.json"
        with open(book_path) as f:
            book_data = json.load(f)

        evaluation = BookEvaluation(
            book_slug=book_slug,
            title=book_data.get("title", "Unknown"),
            level=book_data.get("level", 0)
        )

        char_desc = book_data.get("character_description", "cartoon character")

        # Evaluate images
        if evaluate_images:
            story_pages = [p for p in book_data["pages"]
                          if p.get("type") in ("story", "cover") and p.get("image")]

            # Sample images if too many
            if len(story_pages) > sample_images:
                import random
                story_pages = random.sample(story_pages, sample_images)

            # Use first image as reference
            reference_image = story_pages[0].get("image") if story_pages else None

            for page in story_pages:
                img_eval = self.evaluate_image(
                    image_path=page.get("image", ""),
                    page_text=page.get("text", ""),
                    character_description=char_desc,
                    reference_image_path=reference_image if page != story_pages[0] else None
                )
                evaluation.image_evaluations.append(img_eval)

            if evaluation.image_evaluations:
                evaluation.overall_image_score = round(
                    sum(e.overall_score for e in evaluation.image_evaluations) /
                    len(evaluation.image_evaluations), 2
                )

        # Evaluate text
        if evaluate_text:
            evaluation.text_evaluation = self.evaluate_text(book_data)
            evaluation.overall_text_score = evaluation.text_evaluation.overall_score

        # Calculate overall score (60% images, 40% text)
        if evaluate_images and evaluate_text:
            evaluation.overall_score = round(
                evaluation.overall_image_score * 0.6 +
                evaluation.overall_text_score * 0.4, 2
            )
        elif evaluate_images:
            evaluation.overall_score = evaluation.overall_image_score
        else:
            evaluation.overall_score = evaluation.overall_text_score

        # Generate summary and recommendations
        evaluation.summary = self._generate_summary(evaluation)
        evaluation.recommendations = self._generate_recommendations(evaluation)

        return evaluation

    def _generate_summary(self, evaluation: BookEvaluation) -> str:
        """Generate human-readable summary"""
        score = evaluation.overall_score
        if score >= 4.5:
            quality = "Excellent"
        elif score >= 4.0:
            quality = "Very Good"
        elif score >= 3.5:
            quality = "Good"
        elif score >= 3.0:
            quality = "Acceptable"
        else:
            quality = "Needs Improvement"

        return f"{quality} quality ({score}/5.0). Images: {evaluation.overall_image_score}/5.0, Text: {evaluation.overall_text_score}/5.0"

    def _generate_recommendations(self, evaluation: BookEvaluation) -> list:
        """Generate actionable recommendations"""
        recs = []

        # Image recommendations
        low_image_scores = [e for e in evaluation.image_evaluations if e.overall_score < 3.5]
        if low_image_scores:
            pages = ", ".join([e.page_id for e in low_image_scores])
            recs.append(f"Regenerate images for: {pages}")

        # Collect all image issues
        all_issues = []
        for img_eval in evaluation.image_evaluations:
            all_issues.extend(img_eval.issues)
        if all_issues:
            recs.append(f"Address image issues: {'; '.join(all_issues[:3])}")

        # Text recommendations
        if evaluation.text_evaluation:
            if evaluation.text_evaluation.overall_score < 4.0:
                recs.append("Review and simplify text for reading level accuracy")
            problematic = evaluation.text_evaluation.word_analysis.get("problematic_words", [])
            if problematic:
                recs.append(f"Replace difficult words: {', '.join(problematic[:5])}")

        return recs

    def save_evaluation(self, evaluation: BookEvaluation) -> Path:
        """Save evaluation to JSON file"""
        output_dir = self.project_root / "evaluations"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"{evaluation.book_slug}_eval_{timestamp}.json"

        # Convert to dict
        eval_dict = {
            "book_slug": evaluation.book_slug,
            "title": evaluation.title,
            "level": evaluation.level,
            "overall_score": evaluation.overall_score,
            "overall_image_score": evaluation.overall_image_score,
            "overall_text_score": evaluation.overall_text_score,
            "summary": evaluation.summary,
            "recommendations": evaluation.recommendations,
            "evaluated_at": evaluation.evaluated_at,
            "image_evaluations": [
                {
                    "page_id": e.page_id,
                    "image_path": e.image_path,
                    "scores": e.scores,
                    "overall_score": e.overall_score,
                    "feedback": e.feedback,
                    "issues": e.issues,
                    "suggestions": e.suggestions
                }
                for e in evaluation.image_evaluations
            ],
            "text_evaluation": {
                "scores": evaluation.text_evaluation.scores,
                "overall_score": evaluation.text_evaluation.overall_score,
                "word_analysis": evaluation.text_evaluation.word_analysis,
                "issues": evaluation.text_evaluation.issues,
                "suggestions": evaluation.text_evaluation.suggestions
            } if evaluation.text_evaluation else None
        }

        with open(output_path, "w") as f:
            json.dump(eval_dict, f, indent=2)

        print(f"Evaluation saved to: {output_path}")
        return output_path


# CLI interface
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate FunBookies book quality")
    parser.add_argument("book_slug", help="Book slug to evaluate")
    parser.add_argument("--images-only", action="store_true", help="Only evaluate images")
    parser.add_argument("--text-only", action="store_true", help="Only evaluate text")
    parser.add_argument("--sample", type=int, default=5, help="Number of images to sample")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    evaluator = QualityEvaluator(args.project_root)

    evaluation = evaluator.evaluate_book(
        args.book_slug,
        evaluate_images=not args.text_only,
        evaluate_text=not args.images_only,
        sample_images=args.sample
    )

    evaluator.save_evaluation(evaluation)

    # Print summary
    print("\n" + "="*60)
    print(f"EVALUATION: {evaluation.title}")
    print("="*60)
    print(f"\n{evaluation.summary}\n")

    if evaluation.recommendations:
        print("RECOMMENDATIONS:")
        for rec in evaluation.recommendations:
            print(f"  - {rec}")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
