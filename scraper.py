#!/usr/bin/env python

import os
import urllib.request
from pathlib import Path

import molparse as mp

import mcol
from mlog import setup_logger
logger = setup_logger('PdbScraper')

OUTPUT_DIR='output'
REMOVE_RESIDUES = "EDO MPD DMS PEG ETG PO4"

RCSB_PDB_DOWNLOAD_URL = 'http://files.rcsb.org/download/'
RCSB_MTZ_DOWNLOAD_URL = 'http://edmaps.rcsb.org/coefficients/'
RCSB_CIF_DOWNLOAD_URL = 'http://files.rcsb.org/ligands/download/'

def read_pdb_codes(
    file: str
) -> list[str]:

    """read PDB codes from a text file

    :param file: path to text file
    :returns: a list of lowercase PDB code strings

    """

    codes = []
    with open(file, 'rt') as f:
        for line in f:
            codes.append(line.strip().lower())

    if not codes:
        logger.error(f'Could not read any PDB codes from {PDB_CODE_FILE}')

    return codes

def download_pdb(
    code: str, 
    out_dir: Path
) -> Path:

    out_file = out_dir/f'{code}_rcsb.pdb'
    logger.writing(out_file)
    urllib.request.urlretrieve(f'{RCSB_PDB_DOWNLOAD_URL}/{code}.pdb', out_file)
    return out_file

def download_mtz(
    code: str, 
    out_dir: Path
) -> Path:

    out_file = out_dir/f'{code}.mtz'
    logger.writing(out_file)
    urllib.request.urlretrieve(f'{RCSB_MTZ_DOWNLOAD_URL}/{code}.mtz', out_file)
    return out_file

def download_cif(
    code: str, 
    out_dir: Path
) -> Path:

    out_file = out_dir/f'{code}_rcsb.cif'
    logger.writing(out_file)
    urllib.request.urlretrieve(f'{RCSB_CIF_DOWNLOAD_URL}/{code}.cif', out_file)
    return out_file

def clean_pdb(
    in_file: Path, 
    # remove_heterogens: bool = True,
) -> str:

    out_file = str(in_file).replace('_rcsb.pdb', '.pdb')

    sys = mp.parse(in_file, keep_headers=True)

    # if remove_heterogens:
    #   sys.remove_heterogens()

    if REMOVE_RESIDUES:
        sys.remove_residues(names=REMOVE_RESIDUES.split())

    lig_code = extract_ligand_code(sys)

    assert lig_code

    sys.rename_residues(lig_code, 'LIG')

    mp.write(out_file, sys)

    return lig_code

def clean_cif(
    in_file: Path,
    lig_code: str,
) -> None:

    out_file = str(in_file).replace('_rcsb.cif', '.cif')
    buffer = in_file.read_text()
    buffer = buffer.replace(lig_code, 'LIG')
    logger.writing(out_file)
    with open(out_file,'wt') as f:
        f.write(buffer)

def extract_ligand_code(
    sys: mp.System,
) -> str:

    hetnam_lines = [s for s in sys._header_data if s.startswith('HETNAM')]

    lig_codes = [l.split()[1] for l in hetnam_lines]

    lig_codes = [c for c in lig_codes if c not in REMOVE_RESIDUES.split()]

    if len(lig_codes) != 1:
        logger.error(f'Multiple candidate ligands: {lig_codes}')
        return None

    return lig_codes[0]

def parse_args():

    import argparse
    parser = argparse.ArgumentParser(prog='pdb-scrape', description='Fetches necessary files from the protein data bank for collation and alignment with xchem-align')

    parser.add_argument("pdb_code_file", help='Text file containing PDB codes on separate lines')
    parser.add_argument("-o", '--output', help=f"output directory/path (defaults to {OUTPUT_DIR})")
    parser.add_argument("-f", '--force', action='store_true', help="don't warn when overwriting data")
    parser.add_argument("-r", '--remove', help=f"space-delimited list of residue names to ignore/remove (defaults to '{REMOVE_RESIDUES}'')")
    parser.add_argument("-c", '--clean', action='store_true', help=f"clean up original RCSB files")

    return parser.parse_args()

def main():

    global OUTPUT_DIR
    global REMOVE_RESIDUES

    args = parse_args()

    PDB_CODE_FILE = args.pdb_code_file
    OUTPUT_DIR = args.output or OUTPUT_DIR
    REMOVE_RESIDUES = args.output or REMOVE_RESIDUES

    logger.var("PDB_CODE_FILE", PDB_CODE_FILE)
    logger.var("OUTPUT_DIR", OUTPUT_DIR)
    logger.var("REMOVE_RESIDUES", REMOVE_RESIDUES)

    # read PDB codes
    codes = read_pdb_codes(PDB_CODE_FILE)

    if not codes:
        return

    out_dir = Path(OUTPUT_DIR)
    logger.writing(out_dir)
    
    try:
        out_dir.mkdir(parents=True, exist_ok=False)
    
    except FileExistsError:

        if not args.force:
            
            logger.warning(f'Would overwrite existing directory {out_dir}')
        
            try:
                input(f"{mcol.bold}Press any key to continue, or CTRL-C to abort{mcol.clear}")
            
            except KeyboardInterrupt:
                print()
                exit()

        for child in out_dir.iterdir():
            if child.is_file():
                child.unlink()

    for code in codes:
        logger.title(code)
        pdb_file = download_pdb(code, out_dir)
        mtz_file = download_mtz(code, out_dir)
        lig_code = clean_pdb(pdb_file)
        cif_file = download_cif(lig_code, out_dir)
        clean_cif(cif_file, lig_code)

    if args.clean:
        for child in out_dir.iterdir():
            if child.is_file():
                if '_rcsb' in str(child):
                    child.unlink()

if __name__ == '__main__':
    main()
