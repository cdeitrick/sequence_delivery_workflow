from typing import List
from unittest.mock import MagicMock

import pytest

import boxio


@pytest.fixture
def dmux_folder():
	pass


@pytest.fixture
def test_files() -> List[str]:
	files = [
		"T1_S81_R1_001.fastq.gz", "T1_S81_R2_001.fastq.gz", "T1_S81_I1_001.fastq.gz", "T1_S81_I2_001.fastq.gz",
		"T2_S82_R1_001.fastq.gz", "T2_S82_R2_001.fastq.gz", "T2_S82_I1_001.fastq.gz", "T2_S82_I2_001.fastq.gz",
		"T3_S83_R1_001.fastq.gz", "T3_S83_R2_001.fastq.gz", "T3_S83_I1_001.fastq.gz", "T3_S83_I2_001.fastq.gz",
		"L1_S91_R1_001.fastq.gz", "L1_S91_R2_001.fastq.gz", "L1_S91_I1_001.fastq.gz", "L1_S91_I2_001.fastq.gz",
		"L2_S92_R1_001.fastq.gz", "L2_S92_R2_001.fastq.gz", "L2_S92_I1_001.fastq.gz", "L2_S92_I2_001.fastq.gz",
		"L3_S93_R1_001.fastq.gz", "L3_S93_R2_001.fastq.gz", "L3_S93_I1_001.fastq.gz", "L3_S93_I2_001.fastq.gz",
	]
	return files


def test_get_project_name_from_folder():
	fake_folder = MagicMock()
	a, b, c, d = MagicMock(), MagicMock(), MagicMock(), MagicMock()
	a.is_dir.return_value = b.is_dir.return_value = c.is_dir.return_value = d.is_dir.return_value = True
	a.name = 'Gilead'
	b.name = 'Cooperlab'
	c.name = 'Reports'
	d.name = 'Stats'
	fake_folder.iterdir.return_value = [a, b, c, d]

	assert ['Gilead', 'Cooperlab'] == boxio._get_project_names_from_dmux_folder(fake_folder)


def test_get_project_files_on_box(test_files):
	project_name = 'testboxapi'

	result = boxio.get_project_files_on_box(project_name)
	result = {i.name for i in result}

	assert set(test_files) == result

@pytest.mark.parametrize("filename,expected",
[
	("T1_S81_R1_001.fastq.gz", True),
	("L1_S91_R1_001.fastq.gz", True),
	("L1_S91_R2_001.fastq.gz", True),
	("none", False),
	("doesnotexist.txt", False)
]
)
def test_file_exists(filename, expected):
	result = boxio.file_exists("testboxapi", filename)
	assert expected == result




