import hashlib
from pathlib import Path
from typing import Any, Union

def _generate_checksum(metric: Any, filename: Union[str, Path], blocksize: int = 2 ** 20) -> str:
	""" Generates the SHA-1 hash of a file. Does not require a lot of memory.

		Parameters
		----------
		filename: string
			The file to generate the md5sum for.
		blocksize: int; default 2**20
			The amount of memory to use when
			generating the md5sum string.

		Returns
		-------
		str
			The md5sum string.
	"""
	with open(str(filename), "rb") as f:
		while True:
			buf = f.read(blocksize)
			if not buf: break
			metric.update(buf)
	return metric.hexdigest()


def generate_file_sha1(filename: Union[str, Path]) -> str:
	metric = hashlib.sha1()
	return _generate_checksum(metric, filename)


def generate_file_md5(filename: Union[str, Path]) -> str:
	metric = hashlib.md5()
	return _generate_checksum(metric, filename)
