import pytest
from pathlib import Path
import fileio

def test_get_container_id():
	folder = Path("160526_NB501145_0011_AHMW7MBGXX")
	sheet = Path("SampleSheet.csv")
	container_id, container_name = fileio.get_container_id(folder, sheet)

	assert container_id == "160526"
	assert container_name == "2016-05-26"

def test_get_project_samples():
	project = Path("dmux_data/BombergerLab")
	sample_files = fileio.get_project_samples(project)
	assert [i.name for i in sample_files] == ["25", "39"]

def test_get_sample_files():
	expected = (
		Path("dmux_data/BombergerLab/25/25_S30_R1_001.fastq.gz"),
		Path("dmux_data/BombergerLab/25/25_S30_R2_001.fastq.gz"),
		Path("dmux_data/BombergerLab/25/25_S30_I1_001.fastq.gz"),
		Path("dmux_data/BombergerLab/25/25_S30_I2_001.fastq.gz")
	)
	class FakePath():
		def iterdir(self):
			files = (
				Path("dmux_data/BombergerLab/25/25_S30_R2_001.fastq.gz"),
				Path("dmux_data/BombergerLab/25/25_S30_I1_001.fastq.gz"),
				Path("dmux_data/BombergerLab/25/25_S30_I2_001.fastq.gz"),
				Path("dmux_data/BombergerLab/25/25_S30_R1_001.fastq.gz")
			)
			return files
	result = fileio.get_sample_files(FakePath())
	assert expected == result