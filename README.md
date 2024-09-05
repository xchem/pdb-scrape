# pdb-scrape

Fetches necessary files from the protein data bank for collation and alignment with xchem-align

## Usage (at DLS)

1. If you are on a DLS linux machine:

`source /dls/science/groups/i04-1/software/max/load_py310.sh`

2. See the help screen:

`$PDB_SCRAPE/pdb-scrape --help`

3. Run the scraper:

`$PDB_SCRAPE/pdb-scrape pdb_codes.txt`

## Installation (if not at DLS)

*This program requires a modern python (`>=3.10`) installation*

1. Clone this directory

`git clone git@github.com:xchem/pdb-scrape`

2. Install pre-requisites

`pip install --upgrade molparse tqdm`

3. Create an environment variable to point to the directory (best to put it in your bash_profile or bashrc)

`export PDB_SCRAPE=/path/to/pdb-scrape`
