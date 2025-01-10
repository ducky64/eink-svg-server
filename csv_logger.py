import csv
import os
from typing import List, Dict
import logging


logger = logging.getLogger(__name__)


class CsvLogger:
  """Logger that appends structured data to a CSV file. Creates one if it doesn't exist.
  Closes the CSV between append operations, and reads in headers each time.
  If data doesn't have a header in the CSV, that cell is discarded and a log warning generated."""
  def __init__(self, filename: str, default_headers: List[str]):
    self._filename = filename
    self._default_headers = default_headers

  def log(self, data: Dict[str, str]):
    if not os.path.exists(self._filename):
      logger.info(f"creating new file {self._filename}")
      with open(self._filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(self._default_headers)

    # read the headers
    with open(self._filename, 'r', newline='') as f:
      dictreader = csv.DictReader(f)
      fieldnames = list(dictreader.fieldnames)

    with open(self._filename, 'a', newline='') as f:
      missing_fields = set(data.keys()) - set(fieldnames)
      if missing_fields:
        logger.warn(f"missing fields in file: {missing_fields}")
      dictwriter = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
      dictwriter.writerow(data)
