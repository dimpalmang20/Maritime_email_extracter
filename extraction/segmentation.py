def split_email_blocks(text):

    # Split by separator
    blocks = text.split('---')

    cleaned_blocks = []

    for block in blocks:

        block = block.strip()

        if len(block) > 0:
            cleaned_blocks.append(block)

    return cleaned_blocks