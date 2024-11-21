from pathlib import Path
import mrich
from gemmi import cif


def merge_cifs(infiles: Path, outfile: Path):  # , code_map: dict[str,str]):

    mrich.print("merging:", ",".join([p.name for p in infiles]), "-->", outfile)

    # each infile should contain only one block, e.g. data_LG1

    indocs = []

    for infile in infiles:
        indocs.append(cif.read_file(str(infile.resolve())))

    assert len(indocs) > 1

    # Load or create target document
    outdoc = cif.Document()

    for doc in indocs:
        block = doc.sole_block()
        new_block = outdoc.add_new_block(block.name)

        for item in block:  # This iterates through all data in the block
            new_block.add_item(item)

    # Save the target document if needed
    outdoc.write_file(str(outfile.resolve()))

    return outfile
