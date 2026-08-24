from typing import Any


def generate_creative(segment: dict[str, Any]) -> dict[str, Any]:
    """Return a repeatable LLM-like response tailored to one campaign row."""
    audience = segment["Audience_Segment"]
    platform = segment["Platform"]
    issue = "high acquisition cost" if segment["CPA_USD"] > 50 else "weak click-through"
    objective = segment["Campaign_Type"].lower()
    return {
        "analysis": (
            f"The {platform} creative is reaching {audience}, but the signal shows {issue}. "
            f"The current {objective} message likely asks for too much attention before making the benefit clear. "
            "The agent is tightening the promise, making the audience cue explicit, and adding a lower-friction next step."
        ),
        "variants": [
            {
                "headline": f"Built for {audience}",
                "text": f"Skip the generic pitch. Discover a sharper way to reach your next win, made for {audience}. See what changes when relevance leads.",
            },
            {
                "headline": "Your next move, made clearer",
                "text": f"Less noise. More momentum. Get the practical insight {audience} can act on today, with one simple step to begin.",
            },
            {
                "headline": "Turn attention into action",
                "text": f"A focused solution for {audience}: find the value faster, move with confidence, and take the next step on {platform}.",
            },
        ],
    }
