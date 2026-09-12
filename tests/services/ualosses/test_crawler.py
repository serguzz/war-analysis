import pytest

from src.services.ualosses.crawler import next_prefix


@pytest.mark.parametrize(
    ("prefix", "expected"),
    [
        # Empty.
        ("", ""),

        # Symbols.
        ("'", "-"),
        ("-", "a"),

        # Single letters.
        ("a", "b"),
        ("b", "c"),
        ("y", "z"),
        ("z", ""),

        # Multiple letters.
        ("aa", "ab"),
        ("ab", "ac"),
        ("ay", "az"),
        ("az", "b"),
        ("za", "zb"),
        ("zy", "zz"),
        ("zz", ""),
    ],
)
def test_next_prefix(
    prefix: str,
    expected: str,
):
    assert next_prefix(prefix) == expected