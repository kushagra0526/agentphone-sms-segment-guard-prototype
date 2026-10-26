# smsguard: what an AI agent's text message really costs in SMS segments

AgentPhone gives an AI agent "its own phone number" for voice and messages through one webhook (https://agentphone.ai/). Anything an LLM writes and sends as SMS hits a billing rule that is easy to miss: if the message contains a single character outside the GSM-7 alphabet (a curly apostrophe, an en dash, an ellipsis character, an emoji), the whole message is sent as UCS-2, where a segment holds 70 characters instead of 160 (67 vs 153 when split). This prototype counts segments exactly, removes the harmless typography, and reports what it cannot fix.

## What it does
`smsguard/sms.py`:
- `count(text)`: encoding (GSM-7 or UCS-2), units and billed segments (GSM-7 extension characters `^ { } \ [ ~ ] | €` cost 2 septets; emoji beyond the BMP cost 2 UCS-2 units).
- `clean(text)`: replaces curly quotes, en/em dashes, the ellipsis character, non-breaking spaces and bullets with GSM-7 equivalents. With `extended=True` it also drops invisible format characters (zero-width space, joiners, variation selectors, soft hyphen) and NFKC-folds compatibility characters. Emoji and letters outside GSM-7 (for example ë) are never changed silently; `report()` lists them.
- Facts used: GSM 03.38 / 3GPP TS 23.038 alphabets and 160/153/70/67 limits. Carriers and aggregators may handle exotic characters differently; check yours.

## Results (3,000 synthetic LLM-style replies per split)
My generator writes agent replies the way LLMs do (smart quotes, dashes, ellipses, an emoji in 20%, a name with an accent now and then); how often real traffic has such characters depends on the model and the prompt, so the percentages below are for my generator.

| | dev | held-out (as written) | held-out after `clean` | held-out after `clean(extended)` | held-out after one more fix |
|---|---|---|---|---|---|
| billed segments (3,000 messages) | 7,938 -> 5,185 | 8,045 | 6,772 | 5,397 | **5,163** |
| messages sent as UCS-2 | 2,790 -> 829 | 2,900 | 1,983 | 1,015 | **849** |
| estimate "length / 160" is too low for | 2,785 of 3,000 | 2,896 | | | |

- A length/160 estimate under-counts nearly every message in this set (the cost is about 2x, because most messages are UCS-2 and 70 characters per segment).
- Cleaning typography cuts billed segments by 35% (dev) and 36% (held-out, after the last fix); what remains as UCS-2 is emoji and non-GSM letters, which are a product decision, not a clean-up.
- Held-out contains seven characters the cleaner had not been built around (zero-width space, narrow no-break space, non-breaking hyphen, variation selector 16, fullwidth comma, soft hyphen, word joiner). The plain `clean` fixed few of them (6,772 segments); the extended rules, which handle format characters and NFKC folding, got to 5,397; and 222 messages were still UCS-2 because NFKC turns U+2011 into U+2010, which is not GSM-7. I added that mapping after the held-out run (last column). The first two held-out runs are kept in `out/first_runs.txt`. Note the extended rules were written with these character classes in mind before the run, so treat run 1 vs run 2 as an ablation, not a discovery.

## Read this before believing the table
The messages are generated; real conversations differ. It does not know carrier rules for 10DLC, opt-outs or length-based throttling, and it changes message text (punctuation only) without asking, which a product may want to confirm. Nothing here uses AgentPhone data, its API or any phone network.

## Run it (3 commands)
```
pip install pytest
python -m pytest -q tests
python -m smsguard.run
```
Standard library only. 5 tests.

Unofficial prototype by Kushagra Pratap Singh. Not affiliated with AgentPhone.
