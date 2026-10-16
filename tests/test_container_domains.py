"""Malformed JSON containers must be reported as domain errors by both parsers."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from cases import boundary_case
from model import Model, InvalidModel
from checker import Semantics, CheckError

class ContainerDomainTests(unittest.TestCase):
    def test_malformed_containers_have_declared_errors(self):
        edits = [
            ('capacity', None), ('capacity', 2), ('retain', None),
            ('retain', True), ('outputs', [[]]), ('outputs', [{}]),
        ]
        for field, value in edits:
            for parser, error in ((Model, InvalidModel), (Semantics, CheckError)):
                with self.subTest(field=field, value=value, parser=parser.__name__):
                    instance=boundary_case()
                    instance[field]=copy.deepcopy(value)
                    with self.assertRaises(error):
                        parser(instance)

    def test_unhashable_mode_is_rejected_before_deduplication(self):
        for parser, error in ((Model, InvalidModel), (Semantics, CheckError)):
            with self.subTest(parser=parser.__name__):
                instance=boundary_case()
                instance['nodes'][0]['modes']=[{}]
                with self.assertRaises(error):
                    parser(instance)
