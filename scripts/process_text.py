import argparse
from src.main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dialect", choices=["MSA", "EG", "Gulf"], default="MSA")
    parser.add_argument("--input", default="data/test_cases/msa_sample.txt")
    parser.add_argument("--output", default="output.json")
    args = parser.parse_args()

    main(dialect=args.dialect, input_file=args.input, output_file=args.output)