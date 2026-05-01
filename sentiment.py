import re
import json


def _clean(text):
    """Strip HTML tags and collapse whitespace."""
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', text)).strip()


def _dominant(counts):
    """Return the sentiment label with the highest count (ignores 'total')."""
    return max(("positive", "negative", "neutral"), key=lambda k: counts[k])



def analyze_with_groq(comments, video_title, api_key):
    """
    Classify comments using Groq's gemma2-9b-it in a single batched prompt.

    Understands sarcasm, Hinglish, emojis, and informal slang — far more
    accurate than TextBlob for an India-focused YouTube audience.
    Returns (results_dict, error_str). On failure, results_dict is None.
    """
    try:
        from groq import Groq
    except ImportError:
        return None, "groq is not installed. Add 'groq' to requirements.txt."

    client = Groq(api_key=api_key)

    # Build indexed comment list, cap at 100, skip empty
    indexed = []
    for i, c in enumerate(comments[:100]):
        text = _clean(c["text"] if isinstance(c, dict) else c)
        if text:
            indexed.append((i, text))

    if not indexed:
        return None, "No processable comment text found."

    formatted = "\n".join(f"{idx}: {txt}" for idx, txt in indexed)

    prompt = f"""You are a YouTube comment sentiment analyzer for an India-focused analytics platform.

Analyze these comments from the video: "{video_title}"

Comments (format "index: comment text"):
{formatted}

Rules:
- Detect sarcasm accurately (e.g. "wow great video 🙄" = negative)
- Understand Hinglish/Hindi romanized (e.g. "ekdum mast bhai" = positive, "bakwas video" = negative)
- Read emoji context (🔥 = positive, 😤 = negative, 💀 = usually positive slang meaning "too funny")
- Do NOT label everything neutral — be precise

Return ONLY a valid JSON object, no markdown fences, no explanation outside JSON:
{{
  "positive": [list of integer indices],
  "negative": [list of integer indices],
  "neutral": [list of integer indices],
  "overall_sentiment": "positive" | "negative" | "neutral" | "mixed",
  "summary": "2-3 sentences on what the audience is saying and feeling about this video",
  "key_themes": ["up to 4 short theme labels"]
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences the model sometimes adds
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw).strip()

        data = json.loads(raw)

        def _build(indices):
            out = []
            for i in indices:
                if isinstance(i, int) and i < len(comments):
                    c = comments[i]
                    out.append({
                        "index": i,
                        "text": c["text"] if isinstance(c, dict) else c,
                        "score": 0.0,
                    })
            return out

        positive = _build(data.get("positive", []))
        negative = _build(data.get("negative", []))
        neutral  = _build(data.get("neutral",  []))

        total_analyzed = len(positive) + len(negative) + len(neutral)
        
        counts = {
            "positive": len(positive),
            "negative": len(negative),
            "neutral":  len(neutral),
            "total":    total_analyzed if total_analyzed > 0 else 1,
            "fetched":  len(comments),
        }

        return {
            "positive": positive,
            "negative": negative,
            "neutral":  neutral,
            "counts":   counts,
            "overall_sentiment": data.get("overall_sentiment", _dominant(counts)),
            "summary":    data.get("summary", ""),
            "key_themes": data.get("key_themes", []),
        }, None

    except json.JSONDecodeError as e:
        return None, f"Groq returned invalid JSON: {e}\nRaw response (first 400 chars): {raw[:400]}"
    except Exception as e:
        return None, f"Groq API error: {e}"
