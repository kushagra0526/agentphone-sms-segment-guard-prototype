"""Synthetic agent replies the way LLMs write them: smart quotes, dashes, ellipses, now and then an emoji or an accent."""
import random

NAMES = ["Sam", "Priya", "José", "Zoë", "Marcus", "Nguyen", "Åsa", "Müller", "Chen"]
OPEN = ["Hi {n}, thanks for reaching out", "Hey {n} — quick update on your order", "Hello {n}, I’m the assistant for Bright Dental", "Thanks {n}! Here’s what I found"]
MID = ["your appointment is confirmed for Thursday at 3:30pm", "we’re open 9–5 on weekdays", "I couldn’t find that booking… could you share the email you used?",
       "the total is $42.50 (tax included)", "you can reschedule any time at https://example.com/r/8XK2", "reply STOP to opt out",
       "your code is 482913 and expires in 10 minutes", "we’ve sent a confirmation to your email", "the technician will arrive between 1–3pm"]
END = ["Let me know if that works.", "Anything else I can help with?", "See you soon!", "Thanks again for your patience."]
EMOJI = ["\U0001F60A", "✅", "\U0001F44D", "\U0001F4C5"]
HELD_ONLY = ["​", " ", "‑", "️", "，", "­", "⁠"]   # zero-width space, narrow nbsp, non-breaking hyphen, VS16, fullwidth comma, soft hyphen, word joiner


def make_message(seed, held_out=False):
    rng = random.Random(seed)
    parts = [rng.choice(OPEN).format(n=rng.choice(NAMES)), rng.choice(MID), rng.choice(MID) if rng.random() < 0.5 else "", rng.choice(END)]
    text = ". ".join(p for p in parts if p)
    if rng.random() < 0.2:
        text += " " + rng.choice(EMOJI)
    if held_out and rng.random() < 0.5:
        i = rng.randrange(len(text))
        text = text[:i] + rng.choice(HELD_ONLY) + text[i:]
    if rng.random() < 0.15:
        text += "\n\n" + " ".join(rng.choice(MID) for _ in range(3))
    return text
