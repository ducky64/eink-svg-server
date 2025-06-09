import os.path
import unittest

from csv_logger import CsvLogger


class CsvLoggerTestCase(unittest.TestCase):
  TEST_DIR = "test"
  TEST_FILE = f"{TEST_DIR}/test.csv"

  def test_create(self):
    os.makedirs(self.TEST_DIR, exist_ok=True)
    if os.path.isfile(self.TEST_FILE):
      os.remove(self.TEST_FILE)

    logger = CsvLogger(self.TEST_FILE, ["a", "b", "c"])
    logger.log({"a": "1", "b": "2", "c": "3"})
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c\n1,2,3\n")

  def test_append(self):
    logger = CsvLogger(self.TEST_FILE, ["a", "b", "c"])
    os.makedirs(self.TEST_DIR, exist_ok=True)
    with open(self.TEST_FILE, 'w') as f:
      f.write("a,b,c\n1,2,3\n")

    logger.log({"c": "4", "a": "5", "b": "6"})
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c\n1,2,3\n5,6,4\n")

    logger.log({"b": "7", "c": "8", "a": "9"})
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c\n1,2,3\n5,6,4\n9,7,8\n")

  def test_update_headers(self):
    os.makedirs(self.TEST_DIR, exist_ok=True)
    with open(self.TEST_FILE, 'w') as f:
      f.write("a,b,c\n1,2,3\n")

    logger = CsvLogger(self.TEST_FILE, ["a", "b", "d", "c"])
    logger.update_headers()
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c,d\n1,2,3,\n")

    logger.log({"c": "4", "a": "5", "b": "6", "d": "7"})
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c,d\n1,2,3,\n5,6,4,7\n")

    logger.update_headers()

  def test_update_headers_nodelete(self):
    os.makedirs(self.TEST_DIR, exist_ok=True)
    with open(self.TEST_FILE, 'w') as f:
      f.write("a,b,c\n1,2,3\n")

    logger = CsvLogger(self.TEST_FILE, ["a", "b"])
    logger.update_headers()
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c\n1,2,3\n")

    logger = CsvLogger(self.TEST_FILE, ["a", "b", "d"])
    logger.update_headers()
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c,d\n1,2,3,\n")

    logger.log({"a": "5", "b": "6"})
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c,d\n1,2,3,\n5,6,,\n")

    logger.update_headers()

  def test_extrafield(self):
    logger = CsvLogger(self.TEST_FILE, ["a", "b", "c"])
    os.makedirs(self.TEST_DIR, exist_ok=True)
    with open(self.TEST_FILE, 'w') as f:
      f.write("a,b,c\n1,2,3\n")

    logger.log({"a": "4", "d": "5", "c": "6"})
    with open(self.TEST_FILE, 'r') as f:
      self.assertEqual(f.read(), "a,b,c\n1,2,3\n4,,6\n")

  def test_read(self):
    logger = CsvLogger(self.TEST_FILE, ["a", "b", "c"])
    os.makedirs(self.TEST_DIR, exist_ok=True)
    with open(self.TEST_FILE, 'w') as f:
      f.write("a,b,c\n1,2,3\n")

    self.assertEqual(logger.read(), "a,b,c\n1,2,3\n")

  def test_read_empty(self):
    logger = CsvLogger(self.TEST_FILE, ["a", "b", "c"])
    os.makedirs(self.TEST_DIR, exist_ok=True)
    if os.path.isfile(self.TEST_FILE):
      os.remove(self.TEST_FILE)

    self.assertEqual(logger.read(), "")
