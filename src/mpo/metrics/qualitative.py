"""
Qualitative metrics for prompt evaluation.

Provides rubric-based evaluation and readability metrics for
culturally-adapted responses.
"""

from typing import Dict, List
import textstat
from enum import Enum


class CulturalAppropriatenessScore(Enum):
    """Cultural appropriateness rating scale."""
    EXCELLENT = 5
    GOOD = 4
    ADEQUATE = 3
    POOR = 2
    INAPPROPRIATE = 1


def calculate_readability_metrics(response: str, language: str = "en") -> Dict[str, any]:
    """
    Calculate readability metrics.

    Args:
        response: Response text
        language: Language code (affects which metrics are applicable)

    Returns:
        Dictionary with readability scores
    """
    metrics = {}

    # English readability metrics
    if language == "en":
        metrics["flesch_reading_ease"] = round(textstat.flesch_reading_ease(response), 2)
        metrics["flesch_kincaid_grade"] = round(textstat.flesch_kincaid_grade(response), 2)
        metrics["gunning_fog"] = round(textstat.gunning_fog(response), 2)
        metrics["smog_index"] = round(textstat.smog_index(response), 2)
        metrics["automated_readability_index"] = round(textstat.automated_readability_index(response), 2)

        # Interpretation
        fre = metrics["flesch_reading_ease"]
        if fre >= 90:
            metrics["readability_level"] = "Very Easy"
        elif fre >= 80:
            metrics["readability_level"] = "Easy"
        elif fre >= 70:
            metrics["readability_level"] = "Fairly Easy"
        elif fre >= 60:
            metrics["readability_level"] = "Standard"
        elif fre >= 50:
            metrics["readability_level"] = "Fairly Difficult"
        elif fre >= 30:
            metrics["readability_level"] = "Difficult"
        else:
            metrics["readability_level"] = "Very Difficult"

    else:
        # For non-English, use language-agnostic metrics
        metrics["syllable_count"] = textstat.syllable_count(response)
        metrics["lexicon_count"] = textstat.lexicon_count(response)
        metrics["sentence_count"] = textstat.sentence_count(response)
        metrics["avg_syllables_per_word"] = round(
            metrics["syllable_count"] / max(metrics["lexicon_count"], 1), 2
        )
        metrics["avg_words_per_sentence"] = round(
            metrics["lexicon_count"] / max(metrics["sentence_count"], 1), 2
        )

        # Simple complexity score (higher = more complex)
        complexity = (
            metrics["avg_syllables_per_word"] * 30 +
            metrics["avg_words_per_sentence"] * 2
        )
        metrics["complexity_score"] = round(complexity, 2)

        if language == "de":
            metrics["readability_level"] = "German (custom metrics)"
        elif language == "es":
            metrics["readability_level"] = "Spanish (custom metrics)"

    return metrics


def evaluate_cultural_appropriateness(
    response: str,
    language: str,
    formality: str,
    domain: str
) -> Dict[str, any]:
    """
    Evaluate cultural appropriateness using a rubric.

    Note: This is a rule-based heuristic. In production, consider
    human evaluation or fine-tuned classification models.

    Args:
        response: Response text
        language: Language code
        formality: Target formality level
        domain: Prompt domain

    Returns:
        Dictionary with appropriateness scores
    """
    scores = {
        "language": language,
        "formality_target": formality,
        "domain": domain,
        "criteria": {}
    }

    # Criteria 1: Greeting appropriateness
    greeting_score = _evaluate_greeting(response, language, formality)
    scores["criteria"]["greeting"] = greeting_score

    # Criteria 2: Formality match
    formality_score = _evaluate_formality_match(response, language, formality)
    scores["criteria"]["formality_match"] = formality_score

    # Criteria 3: Cultural markers
    cultural_markers_score = _evaluate_cultural_markers(response, language, domain)
    scores["criteria"]["cultural_markers"] = cultural_markers_score

    # Criteria 4: Closing appropriateness
    closing_score = _evaluate_closing(response, language, formality)
    scores["criteria"]["closing"] = closing_score

    # Overall score (average)
    total_score = sum([
        greeting_score["score"],
        formality_score["score"],
        cultural_markers_score["score"],
        closing_score["score"]
    ]) / 4

    scores["overall_score"] = round(total_score, 2)
    scores["overall_rating"] = _score_to_rating(total_score)

    return scores


def _evaluate_greeting(response: str, language: str, formality: str) -> Dict:
    """Evaluate greeting appropriateness."""
    score = 3  # Default: adequate
    notes = []

    if language == "de":
        if formality == "formal":
            if "Sehr geehrte" in response:
                score = 5
                notes.append("Excellent: Very formal German greeting")
            elif "Guten Tag" in response:
                score = 4
                notes.append("Good: Appropriate formal greeting")
            elif "Hallo" in response:
                score = 2
                notes.append("Poor: Too casual for formal context")
        elif formality == "casual":
            if "Hallo" in response or "Hi" in response:
                score = 5
                notes.append("Excellent: Casual greeting matches formality")
            elif "Guten Tag" in response:
                score = 3
                notes.append("Adequate: Slightly formal for casual context")

    elif language == "es":
        if formality == "formal":
            if "Estimado" in response or "Estimada" in response:
                score = 5
                notes.append("Excellent: Formal Spanish greeting")
            elif "Buenos días" in response:
                score = 4
                notes.append("Good: Professional greeting")
            elif "Hola" in response:
                score = 2
                notes.append("Poor: Too casual for formal context")
        elif formality == "casual":
            if "Hola" in response or "¿Qué tal?" in response:
                score = 5
                notes.append("Excellent: Casual greeting matches formality")

    elif language == "en":
        if formality == "formal":
            if "Dear" in response[:50]:
                score = 5
                notes.append("Excellent: Formal English greeting")
            elif response.startswith("Please"):
                score = 4
                notes.append("Good: Polite formal opening")

    return {"score": score, "notes": notes}


def _evaluate_formality_match(response: str, language: str, formality: str) -> Dict:
    """Evaluate formality match."""
    score = 3
    notes = []

    if language == "de":
        has_sie = "Sie" in response
        has_du = "du" in response.lower()

        if formality in ["formal", "neutral"]:
            if has_sie and not has_du:
                score = 5
                notes.append("Perfect: Uses 'Sie' consistently")
            elif has_du:
                score = 2
                notes.append("Poor: Uses 'du' in formal context")
        elif formality == "casual":
            if has_du and not has_sie:
                score = 5
                notes.append("Perfect: Uses 'du' for casual tone")

    elif language == "es":
        has_usted = "usted" in response.lower()
        has_tu = "tú" in response.lower()

        if formality in ["formal", "neutral"]:
            if has_usted and not has_tu:
                score = 5
                notes.append("Perfect: Uses 'usted' consistently")
            elif has_tu:
                score = 2
                notes.append("Poor: Uses 'tú' in formal context")
        elif formality == "casual":
            if has_tu and not has_usted:
                score = 5
                notes.append("Perfect: Uses 'tú' for casual tone")

    return {"score": score, "notes": notes}


def _evaluate_cultural_markers(response: str, language: str, domain: str) -> Dict:
    """Evaluate presence of cultural markers."""
    score = 3
    notes = []

    if language == "es" and domain == "business":
        # Spanish business contexts value relational preambles
        if "Espero que" in response:
            score += 1
            notes.append("Good: Includes well-being inquiry (Spanish cultural norm)")
        if "Agradezco" in response or "agradezco" in response:
            score += 1
            notes.append("Good: Expresses gratitude (Spanish cultural value)")

    elif language == "de" and domain in ["business", "technical"]:
        # German contexts value structure and directness
        has_structure = any(marker in response for marker in ["Ich möchte", "Ich bitte", "Kurze Frage"])
        if has_structure:
            score += 1
            notes.append("Good: Direct and structured (German cultural preference)")

    score = min(score, 5)  # Cap at 5
    return {"score": score, "notes": notes}


def _evaluate_closing(response: str, language: str, formality: str) -> Dict:
    """Evaluate closing appropriateness."""
    score = 3
    notes = []

    if language == "de":
        if formality == "formal" and "Hochachtungsvoll" in response:
            score = 5
            notes.append("Excellent: Very formal German closing")
        elif "freundlichen Grüßen" in response:
            score = 4
            notes.append("Good: Standard professional closing")
        elif formality == "casual" and "Viele Grüße" in response:
            score = 5
            notes.append("Excellent: Casual closing matches formality")

    elif language == "es":
        if formality == "formal" and ("Cordialmente" in response or "Atentamente" in response):
            score = 5
            notes.append("Excellent: Formal Spanish closing")
        elif "Saludos" in response and formality == "casual":
            score = 5
            notes.append("Excellent: Casual closing matches formality")

    elif language == "en":
        if formality == "formal" and "Sincerely" in response:
            score = 5
            notes.append("Excellent: Formal English closing")

    return {"score": score, "notes": notes}


def _score_to_rating(score: float) -> str:
    """Convert numerical score to rating."""
    if score >= 4.5:
        return "Excellent"
    elif score >= 3.5:
        return "Good"
    elif score >= 2.5:
        return "Adequate"
    elif score >= 1.5:
        return "Poor"
    else:
        return "Inappropriate"


def calculate_all_qualitative_metrics(
    response: str,
    language: str,
    formality: str,
    domain: str
) -> Dict[str, any]:
    """
    Calculate all qualitative metrics for a response.

    Args:
        response: Response text
        language: Language code
        formality: Target formality level
        domain: Prompt domain

    Returns:
        Dictionary with all qualitative metrics
    """
    return {
        "readability": calculate_readability_metrics(response, language),
        "cultural_appropriateness": evaluate_cultural_appropriateness(
            response, language, formality, domain
        )
    }
