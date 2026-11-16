from hces.sections import build, split_sections


def test_headings_in_code_fences_do_not_split():
    text = "# Title\nintro\n## A\nbody a\n```\n# not a heading\n```\n## B\nbody b\n"
    secs = split_sections(text)
    assert [t for t, _ in secs] == [["Title"], ["Title", "A"], ["Title", "B"]]
    assert "# not a heading" in secs[1][1]


def test_preamble_joins_first_section_and_trail_resets_by_level():
    secs = split_sections("lead line\n# T\n## A\n### a1\nx\n## B\ny\n")
    assert secs[0][0] == ["T"] and "lead line" in secs[0][1]
    assert [t for t, _ in secs][2:] == [["T", "A", "a1"], ["T", "B"]]


def test_long_section_splits_at_blank_lines(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# T\n\n" + "\n\n".join(["word " * 300] * 3), encoding="utf-8")
    units = build(lambda s: len(s.split()), tmp_path)
    assert len(units) >= 2 and all(u["tokens"] <= 502 for u in units)
    assert all(u["text"].startswith("File: CLAUDE.md\nSection: T") for u in units)


def test_block_without_blank_lines_splits_at_line_breaks(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# T\n\n" + "\n".join(["| a | " + "w " * 40 + "|"] * 30), encoding="utf-8")
    units = build(lambda s: len(s.split()), tmp_path)
    assert len(units) >= 3 and all(u["tokens"] <= 502 for u in units)
