import pytest

from algorithms.huffman.solver import solve


def test_empty_text_raises_error():
    with pytest.raises(ValueError):
        solve("")


def test_single_character_repeated():
    result = solve("aaaa")
    assert result["decoded_text"] == "aaaa"
    assert result["decoding_matches_original"] is True
    assert len(result["codes"]) == 1


def test_two_distinct_characters():
    result = solve("ab")
    assert result["decoding_matches_original"] is True
    codes = {item["char"]: item["code"] for item in result["codes"]}
    assert len(codes["a"]) == 1
    assert len(codes["b"]) == 1


def test_codes_are_prefix_free():
    result = solve("abracadabra")
    codes = [item["code"] for item in result["codes"]]
    for i in range(len(codes)):
        for j in range(len(codes)):
            if i == j:
                continue
            assert not codes[j].startswith(codes[i])


def test_encoding_and_decoding_round_trip():
    text = "este e um teste de compressao de huffman com varios caracteres repetidos"
    result = solve(text)
    assert result["decoded_text"] == text
    assert result["decoding_matches_original"] is True


def test_more_frequent_characters_get_shorter_or_equal_codes():
    result = solve("aaaaaaaaaabbbbbbccccdd")
    codes_by_char = {item["char"]: item["code"] for item in result["codes"]}
    assert len(codes_by_char["a"]) <= len(codes_by_char["d"])


def test_large_text_round_trip():
    text = "lorem ipsum dolor sit amet consectetur adipiscing elit " * 200
    result = solve(text)
    assert result["decoding_matches_original"] is True
    assert result["compression_ratio"] > 0
