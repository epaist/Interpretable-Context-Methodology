from hces import pilot as P


def test_code_checks_flag_dashes_caps_and_bad_placeholders():
    long_ctx = "\n".join(["x"] * 81)
    text = (f'<file path="stages/01-a/CONTEXT.md">\n{long_ctx}\n</file>\n'
            '<file path="shared/voice.md">\nHi {{BRAND_NAME}} {{?OPTIONAL}} {{/OPTIONAL}} {{brandName}} \u2014 ok scan for `{{` patterns and `}}`\n</file>')
    c = P.code_checks(text)
    assert c["files"] == 2 and c["dashes"] == 1
    assert c["over_cap"] == ["stages/01-a/CONTEXT.md"]
    assert c["bad_placeholders"] == ["brandName"]


def test_section_reads_one_heading_block():
    text = "# T\n\n## Audit\n\n| Check | Pass Condition |\n|--|--|\n| A | b |\n\n## Outputs\n\nx\n"
    assert P.section(text, "Audit").splitlines()[-1] == "| A | b |"
    assert P.section(text, "Missing") == ""
