import argparse

from src.extract import extract
from src.transform import transform_load


def cli():
    parser = argparse.ArgumentParser("fipi-parser")

    parser.add_argument("--db_path", type=str, help="DB path (sqlite3)")
    parser.add_argument("--chroma_dir", type=str, help="Chroma persistent directory")

    args = parser.parse_args()

    return args


def main():
    args = cli()

    db_path = args.db_path
    chroma_dir = args.chroma_dir

    extract(db_path)
    transform_load(db_path, chroma_dir)


if __name__ == "__main__":
    main()