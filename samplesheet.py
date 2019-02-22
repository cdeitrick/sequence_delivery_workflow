import csv
import itertools
from collections import Counter
from pathlib import Path
from pprint import pprint
from typing import Dict, List, NamedTuple

TableType = List[Dict[str, str]]


class SampleSheetColumns(NamedTuple):
	sample_id: str = 'Sample_ID'
	sample_name: str = 'Sample_Name'
	species: str = 'Species'
	project: str = 'Project'
	nucleic_acid: str = 'NucleicAcid'
	sample_well: str = 'Sample_Well'
	i7: str = "I7_Index_ID"
	index: str = 'index'
	i5: str = "I5_Index_ID"
	index2: str = "index2"


COLUMNS = SampleSheetColumns()


def verify_sample_sheet(table: TableType):
	sample_name_counts = Counter([i[COLUMNS.sample_name] for i in table])

	assert all(i < 2 for i in sample_name_counts.values())


def get_container_id(filename: Path) -> str:
	""" Attempts to get the container id from the samplesheet"""
	with filename.open('r') as file1:
		reader = csv.DictReader(file1, fieldnames = list(COLUMNS))
		for line in reader:
			if line[COLUMNS.sample_id] == "ContainerID":
				return line[COLUMNS.sample_name]


def read_sample_sheet(path: Path) -> TableType:
	with path.open('r') as csv_file:
		reader = csv.DictReader(csv_file, fieldnames = list(COLUMNS))

		# Skip the header information.
		# Use list() to make sure the iterator advances.
		list(itertools.takewhile(lambda line: line[COLUMNS.sample_id] != COLUMNS.sample_id, reader))
		sheet: TableType = list(reader)
	verify_sample_sheet(sheet)
	return sheet


if __name__ == "__main__":
	samplesheet_filename = Path(__file__).parent / "tests" / "SampleSheet.csv"
	sheet = read_sample_sheet(samplesheet_filename)
	pprint(sheet)
