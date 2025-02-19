import os


def test_output_folder_is_created():
    output_folder = "output"
    assert os.path.exists(output_folder)