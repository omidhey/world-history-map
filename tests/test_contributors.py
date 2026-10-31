"""Contributor list: counting, ordering and bot filtering (pipeline/make_contributors.py)."""

import make_contributors


def test_counts_and_orders_by_commits_then_name():
    out = "Bea\nAl\nBea\nCy\nAl\nBea\n"
    assert make_contributors.parse_names(out) == [
        {"name": "Bea", "commits": 3},
        {"name": "Al", "commits": 2},
        {"name": "Cy", "commits": 1},
    ]


def test_bots_and_blank_lines_are_dropped():
    out = "dependabot[bot]\n\nAl\ngithub-actions\n"
    assert make_contributors.parse_names(out) == [{"name": "Al", "commits": 1}]
