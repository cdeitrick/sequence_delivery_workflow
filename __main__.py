import argparse
from pathlib import Path

import processes

parser = argparse.ArgumentParser()
parser.add_argument(
	"-i", "--input",
	type = Path,
	action = 'store',
	dest = 'input_folder',
	required = True
)
parser.add_argument(
	"-o", "--output",
	type = Path,
	action = "store",
	dest = "output_folder",
	required = True
)
parser.add_argument(
	"-s", "--samplesheet",
	type = Path,
	action = "store",
	dest = "filename"
)

if __name__ == "__main__":
	args = parser.parse_args()
	input_folder = args.input_folder
	output_folder = args.output_folder
	filename = args.filename
	if input_folder is None:
		message = "Please specify the input folder."
		raise ValueError(message)
	if output_folder is None:
		message = "Please specify the output folder"
		raise ValueError(message)
	if filename is None:
		filename = input_folder / "SampleSheet.csv"
	processes.process_container(filename, input_folder, output_folder)
