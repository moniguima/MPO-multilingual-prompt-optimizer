"""
Quantitative metrics for prompt evaluation.

Provides numerical measurements of prompt responses including
token efficiency, length statistics, and basic NLP metrics.
"""

from typing import Dict, List
import re
from collections import Counter


def calculate_token_efficiency(response: str, tokens_output: int) -> Dict[str, float]:
    """
    Calculate token efficiency metrics.

    Args:
        response: Response text
        tokens_output: Number of output tokens

    Returns:
        Dictionary with efficiency metrics
    """
    # Count sentences (approximate)
    sentences = [s.strip() for s in re.split(r'[.!?]+', response) if s.strip()]
    num_sentences = len(sentences)

    # Count words
    words = response.split()
    num_words = len(words)

    # Calculate metrics
    metrics = {
        "tokens_per_sentence": tokens_output / max(num_sentences, 1),
        "tokens_per_word": tokens_output / max(num_words, 1),
        "words_per_sentence": num_words / max(num_sentences, 1),
        "total_tokens": tokens_output,
        "total_words": num_words,
        "total_sentences": num_sentences
    }

    return metrics


def calculate_length_metrics(response: str) -> Dict[str, int]:
    """
    Calculate length-based metrics.

    Args:
        response: Response text

    Returns:
        Dictionary with length metrics
    """
    metrics = {
        "char_count": len(response),
        "char_count_no_spaces": len(response.replace(" ", "")),
        "word_count": len(response.split()),
        "line_count": len(response.split('\n')),
        "paragraph_count": len([p for p in response.split('\n\n') if p.strip()])
    }

    return metrics


def calculate_lexical_diversity(response: str) -> Dict[str, float]:
    """
    Calculate lexical diversity metrics.

    Args:
        response: Response text

    Returns:
        Dictionary with diversity metrics
    """
    # Tokenize (simple word-based)
    words = re.findall(r'\b\w+\b', response.lower())

    if not words:
        return {
            "type_token_ratio": 0.0,
            "unique_words": 0,
            "total_words": 0
        }

    # Count unique words
    unique_words = len(set(words))
    total_words = len(words)

    # Type-Token Ratio (TTR)
    ttr = unique_words / total_words if total_words > 0 else 0.0

    # Most common words
    word_freq = Counter(words)
    most_common = word_freq.most_common(10)

    metrics = {
        "type_token_ratio": round(ttr, 3),
        "unique_words": unique_words,
        "total_words": total_words,
        "most_common_words": dict(most_common)
    }

    return metrics


def detect_formality_markers(response: str, language: str) -> Dict[str, any]:
    """
    Detect formality markers in response.

    Args:
        response: Response text
        language: Language code

    Returns:
        Dictionary with formality indicators
    """
    markers = {
        "language": language,
        "detected_markers": []
    }

    if language == "de":
        # German formality markers
        if re.search(r'\bSie\b', response):
            markers["detected_markers"].append("formal_pronoun_Sie")
        if re.search(r'\bdu\b', response, re.IGNORECASE):
            markers["detected_markers"].append("casual_pronoun_du")
        if "Sehr geehrte" in response:
            markers["detected_markers"].append("very_formal_greeting")
        if "Guten Tag" in response:
            markers["detected_markers"].append("neutral_greeting")
        if "Hallo" in response:
            markers["detected_markers"].append("casual_greeting")

    elif language == "es":
        # Spanish formality markers
        if re.search(r'\busted\b', response, re.IGNORECASE):
            markers["detected_markers"].append("formal_pronoun_usted")
        if re.search(r'\btú\b', response, re.IGNORECASE):
            markers["detected_markers"].append("casual_pronoun_tu")
        if "Estimado" in response or "Estimada" in response:
            markers["detected_markers"].append("formal_greeting")
        if "Buenos días" in response or "Buenas tardes" in response:
            markers["detected_markers"].append("neutral_greeting")
        if "Hola" in response:
            markers["detected_markers"].append("casual_greeting")

    elif language == "en":
        # English formality markers
        if "Dear Sir/Madam" in response or "Dear Madam/Sir" in response:
            markers["detected_markers"].append("very_formal_greeting")
        if response.startswith("Please "):
            markers["detected_markers"].append("polite_request")
        if "Sincerely" in response or "Respectfully" in response:
            markers["detected_markers"].append("formal_closing")

    markers["formality_score"] = len(markers["detected_markers"])
    markers["has_formality_markers"] = len(markers["detected_markers"]) > 0

    return markers


def calculate_sentiment_basic(response: str) -> Dict[str, any]:
    """
    Calculate basic sentiment indicators.

    Note: This is a simple rule-based implementation.
    For production, consider using proper sentiment analysis libraries.

    Args:
        response: Response text

    Returns:
        Dictionary with sentiment metrics
    """
    response_lower = response.lower()

    # Simple positive/negative word lists
    positive_words = {
        'good', 'great', 'excellent', 'wonderful', 'fantastic', 'amazing',
        'helpful', 'beneficial', 'valuable', 'effective', 'successful',
        'bien', 'excelente', 'maravilloso', 'fantástico', 'útil',  # Spanish
        'gut', 'großartig', 'wunderbar', 'hilfreich', 'effektiv'  # German
    }

    negative_words = {
        'bad', 'poor', 'terrible', 'awful', 'horrible', 'difficult',
        'problem', 'issue', 'error', 'fail', 'unfortunately',
        'malo', 'terrible', 'problema', 'error', 'desafortunadamente',  # Spanish
        'schlecht', 'furchtbar', 'Problem', 'Fehler', 'schwierig'  # German
    }

    # Count occurrences
    pos_count = sum(1 for word in positive_words if word in response_lower)
    neg_count = sum(1 for word in negative_words if word in response_lower)

    # Calculate polarity
    total = pos_count + neg_count
    if total > 0:
        polarity = (pos_count - neg_count) / total
    else:
        polarity = 0.0

    return {
        "positive_words_count": pos_count,
        "negative_words_count": neg_count,
        "polarity": round(polarity, 3),
        "sentiment_label": "positive" if polarity > 0.2 else "negative" if polarity < -0.2 else "neutral"
    }


def analyze_structural_features(response: str) -> Dict[str, any]:
    """
    Analyze structural features of the response.

    Args:
        response: Response text

    Returns:
        Dictionary with structural metrics
    """
    # Check for common structural elements
    has_greeting = bool(re.search(r'^(Hello|Hi|Dear|Hola|Guten Tag|Buenos días)', response))
    has_closing = bool(re.search(r'(Sincerely|Best|Regards|Saludos|Grüße|Cordialmente)', response, re.IGNORECASE))

    # Count questions
    question_marks = response.count('?')
    question_marks_es = response.count('¿')  # Spanish opening question mark

    # Count exclamations
    exclamations = response.count('!')
    exclamations_es = response.count('¡')  # Spanish opening exclamation

    # Detect lists or bullet points
    has_bullets = bool(re.search(r'[\n\r]\s*[-•*]\s+', response))
    has_numbers = bool(re.search(r'[\n\r]\s*\d+[\.)]\s+', response))

    return {
        "has_greeting": has_greeting,
        "has_closing": has_closing,
        "question_marks": question_marks + question_marks_es,
        "exclamation_marks": exclamations + exclamations_es,
        "has_bullet_points": has_bullets,
        "has_numbered_list": has_numbers,
        "structure_type": "structured" if (has_greeting and has_closing) else "informal"
    }


def calculate_all_quantitative_metrics(
    response: str,
    tokens_output: int,
    language: str
) -> Dict[str, any]:
    """
    Calculate all quantitative metrics for a response.

    Args:
        response: Response text
        tokens_output: Number of output tokens
        language: Language code

    Returns:
        Dictionary with all quantitative metrics
    """
    return {
        "token_efficiency": calculate_token_efficiency(response, tokens_output),
        "length_metrics": calculate_length_metrics(response),
        "lexical_diversity": calculate_lexical_diversity(response),
        "formality_markers": detect_formality_markers(response, language),
        "sentiment": calculate_sentiment_basic(response),
        "structural_features": analyze_structural_features(response)
    }
