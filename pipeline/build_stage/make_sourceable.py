import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("params_path", type=str)
    parser.add_argument("output_path", type=str)
    args = parser.parse_args()

    with open(args.params_path, "r") as source_file:
        params = json.load(source_file)

    with open(args.output_path, "w") as out_file:
        lines = [f"{key.upper()}={value}" for key, value in params.items()]
        out_file.write("\n".join(lines))

if __name__ == "__main__":
    main()