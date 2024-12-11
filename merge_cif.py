from pathlib import Path
import mrich
from gemmi import cif

HEADER_LOOP_COLUMNS = [
    ".id",
    ".three_letter_code",
    ".name",
    ".group",
    ".number_atoms_all",
    ".number_atoms_nh",
    ".desc_level",
]


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
        new_name = f"comp_{block.name}"
        new_block = outdoc.add_new_block(new_name)

        for item in block:  # This iterates through all data in the block
            new_block.add_item(item)

    # create the header block
    outdoc.add_new_block("comp_list", 0)
    header_block = outdoc.find_block("comp_list")
    header_loop = header_block.init_loop("_chem_comp", HEADER_LOOP_COLUMNS)

    # populate the header block
    for indoc in indocs:
        lig_name = indoc.sole_block().name.removeprefix("data_")
        header_loop.add_row([lig_name, lig_name, "?", "?", "?", "?", "?"])

    # Save the target document if needed
    outdoc.write_file(str(outfile.resolve()))

    return outfile
