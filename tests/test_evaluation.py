def test_evaluates(evaluated_model):
    evaluation_dir, test_model_info = evaluated_model

    try:
        assert evaluation_dir.exists()
        assert len(list(evaluation_dir.rglob("*.json"))) > 0
    except AssertionError as e:
        error_lines = [
            f"Output directory {evaluation_dir} check failed. Walking back...",
        ]
        d = evaluation_dir.parent
        while not d.exists():
            error_lines.append(f"Directory {d} does not exist.")
            d = d.parent
        error_lines.append(f"Directory {d} exists. Contents:")
        error_lines.append(str(list(d.rglob("*"))))
        raise AssertionError("\n".join(error_lines)) from e
