from services.competency_engine import calculate_gap

def test_calculate_gap_minor():
    result = calculate_gap(70, 80)
    assert result["gap"] == 10
    assert result["status"] == "Minor Gap"

def test_calculate_gap_critical():
    result = calculate_gap(50, 90)
    assert result["gap"] == 40
    assert result["status"] == "Critical"

def test_calculate_gap_competent():
    result = calculate_gap(90, 80)
    assert result["gap"] == 0
    assert result["status"] == "Competent"
