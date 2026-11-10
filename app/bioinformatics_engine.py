from Bio.Seq import Seq


def analyze_dna_sequence(sequence):
    """
    Analyze a DNA sequence using Biopython 1.83.

    GC percentage uses only canonical A, T, G and C bases.
    Translation uses reading frame 0.
    Incomplete trailing codon bases are excluded.
    """

    if not isinstance(sequence, str):
        raise TypeError("DNA sequence must be a string.")

    dna_string = "".join(sequence.split()).upper()

    if not dna_string:
        raise ValueError("DNA sequence is empty.")

    valid_symbols = set("ACGTRYSWKMBDHVN")
    invalid_symbols = set(dna_string) - valid_symbols

    if invalid_symbols:
        raise ValueError(
            "Invalid DNA symbols: " + ", ".join(sorted(invalid_symbols))
        )

    dna = Seq(dna_string)

    a = dna.count("A")
    t = dna.count("T")
    g = dna.count("G")
    c = dna.count("C")

    canonical_bases = a + t + g + c

    if canonical_bases == 0:
        gc_percentage = None
    else:
        gc_percentage = round(
            ((g + c) / canonical_bases) * 100, 2
        )

    remainder = len(dna) % 3
    complete_length = len(dna) - remainder

    complete_dna = dna[:complete_length]

    return {
        "sequence_length": len(dna),
        "A": a,
        "T": t,
        "G": g,
        "C": c,
        "GC_percentage": gc_percentage,
        "reverse_complement": str(dna.reverse_complement()),
        "RNA": str(dna.transcribe()),
        "protein_frame_0": str(complete_dna.translate()),
        "incomplete_trailing_bases": remainder
    }
