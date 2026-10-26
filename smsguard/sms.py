"""SMS segment counting and safe typography clean-up for text written by an LLM agent.

GSM 03.38 (3GPP TS 23.038) basic alphabet: 1 septet each; extension table (^ { } \\ [ ~ ] | and the euro sign): 2 septets.
One segment holds 160 septets, or 153 each when the message is split (concatenation header). If any character is outside
GSM-7 the whole message goes out as UCS-2: 70 units in one segment, 67 each when split; characters beyond the BMP
(most emoji) take 2 units.
"""
import unicodedata

GSM_BASIC = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
GSM_EXT = set("^{}\\[~]|€\f")

# typography an LLM likes, with a harmless GSM-7 equivalent
SAFE = {"‘": "'", "’": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"', "–": "-", "—": "-",
        "−": "-", "…": "...", " ": " ", " ": " ", " ": " ", " ": " ", "•": "-", "·": "-", "→": "->"}


def septets(text):
    n = 0
    for ch in text:
        if ch in GSM_BASIC:
            n += 1
        elif ch in GSM_EXT:
            n += 2
        else:
            return None
    return n


def ucs2_units(text):
    return sum(2 if ord(ch) > 0xFFFF else 1 for ch in text)


def count(text):
    """-> {"encoding", "units", "segments"} for the text exactly as given."""
    s = septets(text)
    if s is not None:
        return {"encoding": "GSM-7", "units": s, "segments": 1 if s <= 160 else -(-s // 153)}
    u = ucs2_units(text)
    return {"encoding": "UCS-2", "units": u, "segments": 1 if u <= 70 else -(-u // 67)}


def naive_segments(text):
    """What people often assume: characters / 160."""
    return max(1, -(-len(text) // 160))


def offenders(text):
    """Characters that force UCS-2."""
    return sorted({ch for ch in text if ch not in GSM_BASIC and ch not in GSM_EXT})


def clean(text, extended=False):
    """Replace typography with GSM-7 equivalents. With extended=True also NFKC-fold compatibility characters and drop
    invisible format characters (zero-width space, joiners, variation selectors), which otherwise force UCS-2.
    Never touches emoji or letters outside GSM-7: those are reported, not silently changed."""
    out = []
    for ch in text:
        if ch in SAFE:
            out.append(SAFE[ch])
            continue
        if extended:
            if unicodedata.category(ch) == "Cf" or 0xFE00 <= ord(ch) <= 0xFE0F:
                continue
            f = unicodedata.normalize("NFKC", ch)
            if f != ch and all(c in GSM_BASIC or c in GSM_EXT for c in f):
                out.append(f)
                continue
        out.append(ch)
    return "".join(out)


def report(text, extended=False):
    before, fixed = count(text), clean(text, extended)
    after = count(fixed)
    return {"before": before, "after": after, "text": fixed, "still_forces_ucs2": offenders(fixed)}
