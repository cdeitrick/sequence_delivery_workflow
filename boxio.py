import functools
import itertools
from pathlib import Path
from typing import Any, List, Optional, Union
from pprint import pprint
import boxapi
import fileio
import logging
logger = logging.getLogger(__file__)


def _get_project_names_from_dmux_folder(folder: Path):
	""" Infers the project names in a sequencing run from the folder names after dmuxing."""

	folders = [i.name for i in folder.iterdir() if i.is_dir()]
	project_names = [i for i in folders if i not in {'Reports', 'Stats'}]
	return project_names


@functools.lru_cache(maxsize = 128)
def get_project_files_on_box(project_name: str) -> List:
	project_folder = get_box_folder(boxapi.FOLDER, project_name)
	containers = project_folder.item_collection['entries']
	containers = [i.get(fields = None, etag = None) for i in containers]
	project_files = list()
	for container in containers:
		container_samples:List[Any] = [i.get(fields = None, etag = None) for i in container.item_collection['entries']]
		container_files:List[List[Any]] = [sample.item_collection['entries'] for sample in container_samples if hasattr(sample, 'item_collection')]
		project_files += list(itertools.chain.from_iterable(container_files))
	#pprint(project_files)
	#project_files = list(itertools.chain.from_iterable(project_files))
	return project_files


def file_exists(project_name: str, file_name: Union[str, Path]) -> bool:
	if isinstance(file_name, Path):
		file_name = file_name.name
	project_files = get_project_files_on_box(project_name)

	project_filenames = [i.name for i in project_files]
	return file_name in project_filenames


def get_box_folder(parent_folder, item_name: str):
	""" Attempts to find an existing project folder on box.com. If no folder is found, create one."""
	existing_items = parent_folder.item_collection['entries']
	print(parent_folder, item_name)
	pprint(existing_items)
	for existing_item in existing_items:
		if existing_item.name == item_name:
			subfolder = existing_item
			break
	else:
		# Could not locate the folder on box.com. create one.

		subfolder = parent_folder.create_subfolder(item_name)
	# Retrieve the folder properties.
	subfolder = subfolder.get(fields = None, etag = None)
	return subfolder


def upload_project_to_box(project_folder: Path, container_id: str, project_name: Optional[str] = None) -> str:
	"""
		Uploads all files for a project to box.com and returns a sharable link to the project folder.
	Parameters
	----------
	project_folder
	container_id
	project_name

	Returns
	-------

	"""
	if project_name is None:
		project_name = project_folder.name
	# Create a folder for the selected project
	project_box_folder = get_box_folder(boxapi.FOLDER, project_name)

	# Create a subfolder for the current sequencing run.
	container_folder = get_box_folder(project_box_folder, container_id)
	# Upload the file checksums.
	checksum_filename = project_folder / "checksums.tsv"
	if checksum_filename.exists() and not file_exists(project_name, 'checksums.tsv'):
		try:
			container_folder.upload(str(checksum_filename))
		except:
			pass
	# Upload sample folders
	sample_folders = fileio.get_project_samples(project_folder)

	for sample_folder in sample_folders:
		print("\t Uploading ", sample_folder.name)
		# Need to create a subfolder for each sample.
		sample_box_folder = get_box_folder(container_folder, sample_folder.name)
		upload_project_samples_to_box(sample_folder, sample_box_folder)

	return project_box_folder.get_shared_link()


def upload_project_samples_to_box(samples: fileio.Sample, sample_box_folder: Any):
	existing_files = [i.name for i in sample_box_folder.item_collection['entries']]

	for filename in samples:
		if filename.name in existing_files: continue
		if filename.stat().st_size > 50E6:
			# The chunked API raises an error if the filesize is less than 20MB.
			chunked_uploader = sample_box_folder.get_chunked_uploader(str(filename))
			uploaded_file = chunked_uploader.start()
		else:
			uploaded_file = sample_box_folder.upload(str(filename))
		print("\t\t\tUploaded ", filename, "\t", uploaded_file)


if __name__ == "__main__":
	pass
