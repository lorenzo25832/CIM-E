#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path
import shutil
import datetime

def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive experiment results and config into a subfolder in the results"
    )

    parser.add_argument(
        "experiment_name",
        help="Name of the experiment",
    )

    parser.add_argument(
        "archive_name",
        help="Name of the archive",
    )

    return parser.parse_args()


def change_to_git_root():
    try:
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        print("Error: not inside a Git repository.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: git is not installed or not found in PATH.", file=sys.stderr)
        sys.exit(1)

    if os.getcwd() != repo_root:
        os.chdir(repo_root)

    return repo_root


def main():
    args = parse_args()

    repo_root = change_to_git_root()

    results_folder = Path(repo_root) / "results" / args.experiment_name
    results_csv = results_folder / (args.experiment_name+".csv")
    config_json = Path(repo_root) / "src" / "configs" / (args.experiment_name+".json")
    if not results_folder.is_dir():
        raise ValueError(f"{results_folder=} does not exist")
    if not results_csv.is_file() or results_csv.stat().st_size == 0:
        raise ValueError(f"{results_csv=} does not exist or empty")
    if not config_json.is_file() or config_json.stat().st_size == 0:
        raise ValueError(f"{config_json=} does not exist or empty")

    archive_folder = results_folder / (datetime.datetime.now().strftime("%Y_%m_%d ") + args.archive_name)
    if archive_folder.is_dir():
        raise ValueError("archive already exists")

    os.mkdir(archive_folder)
    shutil.copy(config_json, archive_folder / config_json.name)
    shutil.copy(results_csv, archive_folder / results_csv.name)

if __name__ == "__main__":
    main()
