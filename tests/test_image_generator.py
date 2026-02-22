import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


def test_generate_image_saves_file(tmp_path):
    fake_image_bytes = b"\xff\xd8\xff"  # minimal JPEG header

    # Create a fake input image
    input_image = tmp_path / "couple.jpg"
    input_image.write_bytes(b"fake input image")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = fake_image_bytes

    with patch("image_generator.fal_client") as mock_fal, \
         patch("image_generator.requests.get", return_value=mock_response):

        mock_fal.upload_file.return_value = "https://fal.ai/tmp/couple.jpg"
        mock_fal.subscribe.return_value = {"images": [{"url": "https://example.com/img.jpg"}]}

        from image_generator import generate_image
        output_path = generate_image(
            image_path=str(input_image),
            prompt="A couple skydiving over the Grand Canyon at sunset.",
            output_dir=str(tmp_path / "output"),
        )

    mock_fal.upload_file.assert_called_once_with(str(input_image))
    assert Path(output_path).exists()
    assert Path(output_path).suffix == ".jpg"
    assert Path(output_path).read_bytes() == fake_image_bytes


def test_generate_image_raises_if_input_missing(tmp_path):
    from image_generator import generate_image
    with pytest.raises(FileNotFoundError, match="images/nonexistent.jpg"):
        generate_image(
            image_path="images/nonexistent.jpg",
            prompt="test",
            output_dir=str(tmp_path),
        )
