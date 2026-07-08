"""Filler word counter and analyzer"""
import re
from collections import Counter


FILLER_WORDS = {
    # English fillers
    "um": "um",
    "uh": "uh",
    "er": "er",
    "erm": "erm",
    "like": "like",
    "you know": "you know",
    "i mean": "i mean",
    "sort of": "sort of",
    "kind of": "kind of",
    "basically": "basically",
    "actually": "actually",
    "literally": "literally",
    "uhh": "uh",
    "umm": "um",
    "ah": "ah",
    "so": "so (filler)",
}


def count_filler_words(transcript: str) -> dict:
    """
    Analyze transcript for filler words
    
    Args:
        transcript: Transcribed text
    
    Returns:
        Dict with:
        - total: total filler words found
        - by_word: breakdown by filler type
        - list: formatted list of fillers found
        - percentage: percentage of filler words vs total words
    """
    if not transcript:
        return {"total": 0, "by_word": {}, "list": "", "percentage": 0.0}
    
    # Convert to lowercase for matching
    lower_text = transcript.lower()
    
    # Count total words (rough estimate)
    total_words = len(transcript.split())
    
    # Find all filler words
    found_fillers = []
    filler_counts = Counter()
    
    # Check for multi-word fillers first
    for filler_key, filler_name in sorted(FILLER_WORDS.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(filler_key) + r'\b'
        matches = re.findall(pattern, lower_text, re.IGNORECASE)
        for match in matches:
            found_fillers.append(filler_name)
            filler_counts[filler_name] += 1
    
    total_fillers = len(found_fillers)
    percentage = (total_fillers / total_words * 100) if total_words > 0 else 0
    
    return {
        "total": total_fillers,
        "by_word": dict(filler_counts),
        "list": ", ".join(found_fillers) if found_fillers else "None",
        "percentage": round(percentage, 2),
    }


def get_filler_feedback(analysis: dict) -> str:
    """
    Generate feedback on filler word usage
    
    Args:
        analysis: Result from count_filler_words()
    
    Returns:
        Friendly feedback message in English/Uzbek mix
    """
    total = analysis["total"]
    percentage = analysis["percentage"]
    
    if total == 0:
        return "✅ Excellent! No filler words detected. Your speech is clean and professional."
    
    feedback = f"📊 Filler words found: {total} ({percentage}% of speech)\n\n"
    
    # Breakdown by word type
    if analysis["by_word"]:
        feedback += "Breakdown:\n"
        for word, count in sorted(analysis["by_word"].items(), key=lambda x: x[1], reverse=True):
            feedback += f"  • {word}: {count}x\n"
        feedback += "\n"
    
    # Recommendations based on percentage
    if percentage < 2:
        feedback += "🎯 Great! Very minimal filler usage. Keep it up!"
    elif percentage < 5:
        feedback += "✓ Good. Try to reduce filler words a bit more for a more polished presentation."
    elif percentage < 10:
        feedback += "⚠️ Moderate. Consider pausing instead of using filler words like 'um' or 'like'."
    else:
        feedback += "❌ High filler word usage. Try these tips:\n"
        feedback += "   1. Pause naturally instead of filling silence\n"
        feedback += "   2. Take a breath before continuing\n"
        feedback += "   3. Practice slower, more deliberate speech"
    
    return feedback


def get_filler_tips() -> str:
    """Get general tips for reducing filler words"""
    return """🎤 Tips to reduce filler words:

1. **Pause, don't fill** — Comfortable silence is better than "um" or "uh"
2. **Take a breath** — Use breathing as a natural transition
3. **Slow down** — Speaking slower gives you time to think
4. **Practice pronunciation** — Better articulation reduces hesitation
5. **Record yourself** — Hear your own patterns and catch them
6. **Prepare key points** — Less thinking = fewer fillers
7. **Be mindful** — Once you notice the pattern, you can stop it

Remember: Even native speakers use fillers sometimes. The goal is awareness and improvement! 📈
"""
