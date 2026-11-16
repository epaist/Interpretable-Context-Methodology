import os

import pytest

from hces.rubric import Question, Rubric


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: downloads or runs the real embedding model")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("HCES_SKIP_SLOW"):
        skip = pytest.mark.skip(reason="HCES_SKIP_SLOW is set")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip)


@pytest.fixture
def rubric():
    return Rubric(
        rubric_id="toy-q1",
        version=1,
        task="Why does the lighthouse keeper leave the island?",
        questions=(
            Question("relevance", "score", "How directly does this passage help answer the task?",
                     ["Unrelated", "Mentions the topic", "Partly answers", "Directly answers"], weight=2.0),
            Question("specific", "score", "How specific is the passage about the keeper?",
                     ["Not about the keeper", "About the keeper"]),
            Question("has_fact", "noul", "Does this passage state why the keeper leaves?", critical=True),
            Question("speaker", "choice", "Who is speaking?", {"keeper": None, "narrator": None, "other": None}),
        ),
        answerability=Question("enough", "noul", "Is the evidence enough to answer the task?"),
    )
