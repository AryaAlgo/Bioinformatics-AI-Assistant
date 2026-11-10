
from Bio import SeqIO
from pathlib import Path
import argparse


def analyze_sequence(record):

    dna = record.seq.upper()
    length = len(dna)

    # Nucleotide composition
    a = dna.count("A")
    t = dna.count("T")
    g = dna.count("G")
    c = dna.count("C")

    # GC percentage
    known_bases = a + t + g + c
    gc = ((g + c) / known_bases * 100) if known_bases else 0

    # Reverse complement
    reverse_complement = dna.reverse_complement()

    # DNA transcription into RNA
    rna = dna.transcribe()

    # Incomplete codon handling
    remainder = length % 3
    complete_sequence = dna[:length - remainder]

    # Protein translation
    protein = complete_sequence.translate()

    return {
        "id": record.id,
        "length": length,
        "A": a,
        "T": t,
        "G": g,
        "C": c,
        "GC_percentage": round(gc, 2),
        "incomplete_bases": remainder,
        "reverse_complement": str(reverse_complement),
        "RNA": str(rna),
        "protein": str(protein)
    }


def main():

    parser = argparse.ArgumentParser(
        description="DNA FASTA Analyzer using Biopython"
    )

    parser.add_argument("fasta", help="Input FASTA file")
    args = parser.parse_args()

    fasta_file = Path(args.fasta)

    if not fasta_file.exists():
        print("Error: FASTA file not found.")
        return

    records = list(SeqIO.parse(str(fasta_file), "fasta"))

    if not records:
        print("Error: No sequences found.")
        return

    for record in records:

        result = analyze_sequence(record)

        print("\n" + "=" * 45)
        print("Sequence ID:", result["id"])
        print("Length:", result["length"])
        print("A:", result["A"])
        print("T:", result["T"])
        print("G:", result["G"])
        print("C:", result["C"])
        print("GC percentage:", result["GC_percentage"])
        print("Incomplete bases:", result["incomplete_bases"])
        print("Reverse complement:", result["reverse_complement"])
        print("RNA:", result["RNA"])
        print("Protein:", result["protein"])

    print("\nAnalysis completed!")


if __name__ == "__main__":
    main()
