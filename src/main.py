import argparse
import re as regex
import requests
import time
import pathlib
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse
from clint.textui import progress

class TOKENS(Enum):
    BEGIN_STATEMENT = "#"

class STATEMENTS(Enum):
    IMPORT_STATEMENT = "import"


def handle_url_import(dest_path, url, verbose=False):
    if (verbose):
        print(f"URL import found: {url}, attempting to resolve")
    response = requests.get(url, allow_redirects=True, stream=True)
    fname = ''
    if "Content-Disposition" in response.headers.keys():
        fname = regex.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
    else:
        fname = url.split("/")[-1]
    if (Path(fname).suffix != ".yymps"):
        print(f"The file at the URL {url} is not a .yymps file, cancelling download")
        return None
    path = Path(f"{dest_path}/temp/") 
    if (not path.is_dir):
        path.mkdir(exist_ok=True)
    path = path / fname
    path = path.resolve()
    #if (Path(path).is_file):
        #print(f"The package {fname} has already been downloaded, cancelling download.")
        #return None
    
    start = time.time()
    with open(path, 'wb') as f:
        chunk_size = 4048;
        chunk_next_draw = 0;
        chunk_amount = 10;
        chunks_size = 0;
        total_size = int(response.headers.get('content-length'))
        chunk_incr = total_size / chunk_amount;
        for i in response.iter_content(chunk_size=chunk_size):
            chunks_size += len(i)
            #print(chunks_size, chunk_next_draw)
            if (chunks_size > chunk_next_draw):
                chunk_next_draw += chunk_incr
                chunk_current = int((chunks_size / total_size) * chunk_amount)
                s = "#"*chunk_current
                e = "-"*(chunk_amount-chunk_current)
                print(f">[{s}{e}] {chunks_size}/{total_size}")
            f.write(i)
            f.flush()
        print(f">[DOWNLOADED] in {round(time.time()-start, 4)}s from: {url}")
    return path

def handle_github_import(dest_path, github_identifier, verbose=False):
    if (verbose):
        print(f"Github import {github_identifier} found, attempting to resolve")
    metadata_url = f"https://api.github.com/repos/{github_identifier}/releases/latest"
    metadata = requests.get(metadata_url, allow_redirects=True).json()
    for asset in metadata["assets"]:
        url = asset["browser_download_url"]
        handle_url_import(dest_path, url, verbose)

def uri_validator(x):
    try:
        result = urlparse(x)
        return result.scheme == "http" or result.scheme == "https"
    except:
        return False

def parse_imports(path, try_import_list, verbose=False):
    handled_imports = []
    for import_to_handle in try_import_list:
        import_to_handle = regex.sub(r"[\n\t\s]*", "", import_to_handle)
        is_github_iden = not regex.search("^[a-zA-Z0-9]+/[a-zA-Z0-9]+", import_to_handle) is None
        is_direct_link = uri_validator(import_to_handle)
        print(is_github_iden, is_direct_link)
        if (is_direct_link):
            handled_imports.append(
                handle_url_import(path, import_to_handle, verbose)
            )
            continue
        if (is_github_iden):
            handled_imports.append(
                handle_github_import(path, import_to_handle, verbose)
            )
            continue
        else:
            if (verbose):
                print(f"Mismatched import: {import_to_handle}")


def parse_dependency_file(dir, path, verbose=False):
    unhandled_imports = [];
    with open(path) as file:
        for line in file.readlines():
            match line[:1]:
                case TOKENS.BEGIN_STATEMENT.value:
                    unhandled_imports.append(line[8:])
    parse_imports(dir, unhandled_imports, verbose)

def parse_directory(dir, verbose=False):
    #is this a valid yyp directory ? 
    path = Path(dir)
    try:
        is_dir = path.is_dir()
        is_yyp = any([i.suffix == ".yyp" for i in path.iterdir()])
    finally:
        if (not is_dir or not is_yyp):
            raise Exception(f"Invalid YYP path provided {dir}, exiting.")

    if (verbose):
        print("Valid YYP found, proceeding to parse directories")

    path_to_dependencies = path / "notes" / "dependencies" / "dependencies.txt"
    if (not path_to_dependencies.is_file()):
        raise Exception("No dependency file found, exiting.")
    if (verbose):
        print("Valid dependency file found, proceeding to parse dependencies")

    parse_dependency_file(dir, path_to_dependencies, verbose)


def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("-verbose", "-verbose", action="store_true")
    parser.add_argument("-path", "-path", action="store", type=str)
    args = parser.parse_args()

    parse_directory(args.path, args.verbose)

main()
