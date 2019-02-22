import subprocess
from pathlib import Path
from typing import Tuple


def count_number_of_reads(filename: Path) -> int:
	""" Returns the number of reads in a fastq file."""
	if filename.suffix == '.gz':
		command = f"zcat {filename}"
	else:
		command = f"cat {filename}"
	process = subprocess.Popen(command.split(), stdout = subprocess.PIPE)
	output = subprocess.check_output(["wc", "-l"], stdin = process.stdout)

	reads = int(output.strip()) / 4
	return int(reads)


def calculate_coverage_from_bam(filename: Path) -> float:
	samtools_command = ["/home/cld100/applications/samtools/bin/samtools", "depth", "-a", filename]
	samtools_process = subprocess.check_output(samtools_command, universal_newlines = True)
	# print(samtools_process)
	lines = [line.split('\t') for line in samtools_process.splitlines()]
	counts = [line[-1] for line in lines if line[-1]]
	coverage = sum(map(float, counts)) / len(counts)
	return coverage


def calculate_coverage_from_reads(filename: Path, genome_length: int) -> float:
	# reads = count_number_of_reads(filename)
	read_length, read_count = get_read_stats(filename)
	return (read_count * read_length) / genome_length


def calculate_paired_coverage(left: Path, right: Path, genome_length: int) -> float:
	read_length, read_count = get_read_stats(left, right)
	return (read_count * read_length) / genome_length


def get_read_stats(left: Path, right: Path = None) -> Tuple[int, int]:
	program = "/home/cld100/applications/bbmap/readlength.sh"
	command = ["bash", program, f"in={left}"]
	if right:
		command += [f"in2={right}"]
	# print(" ".join(command))
	output = subprocess.check_output(command, universal_newlines = True, stderr = subprocess.PIPE)
	line = output.splitlines()[-1]
	read_length, read_count, *_ = line.split('\t')
	read_length = int(read_length)
	read_count = int(read_count)

	return read_length, read_count


if __name__ == "__main__":
	folder = Path("/media/cld100/FA86364B863608A1/Users/cld100/Storage/riptide/fastqs/")
	for filename in folder.iterdir():
		cov = calculate_coverage_from_reads(filename, 7702840)
		print(f"{cov:.2f}\t{filename}")
