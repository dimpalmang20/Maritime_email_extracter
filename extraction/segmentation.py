import re


def split_email_blocks(text):

    separators = [

        r'—+',
        r'-{10,}',
        r'\n\s*\n\s*\n',
        r'(?=Cargo:)',
        r'(?=LP:)',
        r'(?=POL:)',
        r'(?=A/C)',
        r'(?=ACCT)',
        r'(?=DELY:)',
        r'(?=Delivery:)',
        r'(?=MV\s)',
        r'(?=M/T\s)'

    ]

    pattern = "|".join(separators)

    blocks = re.split(pattern, text)

    clean_blocks = []

    for block in blocks:

        block = block.strip()

        if len(block) > 40:

            clean_blocks.append(block)

    return clean_blocks