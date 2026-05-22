import re


_TECH_HEADING = re.compile(
    r"(?im)^\s*(?:speed\s*(?:and|&)?\s*consumption|bunker|ballast\s*water|"
    r"weather\s*(?:working|clause)|main\s*engine|disclaimer|without\s*prejudice)\b"
)

MARITIME_BLOCK_START = re.compile(
    r"(?im)^\s*(?:\d+[\)\.\-]\s*)?(?:cargo|commodity|mv|m/v|m\.v|m/t|vsl|vessel|"
    r"open|tc|tct|a/c|acct|account|delivery|dely|redelivery|redel|redely|laycan|"
    r"lp|pol|loading\s*port|discharge\s*port)\b"
)

_MARITIME_SHORT_SIGNAL = re.compile(
    r"(?i)(?:"
    r"loading\s*port|discharge\s*port|commodity\s*:|"
    r"\d{3,6}\s*/\s*\d{3,6}|"
    r"\d{1,3}(?:[.,'\s]\d{3})+\s*(?:\+-?\s*\d+\s*%)?\s*(?:mt|mts|metric\s*tons?)|"
    r"\d{3,6}\s*mt\b|\d{3,6}mt\b"
    r")"
)

_GREETING_OR_SIGNATURE = re.compile(
    r"(?is)^\s*(?:dear\s+(?:all|sir|sirs|team)[,\s]*|good\s+day[,\s]*|"
    r"best\s+regards[,\s]*|kind\s+regards[,\s]*|thanks(?:\s+and\s+regards)?[,\s]*)+$"
)

_TC_START = re.compile(
    r"(?im)^\s*(?:\d+[\)\.\-]\s*)?(?:a/c|acct|account|account\s*:|"
    r"\d+\s+tct\b|tct\b|trip\b|time\s*charter\b|"
    r"(?:mv|m/v|vsl)\b.*\btct\b)"
)


def _is_maritime_block(block: str) -> bool:

    if not block:
        return False

    block = str(block).strip()

    if len(block) < 25:
        return False

    lowered = block.lower()

    # PURE EMAIL HEADER BLOCKS
    header_hits = sum([
        lowered.startswith("from:"),
        lowered.startswith("sent:"),
        lowered.startswith("to:"),
        lowered.startswith("subject:"),
        lowered.startswith("cc:"),
    ])

    if header_hits >= 1 and len(block.splitlines()) <= 6:
        return False

    # PURE CONTACT BLOCKS
    contact_hits = sum([
        "mobile" in lowered,
        "whatsapp" in lowered,
        "teams/skype" in lowered,
        "website" in lowered,
        "@hotmail.com" in lowered,
        "@gmail.com" in lowered,
    ])

    if contact_hits >= 2:
        return False

    # TECHNICAL SPEC BLOCKS
    spec_hits = len(re.findall(
        r"(?i)\b(grain capacity|bale capacity|loa|beam|lbp|grt|nrt|consumption|knots|mt/day)\b",
        lowered
    ))

    if spec_hits >= 3:
        return False

    maritime_signals = len(re.findall(
        r"(?i)\b(cargo|quantity|mts|mt|laycan|dely|redely|tct|delivery|redelivery|pol|pod|load|discharge|dwt|open)\b",
        lowered
    ))

    return maritime_signals >= 2

BULLET_LINE = re.compile(r"(?im)^\s*(?:[-*•]|\d+[\)\.])\s+")


def _strip_forwarded_noise(text):

    if not text:
        return ""

    # =========================================
    # REMOVE HTML REMNANTS
    # =========================================

    text = re.sub(r'<[^>]+>', ' ', text)

    # =========================================
    # REMOVE EMAIL HEADERS
    # =========================================

    header_patterns = [

        r'(?im)^from\s*:.*$',
        r'(?im)^sent\s*:.*$',
        r'(?im)^to\s*:.*$',
        r'(?im)^cc\s*:.*$',
        r'(?im)^bcc\s*:.*$',
        r'(?im)^subject\s*:.*$',

    ]

    for pattern in header_patterns:
        text = re.sub(pattern, ' ', text)

    # =========================================
    # REMOVE CONTACT LINES
    # =========================================

    contact_patterns = [

        r'(?im)^mobile\s*:.*$',
        r'(?im)^mob\s*:.*$',
        r'(?im)^phone\s*:.*$',
        r'(?im)^tel\s*:.*$',
        r'(?im)^fax\s*:.*$',
        r'(?im)^website\s*:.*$',
        r'(?im)^web\s*:.*$',
        r'(?im)^email\s*:.*$',
        r'(?im)^teams.*$',
        r'(?im)^skype.*$',
        r'(?im)^wechat.*$',
        r'(?im)^whatsapp.*$',

    ]

    for pattern in contact_patterns:
        text = re.sub(pattern, ' ', text)

    # =========================================
    # REMOVE URLs
    # =========================================

    text = re.sub(
        r'https?://\S+|www\.\S+',
        ' ',
        text,
        flags=re.I
    )

    # =========================================
    # REMOVE EMAIL IDS
    # =========================================

    text = re.sub(
        r'[\w\.-]+@[\w\.-]+',
        ' ',
        text,
        flags=re.I
    )

    # =========================================
    # REMOVE LONG SIGNATURE BLOCKS
    # =========================================

    signature_patterns = [

        r'(?is)best\s+regards.*',
        r'(?is)kind\s+regards.*',
        r'(?is)warm\s+regards.*',
        r'(?is)thanks\s+and\s+regards.*',
        r'(?is)with\s+best\s+regards.*',

    ]

    for pattern in signature_patterns:

        match = re.search(pattern, text)

        if match and match.start() > 150:
            text = text[:match.start()]
            break

    # =========================================
    # REMOVE REPLY CHAINS
    # =========================================

    reply_patterns = [

        r'(?is)-+\s*original\s+message\s*-+.*',
        r'(?is)on\s+.*?wrote\s*:.*',
        r'(?is)forwarded\s+message.*',
        r'(?is)begin\s+forwarded\s+message.*',

    ]

    for pattern in reply_patterns:

        match = re.search(pattern, text)

        if match and match.start() > 150:
            text = text[:match.start()]
            break

    # =========================================
    # REMOVE EXCESS SPACES
    # =========================================

    text = re.sub(r'\n{3,}', '\n\n', text)

    text = re.sub(r'[ \t]{2,}', ' ', text)

    return text.strip()


def _split_by_blank_groups(text):
    groups = re.split(r"\n\s*\n+", text)
    return [g.strip() for g in groups if g and g.strip()]


def _split_bullets(group):
    lines = [line for line in group.splitlines() if line.strip()]
    if not lines:
        return []
    if sum(1 for line in lines if BULLET_LINE.match(line)) < 2:
        return [group.strip()]

    chunks = []
    current = []
    for line in lines:
        if BULLET_LINE.match(line) and current:
            chunks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current).strip())
    return [chunk for chunk in chunks if len(chunk) > 20]


def _split_compound_cargo_text(text):
    # Secondary split for inline/paragraph emails with multiple cargo fixtures.
    marker = re.compile(
        r"(?im)(?=^\s*(?:cargo|commodity|mv|m/v|vsl)\s*[:\-]?)"
    )
    pieces = [p.strip() for p in re.split(marker, text) if p and p.strip()]
    if len(pieces) <= 1:
        return [text.strip()]
    kept = []
    for p in pieces:
        if len(p) > 25 or re.search(r"(?i)^(?:cargo|commodity|qty|quantity|lp|pol|dp|pod|laycan)\s*[:\-]", p):
            kept.append(p)
    return kept or [text.strip()]


def _split_tc_requirements(text):
    """Keep each TC requirement intact while allowing multi-TC emails to split."""
    lines = (text or "").splitlines()
    if len(lines) < 3:
        return [text.strip()] if text and text.strip() else []

    chunks = []
    current = []
    current_has_tc_detail = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                current.append(line)
            continue
        starts_tc = bool(_TC_START.search(stripped))
        if starts_tc and current and current_has_tc_detail:
            chunks.append("\n".join(current).strip())
            current = [line]
            current_has_tc_detail = False
        else:
            current.append(line)
        if re.search(r"(?i)\b(?:delivery|dely|redelivery|redel|redely|duration|laycan|tct|time\s*charter|ttl|adc|adcom)\b", stripped):
            current_has_tc_detail = True
    if current:
        chunks.append("\n".join(current).strip())
    return [c for c in chunks if c]


def _merge_contextual_blocks(blocks):
    def is_fixture_detail(value):
        v = (value or "").strip().lower()
        return bool(
            re.search(
                r"(?i)^(?:cargo|commodity|commodit|qty|quantity|lp|pol|dp|pod|loading\s*port|"
                r"discharge\s*port|laycan|l/?d\s*rates?|load/?disch|load\s*rate|discharge\s*rate)\b",
                v,
            )
            or re.search(r"(?i)\b\d{1,3}(?:[.,'\s]\d{3})+\s*(?:\+/-\s*\d+%)?\s*(?:mt|mts|metric\s*tons?)\b", v)
            or re.search(r"(?i)\b\d{3,6}\s*/\s*\d{3,6}\b", v)
        )

    grouped = []
    current_group = []
    for block in blocks:
        if is_fixture_detail(block):
            if current_group and re.match(r"(?i)^\s*(?:cargo|commodity|commodit)\s*[:\-]", block.strip()):
                grouped.append("\n".join(current_group).strip())
                current_group = []
            current_group.append(block.strip())
            continue
        if current_group:
            grouped.append("\n".join(current_group).strip())
            current_group = []
        grouped.append(block.strip())
    if current_group:
        grouped.append("\n".join(current_group).strip())

    blocks = grouped
    merged = []
    idx = 0
    while idx < len(blocks):
        current = blocks[idx].strip()
        current_lower = current.lower()
        next_block = blocks[idx + 1].strip() if idx + 1 < len(blocks) else ""
        next_lower = next_block.lower()

        current_is_cargo_line = bool(
            re.match(r"(?i)^(?:cargo|commodity)\s*[:\-]", current_lower)
            or re.search(r"(?i)\b\d{3,6}\s*mts?\b.*\b[a-z]{3,}", current_lower)
            or re.search(r"(?i)\b\d{3,6}mts?\b.*\b[a-z]{3,}", current_lower)
            or re.search(r"(?i)\bmts?\b.*\b[a-z]{3,}", current_lower)
        )
        next_has_route = bool(re.search(r"(?i)\b(lp|pol|dp|pod|laycan|dwt)\b", next_lower))
        current_vessel_header = bool(re.search(r"(?i)\b(tct|time\s*charter|a/c|acct|account)\b", current_lower))
        next_tc_detail = bool(re.search(r"(?i)\b(delivery|dely|redelivery|redel|redely|duration|adc|ttl)\b", next_lower))
        next_starts_requirement = bool(_TC_START.search(next_block))

        next_starts_cargo = bool(re.match(r"(?i)^\s*(?:cargo|commodity|commodit)\s*[:\-]", next_block))

        if current_is_cargo_line and next_block and next_has_route and not next_starts_cargo:
            merged.append(f"{current}\n{next_block}".strip())
            idx += 2
            continue
        if current_vessel_header and next_block and next_tc_detail and not next_starts_requirement:
            merged.append(f"{current}\n{next_block}".strip())
            idx += 2
            continue

        merged.append(current)
        idx += 1
    return merged


def _split_technical_sections(text):
    """Drop text from first technical/legal heading onward in each segment."""
    matches = list(_TECH_HEADING.finditer(text))
    if not matches:
        return [text]
    chunks = []
    pos = 0
    for m in matches:
        if m.start() - pos > 40:
            chunks.append(text[pos : m.start()].strip())
        pos = m.end()
    if not chunks:
        return [text[: matches[0].start()].strip()] if matches[0].start() > 40 else []
    return [c for c in chunks if len(c) > 25] or [text]

def is_noise_block(block: str):

    if not block:
        return True

    block_low = block.lower().strip()

    if len(block_low) < 20:
        return True

    # =====================================
    # EMAIL HEADER BLOCKS
    # =====================================

    header_hits = len(re.findall(

        r'(?i)\b(from|sent|to|subject|cc|bcc)\s*:',

        block_low

    ))

    if header_hits >= 2:
        return True

    # =====================================
    # CONTACT BLOCKS
    # =====================================

    contact_hits = len(re.findall(

        r'(?i)\b(mobile|mob|phone|tel|fax|website|email|skype|teams|whatsapp|wechat)\b',

        block_low

    ))

    if contact_hits >= 2:
        return True

    # =====================================
    # TECHNICAL SPEC BLOCKS
    # =====================================

    tech_hits = len(re.findall(

        r'(?i)\b(grt|nrt|loa|beam|lbp|tpc|consumption|knots|mt/day|ifo|vlsfo|lsmgo)\b',

        block_low

    ))

    if tech_hits >= 5:
        return True

    # =====================================
    # MARITIME SIGNALS
    # =====================================

    maritime_hits = len(re.findall(

        r'(?i)\b(cargo|qty|quantity|mts|mt|laycan|dely|redely|delivery|redelivery|pol|pod|load|discharge|dwt|open|tct)\b',

        block_low

    ))

    if maritime_hits == 0:
        return True

    # =====================================
    # PURE SIGNATURES
    # =====================================

    signature_hits = len(re.findall(

        r'(?i)\b(best regards|kind regards|warm regards|thanks and regards)\b',

        block_low

    ))

    if signature_hits >= 1:
        return True

    return False

def split_email_blocks(text):
    text = _strip_forwarded_noise(text)
    text = text.replace("\r\n", "\n")
    text = "\n\n".join(_split_technical_sections(text))

    separators = [

        r'—+',
        r'(?m:^\s*\+{3,}\s*$)',
        r'(?m:^\s*-{3,}\s*$)',
        r'\n\s*\n\s*\n',
        r'(?im:(?=^\s*Cargo\s*:))',
        r'(?im:(?=^\s*Commodity\s*:))',
        r'(?im:(?=^\s*LP\s*:))',
        r'(?im:(?=^\s*POL\s*:))',
        r'(?im:(?=^\s*A/C\b))',
        r'(?im:(?=^\s*ACCT\b))',
        r'(?im:(?=^\s*ACCOUNT\s*:))',
        r'(?im:(?=^\s*MV\s))',
        r'(?im:(?=^\s*M/T\s))'

    ]

    pattern = "|".join(separators)

    blocks = re.split(pattern, text)

    clean_blocks = []

    for block in blocks:

        block = block.strip()
        if is_noise_block(block):
            continue
        if _is_maritime_block(block):

            clean_blocks.append(block)

    grouped_blocks = []
    for block in clean_blocks:
        for tc_block in _split_tc_requirements(block):
            grouped_blocks.extend(_split_by_blank_groups(tc_block))

    block_level = []
    for group in grouped_blocks:
        block_level.extend(_split_bullets(group))

    final_blocks = []
    for block in block_level:
        if MARITIME_BLOCK_START.search(block):
            final_blocks.extend(_split_compound_cargo_text(block))
        else:
            final_blocks.append(block.strip())

    deduped = []
    seen = set()
    merged_blocks = _merge_contextual_blocks(final_blocks)
    for block in merged_blocks:
        norm = re.sub(r"\s+", " ", block.lower()).strip()
        if _is_maritime_block(block) and norm not in seen:
            seen.add(norm)
            deduped.append(block.strip())

    return deduped
