import subprocess
from pathlib import Path
from typing import Tuple
import matplotlib.pyplot as plt
import pandas
from io import StringIO

def calculate_samtools_coverage(bam_filename: Path, output_filename: Path) -> Path:
	samtools = "/home/cld100/applications/samtools/bin/samtools"
	dfs = list()
	for cutoff in range(0, 40, 10):
		print(cutoff)
		command = [samtools, "depth","-q", str(cutoff), "-a", bam_filename]
		output = subprocess.check_output(command, universal_newlines = True)
		df = pandas.read_csv(StringIO(output), delimiter = "\t", names = ['chrom', 'position', 'depthOfCoverage'])
		df['coverageCutoff'] = cutoff
		dfs.append(df)
	dfs = pandas.concat(dfs)
	dfs.to_csv(str(output_filename), sep = "\t", index = False)
	return output_filename
# plot_coverage_all_positions(coverage_filename, output_folder)

def calculate_bedtools_coverage(bam_filename: Path, output_filename: Path) -> Path:
	command = ["bedtools", "genomecov", "-max", "1000", "-ibam", str(bam_filename)]
	output = subprocess.check_output(command, universal_newlines = False)
	output_filename.write_bytes(output)
	return output_filename

def calculate_coverage(bam_filename:Path, output_folder:Path)->Tuple[Path,Path]:
	samtools_path = output_folder / f"{bam_filename.name}.samtools.tsv"
	bedtools_path = output_folder / f"{bam_filename.name}.bedtools.tsv"
	calculate_bedtools_coverage(bam_filename, bedtools_path)
	calculate_samtools_coverage(bam_filename, samtools_path)

	return samtools_path, bedtools_path

def read_bedtools_coverage_file(coverage_filename: Path):
	return pandas.read_csv(coverage_filename, delimiter = "\t", names = ['chrom', 'depthOfCoverage', 'baseCount', 'chromSize', 'fraction'])


def per_base_bedtools_coverage(coverage_filename: Path, plot_filename: Path):
	"""
		Generates a graph with coverage on the x-axis and # basepairs on the y-axis.
	Parameters
	----------
	coverage_filename

	Returns
	-------

	"""
	coverage_data = read_bedtools_coverage_file(coverage_filename)
	chromosomes = coverage_data.groupby(by = 'chrom')
	print("Plotting...")

	fig, ax = plt.subplots(figsize = (20, 10))
	for chromosome, chromosome_data in chromosomes:
		if chromosome == 'genome': continue
		# counts = chromosome_data['baseCount'].value_counts()

		# counts = counts.sort_index()
		# counts = counts[counts.index < 200]
		ax.plot(chromosome_data['depthOfCoverage'].values, chromosome_data['fraction'].values, label = chromosome)
	ax.set_title('Per-Base Coverage')
	ax.set_xlabel('Reads')
	ax.set_ylabel('# of Bases')
	ax.legend()
	ax.grid(True, which = 'major')
	plt.tight_layout()
	plt.savefig(plot_filename, dpi = 300)

def per_base_samtools_coverage(coverage_filename: Path, plot_filename: Path):
	"""
		Generates a graph with coverage on the x-axis and # basepairs on the y-axis.
	Parameters
	----------
	coverage_filename

	Returns
	-------

	"""
	coverage_data = read_samtools_coverage_file(coverage_filename)
	chromosomes = coverage_data.groupby(by = 'coverageCutoff')
	print("Plotting...")

	fig, ax = plt.subplots(figsize = (20, 10))
	for chromosome, chromosome_data in chromosomes:
		print("Chrom", chromosome)
		counts = chromosome_data['depthOfCoverage'].value_counts()
		counts = counts.sort_index()
		above_1000 = counts[counts.index > 1000]
		counts = counts[counts.index < 1000]
		counts[1000] = above_1000.sum()
		if chromosome == 0:
			print(counts)
		if chromosome == 10:
			continue
		ax.plot(counts.index, counts.values, label = f"at least {chromosome}X coverage")
	ax.set_title('Per-Base Coverage')
	ax.set_xlabel('depthOfCoverage')
	ax.set_ylabel('# of Bases')
	ax.legend()
	ax.grid(True, which = 'major')
	ax.grid(True, which = 'minor')
	#plt.tight_layout()
	plt.savefig(plot_filename, dpi = 300)

def read_samtools_coverage_file(filename: Path) -> pandas.DataFrame:
	return pandas.read_csv(filename, delimiter = "\t")


def plot_coverage_all_positions(coverage_filename: Path, output_folder: Path):
	coverage = read_samtools_coverage_file(coverage_filename)
	coverage['count'] = coverage['count'].clip(0, 200)
	chromosomes = coverage.groupby(by = 'chrom')
	for chromosome, data in chromosomes:
		fig, ax = plt.subplots(figsize = (20, 10))
		ax.plot(data['position'].values, data['count'].values)
		ax.set_title('Genome Coverage')
		ax.set_xlabel('Position')
		ax.set_ylabel('# Reads')
		plt.savefig(output_folder / f"{chromosome}.fullcoverage.png", dpi = 200)


def plot_coverage(filename: Path, output_folder: Path):
	if not output_folder.exists():
		output_folder.mkdir()

	samtools_path, bedtools_path = calculate_coverage(filename, output_folder)
	# coverage_filename = filename

	per_base_bedtools_coverage(coverage_filename, output_folder)




if __name__ == "__main__":
	coverage_filename = Path("/media/cld100/FA86364B863608A1/Users/cld100/Storage/riptide/1-1.depth.tsv")
	filename = Path("/media/cld100/FA86364B863608A1/Users/cld100/Storage/riptide/1-1.bam")

	#plot_coverage(filename, coverage_filename.with_name('1-1'))
	#calculate_samtools_coverage(filename, coverage_filename)
	per_base_samtools_coverage(coverage_filename, coverage_filename.with_name('samtools.png'))
