import json
from collections import Counter

from . import gen, sms


def score(seeds, held, extended):
    t = Counter()
    for s in seeds:
        m = gen.make_message(s, held)
        r = sms.report(m, extended)
        b, a = r["before"], r["after"]
        t["messages"] += 1
        t["naive_len_estimate_segments"] += sms.naive_segments(m)
        t["actual_segments_as_written"] += b["segments"]
        t["segments_after_clean"] += a["segments"]
        t["ucs2_as_written"] += b["encoding"] == "UCS-2"
        t["ucs2_after_clean"] += a["encoding"] == "UCS-2"
        t["naive_underestimates"] += sms.naive_segments(m) < b["segments"]
        t["forced_ucs2_by_typography_only"] += b["encoding"] == "UCS-2" and a["encoding"] == "GSM-7"
        t["still_ucs2_unseen_chars"] += a["encoding"] == "UCS-2" and any(c in "".join(gen.HELD_ONLY) for c in r["still_forces_ucs2"])
    return dict(t)


def main():
    res = {"dev": score(range(0, 3000), False, False), "held_out_run1": score(range(10000, 13000), True, False),
           "held_out_run2_extended_rules": score(range(10000, 13000), True, True),
           "held_out_run3_after_hyphen_fix": score(range(10000, 13000), True, "v3")}
    json.dump(res, open("out/result.json", "w"), indent=1)
    for k, v in res.items():
        print(k, v)


if __name__ == "__main__":
    main()
