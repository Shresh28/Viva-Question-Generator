import json
import pytest

from src.output_parser import OutputValidationError, parse_response


def valid_data():
    return {"project_info": {"title": "Plant Leaf Classifier", "domain": "Machine Learning",
            "objective": "Classify leaf diseases", "technologies": ["Python"]},
            "questions": [{"difficulty": level, "question": f"{level} question {i}?", "answer": "The report says this."}
                          for level in ("Easy", "Medium", "Hard") for i in range(5)]}


def test_valid_json_and_counts():
    result = parse_response(json.dumps(valid_data()))
    assert len(result["questions"]) == 15
    assert [sum(q["difficulty"] == d for q in result["questions"]) for d in ("Easy", "Medium", "Hard")] == [5, 5, 5]


def test_markdown_fence_accepted():
    assert len(parse_response("```json\n" + json.dumps(valid_data()) + "\n```" )["questions"]) == 15


def test_invalid_json_rejected():
    with pytest.raises(OutputValidationError, match="invalid JSON"):
        parse_response("{nope")


def test_missing_project_field_rejected():
    data = valid_data()
    del data["project_info"]["title"]
    with pytest.raises(OutputValidationError, match="title"):
        parse_response(json.dumps(data))


def test_incorrect_question_count_rejected():
    data = valid_data()
    data["questions"].pop()
    with pytest.raises(OutputValidationError, match="exactly 15"):
        parse_response(json.dumps(data))


def test_wrong_difficulty_count_rejected():
    data = valid_data()
    data["questions"][0]["difficulty"] = "Medium"
    with pytest.raises(OutputValidationError, match="counts"):
        parse_response(json.dumps(data))


def test_duplicate_question_rejected():
    data = valid_data()
    data["questions"][1]["question"] = data["questions"][0]["question"]
    with pytest.raises(OutputValidationError, match="duplicate"):
        parse_response(json.dumps(data))


def test_technology_string_is_normalized_to_list():
    data = valid_data()
    data["project_info"]["technologies"] = "Python, SQLite"
    result = parse_response(json.dumps(data))
    assert result["project_info"]["technologies"] == ["Python", "SQLite"]


def test_grouped_question_schema_is_flattened_for_display():
    data = valid_data()
    grouped = {level: [] for level in ("Easy", "Medium", "Hard")}
    for item in data["questions"]:
        grouped[item["difficulty"]].append({"question": item["question"], "answer": item["answer"]})
    data["questions"] = grouped
    result = parse_response(json.dumps(data))
    assert len(result["questions"]) == 15
    assert [sum(q["difficulty"] == level for q in result["questions"])
            for level in ("Easy", "Medium", "Hard")] == [5, 5, 5]

