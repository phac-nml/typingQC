#!/usr/bin/env python

import json
from pathlib import Path
import sys
import argparse
import os
import glob


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Creates example output JSON for loading into IRIDA Next",
        epilog="Example: python irida-next-output.py --json-output output.json *.out",
    )
    parser.add_argument("files", nargs="+")
    parser.add_argument(
        "--json-output",
        action="store",
        dest="json_output",
        type=str,
        help="JSON output file",
        default=None,
        required=True,
    )

    args = parser.parse_args(argv)

    json_output_file = Path(args.json_output)
    if json_output_file.exists():
        sys.stderr.write(f"Error: --json-output [{json_output_file}] exists")
        return 1

    input_files = args.files
    if isinstance(input_files, str):
        input_files = [input_files]

    input_files = [Path(f) for f in input_files]
    samples_dict = {s.name: s for s in input_files}

    output_dict = {
        "files": {
            "summary": {},
            "samples": {},
        },
        "metadata": {
            "samples": {},
        },
    }

    for sample in samples_dict:
        metadata_sample = {"output_name": samples_dict[sample].name}
        output_dict["metadata"]["samples"][sample] = metadata_sample

    samples_json = json.dumps(output_dict, indent=4)
    with open(json_output_file, "w") as oh:
        oh.write(samples_json)

    print(f"Output written to [{json_output_file}]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
