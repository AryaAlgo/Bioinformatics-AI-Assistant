import unittest

from app.bioinformatics_engine import analyze_dna_sequence


class TestDNAAnalyzer(unittest.TestCase):

    def test_normal_dna(self):
        result = analyze_dna_sequence("ATGCGATCGATCGATCGATCG")
        self.assertEqual(result["sequence_length"], 21)
        self.assertEqual(result["A"], 5)
        self.assertEqual(result["T"], 5)
        self.assertEqual(result["G"], 6)
        self.assertEqual(result["C"], 5)
        self.assertEqual(result["GC_percentage"], 52.38)

    def test_reverse_complement(self):
        result = analyze_dna_sequence("ATCG")
        self.assertEqual(result["reverse_complement"], "CGAT")

    def test_transcription(self):
        result = analyze_dna_sequence("ATCG")
        self.assertEqual(result["RNA"], "AUCG")

    def test_translation(self):
        result = analyze_dna_sequence("ATCG")
        self.assertEqual(result["protein_frame_0"], "I")
        self.assertEqual(result["incomplete_trailing_bases"], 1)

    def test_ambiguous_bases(self):
        result = analyze_dna_sequence("ATGCNNRY")
        self.assertEqual(result["GC_percentage"], 50.0)

    def test_only_ambiguous_bases(self):
        result = analyze_dna_sequence("NNNN")
        self.assertIsNone(result["GC_percentage"])

    def test_empty_sequence(self):
        with self.assertRaises(ValueError):
            analyze_dna_sequence("")

    def test_invalid_sequence(self):
        with self.assertRaises(ValueError):
            analyze_dna_sequence("ATGX")


if __name__ == "__main__":
    unittest.main()
