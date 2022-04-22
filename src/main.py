import argparse
from os import mkdir
import re as regex
from matplotlib.cbook import flatten
import requests
import time
import pathlib
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

class TOKENS(Enum):
    BEGIN_STATEMENT = "#"

class STATEMENTS(Enum):
    IMPORT_STATEMENT = "import"


def download_file_url(dest, url, verbose=False):
    chunks_size = Path(dest).stat().st_size if Path(dest).is_file() else 0
    resume_header = {'Range':f'bytes={chunks_size}-'}
    
    response = requests.get(url, stream=True, headers=resume_header)
    total_size = int(response.headers.get('content-length'))
    if (chunks_size >= total_size):
        print(f"Package from {url} already imported, skipping")
        return

    start = time.time()
    with open(dest, 'ab') as f:
        chunk_size = 4048;
        chunk_next_draw = 0;
        chunk_amount = 10;
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
    return dest

def parse_url_import(url, verbose):
    response = requests.get(url, allow_redirects=True, stream=True)
    fname = ''
    if "Content-Disposition" in response.headers.keys():
        fname = regex.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
    else:
        fname = url.split("/")[-1]
    if (Path(fname).suffix != ".yymps"):
        print(f"The file at the URL {url} is not a .yymps file, cancelling download")
        return None
    return (fname, url)

def parse_github_import(github_identifier, verbose=False):
    if (verbose):
        print(f"Github import {github_identifier} found, attempting to resolve")
    metadata_url = f"https://api.github.com/repos/{github_identifier}/releases/latest"
    metadata = requests.get(metadata_url, allow_redirects=True).json()
    if (not metadata.get("assets", False)):
        print(f"The github project {github_identifier} does not contain a release. Please contact the project author. Details can be found in this projects .readme")
        return None
    
    url = metadata["assets"][0]["browser_download_url"]
    url = parse_url_import(url, verbose)
    return url

def uri_validator(x):
    try:
        result = urlparse(x)
        return result.scheme == "http" or result.scheme == "https"
    except:
        return False

def parse_imports(path, try_import_list, verbose=False):
    parsed_imports = []
    for import_to_handle in try_import_list:
        import_to_handle = regex.sub(r"[\n\t\s]*", "", import_to_handle)
        is_github_iden = not regex.search("^[a-zA-Z0-9]+/[a-zA-Z0-9]+", import_to_handle) is None
        is_direct_link = uri_validator(import_to_handle)
        
        if (is_direct_link):
            parsed_imports.append(
                parse_url_import(import_to_handle, verbose)
            )
            continue
        if (is_github_iden):
            parsed_imports.append(
                parse_github_import(import_to_handle, verbose)
            )
            continue
        else:
            if (verbose):
                print(f"Mismatched import: {import_to_handle}")
    return parsed_imports


def parse_dependency_file(path, verbose=False):
    unparsed_imports = [];
    with open(path) as file:
        for line in file.readlines():
            match line[:1]:
                case TOKENS.BEGIN_STATEMENT.value:
                    unparsed_imports.append(line[8:])
    return unparsed_imports

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

    return path_to_dependencies


def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("-upgrade", "-upgrade", action="store_true")
    parser.add_argument("-verbose", "-verbose", action="store_true")
    parser.add_argument("-path", "-path", action="store", type=str)
    args = parser.parse_args()
    working_dir = args.path
    verbose = args.verbose
    upgrade = args.upgrade
    path_to_dependencies = parse_directory(working_dir, verbose)
    unparsed_imports = parse_dependency_file(path_to_dependencies, verbose)
    parsed_imports = parse_imports(working_dir, unparsed_imports, verbose)
    parsed_imports = list(filter(None, parsed_imports))
    temp_dir = f"{working_dir}/temp"
    for (fname, url) in parsed_imports:
        path = f"{temp_dir}/{fname}"
        download_file_url(path, url)

main()
