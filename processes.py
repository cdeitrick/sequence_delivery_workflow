# import logging
import re
import subprocess
# from logging.config import fileConfig
from pathlib import Path
from typing import Optional, Tuple, Dict
import itertools
import boxio
import fileio
import emailio
import samplesheet
import pandas
import functools
# LOG_FILENAME = Path(__file__).parent / "data" / "log.txt"
# LOG_CONFIG = Path(__file__).parent / "data" / "logconfig.ini"
# logging.basicConfig(level = os.environ.get("LOGLEVEL", "INFO"), filename = LOG_FILENAME)

# fileConfig(LOG_CONFIG)
# logger = logging.getLogger(__name__)

DMUX_FOLDER = Path("/home/data/dmux")


def write_process_output(output_folder: Path, process: subprocess.CompletedProcess):
	stdout = process.stdout
	stderr = process.stderr

	with (output_folder / "stdout.txt").open('wb') as stdout_file:
		stdout_file.write(stdout)
	with (output_folder / "stderr.txt").open('wb') as stderr_file:
		stderr_file.write(stderr)


def demultiplex_samples(input_folder: Path, output_folder: Path):
	command = [
		"bcl2fastq",
		# "--input-dir", input_folder,
		"--no-lane-splitting",
		"--create-fastq-for-index-reads",
		"--runfolder-dir", input_folder,
		"--output-dir", output_folder
		# "--sample-sheet", filename
	]

	process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

	write_process_output(output_folder, process)


def process_project(project_folder:Path, sample_sheet: samplesheet.TableType, container_id: str)->Dict:
	""" Processes a project after dmuxing.
		Parameters
		----------
		project_folder: Path
		sample_sheet: TableType
		container_id: str
	"""
	# Rename the project sample folders
	project_name = project_folder.name
	print(f"processing project {project_folder.name}")
	fileio.rename_project_sample_folders(project_folder, sample_sheet)

	# Generate checksums for all of the project's files.
	print(f"Generating checksums")
	checksum_filename = fileio.generate_project_checksums(project_folder)

	# Upload the project to box.com
	print("Uploading to Box")
	project_link = boxio.upload_project_to_box(project_folder, container_id)

	checksum_df = pandas.read_csv(checksum_filename, sep = '\t')

	checksum_df['uploadStatus'] = [boxio.file_exists(project_name, i) for i in checksum_df[fileio.COLUMNS.filename].tolist()]
	failed_samples = set(checksum_df[checksum_df['uploadStatus'] == False][fileio.COLUMNS.sample_name].tolist())
	checksum_df.to_csv(project_folder / "checksums.status.tsv", sep = '\t')
	project_info = {
		'checksumFilename': str(checksum_filename),
		'statusFilename': str(project_folder / "checksums.status.tsv"),
		'projectLink': project_link,
		'totalSamples': len(checksum_df),
		'uploadedSamples': int(checksum_df['uploadStatus'].sum()), # Convert to int
		'failedSamples': sorted(failed_samples)
	}
	from pprint import pprint
	pprint(project_info)

	return project_info




def process_container(filename: Path, input_folder: Path, output_folder: Optional[Path] = None):
	"""
		Demultiplexes, renames, and checks the quality of samples.
	Parameters
	----------
	filename:Path
		Path to the samplesheet for the sequencing run.
	input_folder

	Returns
	-------

	"""
	print(f"Extracting the sample sheet from {filename}")
	sample_sheet = samplesheet.read_sample_sheet(filename)
	container_id, container_name = fileio.get_container_id(input_folder, filename)

	print(f"Container ID: {container_id}")
	print(f"Container Name: {container_name}")

	# Dmultiplex_samples
	if output_folder is None:
		dmux_folder = DMUX_FOLDER / container_name
	else:
		dmux_folder = output_folder

	print(f"dmux_folder exists: {dmux_folder.exists()}")
	if not dmux_folder.exists():
		print(f"Dmultiplexing to {dmux_folder}")
		demultiplex_samples(input_folder, dmux_folder)

	project_names = {i[samplesheet.COLUMNS.project] for i in sample_sheet}
	print(f"There are {len(project_names)} projects in the run {project_names}")
	project_status = dict()
	for project_name in sorted(project_names):
		project_folder = dmux_folder / project_name
		project_info = process_project(project_folder, sample_sheet, container_name)
		project_status[project_name] = project_info

	emailio.generate_email(project_status)



if __name__ == "__main__":
	string = "160526_NB501145_0011_AHMW7MBGXX/"
	match = re.search("^[\d]+_", string)
	print(match)
	print(match.group(0))
