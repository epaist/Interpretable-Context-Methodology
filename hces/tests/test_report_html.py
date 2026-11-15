from hces.report_html import md_to_html


def test_tables_headings_and_fail_marks():
    h = md_to_html("# Title\n\nText\n\n| A | B |\n|---|---|\n| 1 | FAIL 80% |\n", 1)
    assert "<h2>Title</h2>" in h and "<th>A</th>" in h and 'class="fail"' in h and "<td>1</td>" in h
