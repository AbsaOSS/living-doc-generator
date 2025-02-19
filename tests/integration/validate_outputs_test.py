import os

def count_files_in_directory(directory):
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

output_folder = "output"
directory_path = f"{output_folder}/liv-doc-regime"

def test_validate_for_test1():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 4

def test_validate_for_test2():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 2

def test_validate_for_test3():
    assert os.path.exists(output_folder)
    assert count_files_in_directory(directory_path) == 2