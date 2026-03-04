from unittest.mock import patch, MagicMock


def test_main_happy_path(tmp_path):
    fake_scenario = {
        "scenario": "The couple is riding elephants through a jungle.",
        "image_prompt": "A couple riding elephants through a lush jungle at golden hour.",
    }
    fake_output_path = str(tmp_path / "2026-01-01_12-00-00.jpg")

    with patch("main.load_config", return_value={"anthropic_api_key": "a"}), \
         patch("main.get_couple_image_path", return_value="images/couple.jpg"), \
         patch("main.generate_scenario", return_value=fake_scenario) as mock_gen_scenario, \
         patch("main.generate_image", return_value=fake_output_path) as mock_gen_img, \
         patch("main.append_log"):

        from main import run
        run()

    mock_gen_scenario.assert_called_once_with(api_key="a")
    mock_gen_img.assert_called_once_with(
        image_path="images/couple.jpg",
        prompt=fake_scenario["image_prompt"],
        scenario=fake_scenario["scenario"],
    )


def test_get_couple_image_path_finds_jpg(tmp_path):
    img = tmp_path / "couple.jpg"
    img.write_bytes(b"fake")

    from main import get_couple_image_path
    result = get_couple_image_path(images_dir=str(tmp_path))
    assert result == str(img)


def test_get_couple_image_path_raises_if_empty(tmp_path):
    import pytest
    from main import get_couple_image_path
    with pytest.raises(FileNotFoundError, match="No image found"):
        get_couple_image_path(images_dir=str(tmp_path))


def test_run_batch_generates_multiple_images(tmp_path):
    fake_scenario = {
        "scenario": "The couple rides elephants through a jungle.",
        "image_prompt": "A couple riding elephants through a lush jungle.",
    }
    fake_output_path = str(tmp_path / "2026-01-01_12-00-00.jpg")

    with patch("main.load_config", return_value={"anthropic_api_key": "a"}), \
         patch("main.get_couple_image_path", return_value="images/couple.jpg"), \
         patch("main.generate_scenario", return_value=fake_scenario) as mock_scenario, \
         patch("main.generate_image", return_value=fake_output_path) as mock_image, \
         patch("main.append_log"):

        from main import run
        run(count=3)

    assert mock_scenario.call_count == 3
    assert mock_image.call_count == 3


def test_run_batch_stops_on_first_failure(tmp_path):
    import pytest
    fake_scenario = {
        "scenario": "The couple rides elephants.",
        "image_prompt": "A couple riding elephants.",
    }

    with patch("main.load_config", return_value={"anthropic_api_key": "a"}), \
         patch("main.get_couple_image_path", return_value="images/couple.jpg"), \
         patch("main.generate_scenario", return_value=fake_scenario), \
         patch("main.generate_image", side_effect=Exception("API error")), \
         patch("main.append_log"):

        from main import run
        with pytest.raises(SystemExit):
            run(count=3)
