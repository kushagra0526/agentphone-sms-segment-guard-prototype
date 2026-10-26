from smsguard import sms


def test_gsm7_single_and_split_boundaries():
    assert sms.count("a" * 160) == {"encoding": "GSM-7", "units": 160, "segments": 1}
    assert sms.count("a" * 161)["segments"] == 2 and sms.count("a" * 306)["segments"] == 2 and sms.count("a" * 307)["segments"] == 3


def test_extension_characters_cost_two_septets():
    assert sms.count("{}")["units"] == 4 and sms.count("a" * 159 + "|")["segments"] == 2   # 161 septets


def test_one_smart_quote_forces_ucs2_and_inflates_cost():
    t = "It’s " + "a" * 100
    assert sms.count(t)["encoding"] == "UCS-2" and sms.count(t)["segments"] == 2
    assert sms.count(sms.clean(t))["encoding"] == "GSM-7" and sms.count(sms.clean(t))["segments"] == 1


def test_emoji_takes_two_ucs2_units_and_is_not_silently_removed():
    t = "ok \U0001F60A"
    assert sms.count(t) == {"encoding": "UCS-2", "units": 5, "segments": 1}
    assert "\U0001F60A" in sms.clean(t, extended=True) and sms.offenders(sms.clean(t, extended=True)) == ["\U0001F60A"]


def test_invisible_characters_need_the_extended_rules():
    t = "hello​ world"
    assert sms.count(sms.clean(t))["encoding"] == "UCS-2" and sms.count(sms.clean(t, extended=True))["encoding"] == "GSM-7"
