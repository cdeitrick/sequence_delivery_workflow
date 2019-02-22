import csv
import itertools
from pathlib import Path
from typing import List, NamedTuple, Tuple
import re

from dataclasses import dataclass

import checksums
import samplesheet

TableType = samplesheet.TableType


class ChecksumColumns(NamedTuple):
	project: str = "projectName"
	filename: str = 'fileName'
	sample_name: str = 'sampleName'
	md5sum: str = 'md5sum'
	sha1: str = 'sha1'
	size: str = 'fileSize'


COLUMNS = ChecksumColumns()


@dataclass
class Sample:
	name: str
	folder: Path
	forward: Path
	reverse: Path
	index1: Path
	index2: Path

	@classmethod
	def from_folder(cls, folder: Path) -> "Sample":
		f, r, i1, i2 = get_sample_files(folder)

		return Sample(
			folder.name, folder,
			f, r, i1, i2
		)

	def __iter__(self):
		return self.files().__iter__()

	def files(self):
		return self.forward, self.reverse, self.index1, self.index2


def save_table(table: TableType, filename: Path):
	if not table: return None  # Make sure it is not an empty list.
	columns = table[0].keys()
	with filename.open('w') as output_file:
		writer = csv.DictWriter(output_file, fieldnames = columns, extrasaction = 'ignore', delimiter = '\t')
		writer.writeheader()
		writer.writerows(table)

def read_csv(filename:Path)->TableType:
	sep = '\t' if filename.suffix == '.tsv' else ','
	with filename.open() as csv_file:
		reader = csv.DictReader(csv_file, delimiter = sep)
		return list(reader)

def get_sample_files(folder: Path):
	""" Extracts the forward, reverse, and index files from a sample folder.

		Parameters
		----------
		folder: Path
			The sample folder to parse after demultiplexing. Should contain exactly four files
	"""
	files = list(folder.iterdir())
	forward = [i for i in files if 'R1' in i.stem][0]
	reverse = [i for i in files if 'R2' in i.stem][0]
	index1 = [i for i in files if 'I1' in i.stem][0]
	index2 = [i for i in files if 'I2' in i.stem][0]

	return forward, reverse, index1, index2


def get_project_samples(project_folder: Path) -> List[Sample]:
	sample_folders = list(i for i in project_folder.iterdir() if i.is_dir())
	return [Sample.from_folder(i) for i in sample_folders]


def rename_project_sample_folders(project_folder: Path, sample_sheet: TableType):
	project_name = project_folder.name
	project_sheet = list(filter(lambda s: s[samplesheet.COLUMNS.project] == project_name, sample_sheet))
	for row in project_sheet:
		sample_id = row[samplesheet.COLUMNS.sample_id]
		sample_name = row[samplesheet.COLUMNS.sample_name]
		source = project_folder / sample_id
		destination = project_folder / sample_name
		if not destination.exists():
			source.rename(destination)


def rename_sample_folders(dmux_folder: Path, sample_sheet: samplesheet.TableType):
	""" Renames sample folders after demuxing."""
	for row in sample_sheet:
		project_name = row[samplesheet.COLUMNS.project]
		sample_id = row[samplesheet.COLUMNS.sample_id]
		sample_name = row[samplesheet.COLUMNS.sample_name]

		source = dmux_folder / project_name / sample_id
		destination = dmux_folder / project_name / sample_name

		source.rename(destination)


def get_container_name(container_id: str, from_samplesheet: bool = True) -> str:
	if from_samplesheet:
		year = container_id[-2:]
		day = container_id[-4:-2]
		month = container_id[:-4]
	else:
		year = container_id[:2]
		month = container_id[2:4]
		day = container_id[4:]
	return f"20{year}-{month:>02}-{day:>02}"


def get_container_id(input_folder: Path, filename: Path) -> Tuple[str, str]:
	match = re.search("^[\d]+_", str(input_folder.name))
	if match:
		container_id = match.group(0)[:-1]  # remove trailing underscore
		container_name = get_container_name(container_id, False)
	else:
		container_id = samplesheet.get_container_id(filename)
		container_name = get_container_name(container_id, True)
	return container_id, container_name


def generate_project_checksums(project_folder: Path) -> Path:
	""" Generates and saves a list of all sample files and their file hashes."""
	project_file_list_path = project_folder / "checksums.tsv"
	project_name = project_folder.name
	project_table = list()
	project_samples = get_project_samples(project_folder)
	project_files = itertools.chain.from_iterable(project_samples)

	for filename in project_files:
		sample_name = filename.parent.name
		md5sum = checksums.generate_file_md5(filename)
		sha1 = checksums.generate_file_sha1(filename)
		path_info = {
			COLUMNS.project: project_name,
			COLUMNS.sample_name: sample_name,
			COLUMNS.filename:    filename.name,
			COLUMNS.size: filename.stat().st_size,
			COLUMNS.md5sum:      md5sum,
			COLUMNS.sha1:        sha1
		}
		project_table.append(path_info)
	save_table(project_table, project_file_list_path)
	return project_file_list_path



if __name__ == "__main__":
	import re

	string = "160526_NB501145_0011_AHMW7MBGXX/"
	match = re.search("^[\d]+_", string)
	print(match)
	print(match.group(0))
