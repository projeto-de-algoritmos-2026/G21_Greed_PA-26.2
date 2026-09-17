CASES = [
    {
        "id": "sistema-real",
        "title": "Sistema monetario real (canonico)",
        "amount": 287,
        "denominations": [100, 50, 20, 10, 5, 2, 1],
        "expected_optimal": True,
    },
    {
        "id": "contraexemplo-1-3-4",
        "title": "Denominacoes 1, 3, 4 para o valor 6",
        "amount": 6,
        "denominations": [1, 3, 4],
        "expected_optimal": False,
    },
    {
        "id": "contraexemplo-1-10-25",
        "title": "Denominacoes 1, 10, 25 para o valor 30",
        "amount": 30,
        "denominations": [1, 10, 25],
        "expected_optimal": False,
    },
]
