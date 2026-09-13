from services.assessment_engine import calculate_new_competency

def test_exact_70_to_82():
    # 70 current, 88 required, 60% assessment
    new_level = calculate_new_competency(current_level=70, required_level=88, percentage=60.0)
    assert new_level == 82.0

def test_lower_competency():
    # 50 current, 80 required, 90% assessment
    new_level = calculate_new_competency(current_level=50, required_level=80, percentage=90.0)
    assert new_level == 68.0

def test_competency_near_required():
    # 80 current, 80 required, 75% assessment (Exceeds required slightly with 0.25 diminishing factor)
    # base_gain = 15. gap = 0. gain = 0 + 15 * 0.25 = 3.75 -> 83.75
    new_level = calculate_new_competency(current_level=80, required_level=80, percentage=75.0)
    assert new_level == 83.75

def test_competency_above_required():
    # 95 current, 90 required, 100% assessment
    # base_gain = 20. gap = 0. gain = 20 * 0.25 = 5. new_level = 95 + 5 = 100
    new_level = calculate_new_competency(current_level=95, required_level=90, percentage=100.0)
    assert new_level == 100.0

def test_repeated_assessments():
    # 70 -> 82 (60%)
    level1 = calculate_new_competency(current_level=70, required_level=88, percentage=60.0)
    # 82 -> gap is 6. base gain is 12. gain = 6 + 6*0.25 = 7.5. new = 89.5
    level2 = calculate_new_competency(current_level=level1, required_level=88, percentage=60.0)
    assert level2 == 89.5
    # 89.5 -> gap is 0. base gain is 12. gain = 12 * 0.25 = 3.0. new = 92.5
    level3 = calculate_new_competency(current_level=level2, required_level=88, percentage=60.0)
    assert level3 == 92.5

def test_0_assessment():
    new_level = calculate_new_competency(current_level=70, required_level=88, percentage=0.0)
    assert new_level == 70.0

def test_100_assessment_upper_bound():
    new_level = calculate_new_competency(current_level=98, required_level=90, percentage=100.0)
    assert new_level == 100.0

def test_lower_bound_0():
    new_level = calculate_new_competency(current_level=0, required_level=80, percentage=50.0)
    assert new_level == 10.0

def test_required_0():
    # 50 current, 0 required, 100% assessment
    # base_gain = 20, gap = 0, gain = 20 * 0.25 = 5
    new_level = calculate_new_competency(current_level=50, required_level=0, percentage=100.0)
    assert new_level == 55.0

def test_percentage_out_of_bounds():
    # test < 0
    new_level_neg = calculate_new_competency(current_level=70, required_level=88, percentage=-50.0)
    assert new_level_neg == 70.0  # clamped to 0
    
    # test > 100
    new_level_pos = calculate_new_competency(current_level=70, required_level=88, percentage=150.0)
    # clamped to 100, so base_gain = 20, gap = 18, gain = 18 + (2 * 0.25) = 18.5, new = 88.5
    assert new_level_pos == 88.5

def test_current_equals_required():
    new_level = calculate_new_competency(current_level=80, required_level=80, percentage=50.0)
    # clamped to 50, base_gain=10, gap=0, gain=10*0.25=2.5, new=82.5
    assert new_level == 82.5
