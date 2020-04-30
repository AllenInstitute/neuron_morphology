import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template_config_path", type=str)
    parser.add_argument("image_uri", type=str)
    args = parser.parse_args()

    with open(args.template_config_path, "r") as raw_config_file:
        config = json.load(raw_config_file)

    config["Parameters"]["ImageUri"] = args.image_uri

    with open(args.template_config_path, "w") as config_file:
        json.dump(config, config_file, indent=2)

if __name__ == "__main__":
    main()
