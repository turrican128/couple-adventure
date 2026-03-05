from pathlib import Path
from gallery import parse_log


def test_parse_log_returns_scenario_for_image(tmp_path):
    log = tmp_path / "generation_log.txt"
    log.write_text(
        "============================================================\n"
        "Date & Time  : 2026-03-05 14:00:00\n"
        "Output Image : output/2026-03-05_14-00-00_on-mars.jpg\n"
        "Source Photo : images/couple.jpg\n"
        "\nScenario:\nThe couple kisses on Mars.\n"
        "\nImage Prompt:\nA couple kissing on Mars.\n\n",
        encoding="utf-8",
    )

    result = parse_log(log)
    assert result["2026-03-05_14-00-00_on-mars"] == "The couple kisses on Mars."


def test_parse_log_returns_empty_dict_if_no_log(tmp_path):
    result = parse_log(tmp_path / "missing.txt")
    assert result == {}


def test_parse_log_skips_images_with_no_scenario(tmp_path):
    log = tmp_path / "generation_log.txt"
    log.write_text(
        "============================================================\n"
        "Date & Time  : 2026-03-05 14:00:00\n"
        "Output Image : output/2026-03-05_14-00-00_on-mars.jpg\n"
        "Source Photo : images/couple.jpg\n\n",
        encoding="utf-8",
    )

    result = parse_log(log)
    assert result == {}


def test_parse_log_handles_windows_backslash_paths(tmp_path):
    log = tmp_path / "generation_log.txt"
    log.write_text(
        "============================================================\n"
        "Date & Time  : 2026-03-05 14:00:00\n"
        r"Output Image : output\2026-03-05_14-00-00_on-mars.jpg" + "\n"
        "Source Photo : images/couple.jpg\n"
        "\nScenario:\nThe couple kisses on Mars.\n"
        "\nImage Prompt:\nA couple kissing on Mars.\n\n",
        encoding="utf-8",
    )

    result = parse_log(log)
    assert result["2026-03-05_14-00-00_on-mars"] == "The couple kisses on Mars."
