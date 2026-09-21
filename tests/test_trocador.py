from algorithms.trocador.solver import solve, greedy_change, optimal_change


def test_zero_amount():
    result = solve(0, [100, 50, 10, 5, 1])
    assert result["greedy"]["total_coins"] == 0
    assert result["greedy"]["exact"] is True


def test_canonical_system_is_optimal():
    result = solve(287, [100, 50, 20, 10, 5, 2, 1])
    assert result["is_greedy_optimal"] is True
    assert result["greedy"]["exact"] is True


def test_non_canonical_system_1_3_4_is_not_optimal():
    result = solve(6, [1, 3, 4])
    assert result["greedy"]["total_coins"] == 3
    assert result["optimal"]["total_coins"] == 2
    assert result["is_greedy_optimal"] is False


def test_non_canonical_system_1_10_25_is_not_optimal():
    result = solve(30, [1, 10, 25])
    assert result["greedy"]["total_coins"] == 6
    assert result["optimal"]["total_coins"] == 3
    assert result["is_greedy_optimal"] is False


def test_greedy_change_with_single_denomination():
    used, remainder, _ = greedy_change(15, [5])
    assert remainder == 0
    assert used == [{"denomination": 5, "quantity": 3}]


def test_greedy_change_cannot_form_exact_value():
    used, remainder, _ = greedy_change(7, [5, 2])
    assert remainder == 0


def test_optimal_change_returns_none_when_impossible():
    result = optimal_change(3, [2])
    assert result is None
