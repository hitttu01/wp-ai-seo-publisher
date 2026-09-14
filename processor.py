import os
import re
import json
import random

# ==============================================================================
# SHORTCODES, KEYWORDS & INTERNAL LINKS CONFIGURATION
# ==============================================================================

# 7 Shortcodes (4 Content Blocks & 3 CTAs)
SHORTCODES_LIST = [
    "[content_block id=4657]",
    "[content_block slug=cta-1]",
    "[content_block id=4645]",
    "[content_block slug=cta-2]",
    "[content_block id=4642]",
    "[content_block slug=cta-3]",
    "[content_block id=5332]"
]

# Automotive keywords pool for random bolding (<b> or <strong>)
KEYWORDS_TO_BOLD = [
    "24/7 body shop",
    "collision repair",
    "auto body repair",
    "mechanic work",
    "paint repair",
    "dent repair",
    "insurance claims",
    "frame straightening",
    "emergency towing",
    "auto body shop",
    "certified technicians",
    "OEM parts",
    "lifetime warranty",
    "paint matching",
    "Glendale",
    "Studio City"
]

# Client's 6 exact internal links with keyword triggers
INTERNAL_LINKS = [
    {
        "keywords": ["body works", "body work", "collision repair", "body repair"],
        "html": '<a href="https://mycarautogroup.com/services/body-work/">body works</a>'
    },
    {
        "keywords": ["body shop Glendale", "Glendale body shop", "Glendale collision repair", "Glendale shop"],
        "html": '<a href="https://mycarautogroup.com/about/glendale/">body shop Glendale</a>'
    },
    {
        "keywords": ["body shop Studio City", "Studio City body shop", "Studio City collision", "Studio City shop"],
        "html": '<a href="https://mycarautogroup.com/about/studio-city/">body shop Studio City</a>'
    },
    {
        "keywords": ["mechanic work", "mechanical repairs", "mechanic service", "mechanical repair"],
        "html": '<a href="https://mycarautogroup.com/services/mechanic-work/">mechanic work</a>'
    },
    {
        "keywords": ["insurance claims", "insurance claim", "insurance coverage", "insurance deductible"],
        "html": '<a href="https://mycarautogroup.com/services/insurance-claim/">insurance claims</a>'
    },
    {
        "keywords": ["paint work", "paint repair", "auto paint", "paint refinishing", "paint matching"],
        "html": '<a href="https://mycarautogroup.com/services/paint-work/">paint work</a>'
    }
]

# Fallback sentence if 0 links match in the body
FALLBACK_LINK_SENTENCE = (
    '<p>For reliable collision repairs, visit our '
    '<a href="https://mycarautogroup.com/services/body-work/">body works</a> shop or contact our '
    'team for direct assistance with <a href="https://mycarautogroup.com/services/insurance-claim/">insurance claims</a>.</p>'
)


def format_h2_tags(content: str) -> str:
    """
    Converts all Markdown and HTML headings strictly to <h2 class="h2dav">Headline?</h2>.
    Ensures every heading ends with a question mark.
    """
    if not content:
        return ""

    def replace_h2(match):
        heading_text = re.sub(r'[*_`#]', '', match.group(1).strip())
        if not heading_text.endswith('?'):
            heading_text += '?'
        return f'<h2 class="h2dav">{heading_text}</h2>'

    # Convert markdown headings (#, ##, ###)
    content = re.sub(r'^#{1,6}\s+(.+)$', replace_h2, content, flags=re.MULTILINE)
    # Convert existing HTML headings (<h1> - <h6>)
    content = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', replace_h2, content, flags=re.IGNORECASE)
    return content


def format_paragraphs(content: str) -> str:
    """
    Ensures text sections between headings are cleanly wrapped in <p>...</p> tags.
    """
    if not content:
        return ""

    # Split by H2 tags to preserve them
    h2_split = re.split(r'(<h2 class="h2dav">.*?</h2>)', content, flags=re.IGNORECASE)
    formatted_parts = []

    for section in h2_split:
        if section.startswith('<h2'):
            formatted_parts.append(section)
        else:
            # Split section into raw paragraphs by double newlines
            raw_paras = [p.strip() for p in section.split("\n\n") if p.strip()]
            for p in raw_paras:
                # If paragraph already starts with <p> or a shortcode, keep as is
                if p.startswith('<p') or p.startswith('[content_block') or p.startswith('<div') or p.startswith('<ul') or p.startswith('<ol'):
                    formatted_parts.append(p)
                else:
                    # Clean single newlines within a paragraph into a single space
                    cleaned_p = re.sub(r'\s*\n\s*', ' ', p)
                    formatted_parts.append(f"<p>{cleaned_p}</p>")

    return "\n\n".join(formatted_parts)


def distribute_shortcodes_evenly(content: str, shortcodes: list = None) -> str:
    """
    Evenly distributes the 7 shortcodes throughout the ENTIRE article from top to bottom.
    Calculates interval based on the total number of paragraphs/elements so shortcodes
    are never clumped at the top.
    """
    if shortcodes is None:
        shortcodes = list(SHORTCODES_LIST)

    if not content or not shortcodes:
        return content

    # Split content into structured block elements (headings, paragraphs, existing blocks)
    raw_blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    if not raw_blocks:
        return "\n\n".join(shortcodes)

    # Filter out any pre-existing shortcode blocks to prevent duplication
    blocks = [b for b in raw_blocks if not any(sc in b for sc in shortcodes)]

    total_blocks = len(blocks)
    num_shortcodes = len(shortcodes)

    if total_blocks <= num_shortcodes:
        # If very few blocks, alternate between block and shortcode
        interleaved = []
        for i, block in enumerate(blocks):
            interleaved.append(block)
            if i < num_shortcodes:
                interleaved.append(shortcodes[i])
        # Append any remaining shortcodes
        if num_shortcodes > len(blocks):
            interleaved.extend(shortcodes[len(blocks):])
        return "\n\n".join(interleaved)

    # Calculate step interval to space all 7 shortcodes evenly across the body
    # E.g., for 24 blocks and 7 shortcodes, spacing = 24 / 8 = 3 blocks per interval
    step = max(1.0, (total_blocks + 1) / (num_shortcodes + 1))
    
    # Calculate target insertion positions (1-indexed into block list)
    target_indices = [int(round(step * (i + 1))) for i in range(num_shortcodes)]
    # Clamp target indices to ensure they are strictly within range
    target_indices = [min(max(1, idx), total_blocks) for idx in target_indices]

    # Build output with inserted shortcodes at calculated intervals
    result_blocks = []
    sc_idx = 0

    for block_num, block in enumerate(blocks, start=1):
        result_blocks.append(block)
        # Check if one or more shortcodes are scheduled after this block
        while sc_idx < num_shortcodes and target_indices[sc_idx] == block_num:
            result_blocks.append(shortcodes[sc_idx])
            sc_idx += 1

    # In case any shortcodes were not placed, append them before the last element or at end
    while sc_idx < num_shortcodes:
        if len(result_blocks) > 1:
            result_blocks.insert(-1, shortcodes[sc_idx])
        else:
            result_blocks.append(shortcodes[sc_idx])
        sc_idx += 1

    return "\n\n".join(result_blocks)


def bold_keywords(content: str, max_bold_count: int = 8) -> str:
    """
    Randomly applies <b> or <strong> tags to important automotive keywords
    throughout paragraph text, avoiding HTML tags, links, and headings.
    """
    if not content:
        return ""

    bolded_count = 0
    available_keywords = list(KEYWORDS_TO_BOLD)
    random.shuffle(available_keywords)

    for kw in available_keywords:
        if bolded_count >= max_bold_count:
            break

        tag = random.choice(["b", "strong"])
        pattern = re.compile(r'\b(' + re.escape(kw) + r')\b(?![^<]*>|[^<]*<\/a>|[^<]*<\/h2>)', re.IGNORECASE)

        if pattern.search(content):
            content, count = pattern.subn(lambda m, t=tag: f'<{t}>{m.group(0)}</{t}>', content, count=1)
            if count > 0:
                bolded_count += 1

    return content


def inject_internal_links(content: str, target_count: int = None) -> str:
    """
    Shuffles the 6 internal links and scans text using case-insensitive Regex (re.IGNORECASE).
    - Replaces matching keywords with the HTML links.
    - Strictly limits injection to 3 or 4 links total.
    - FALLBACK: If 0 links were injected, appends the exact fallback sentence.
    """
    if not content:
        return content

    if target_count is None:
        target_count = random.choice([3, 4])

    shuffled_links = list(INTERNAL_LINKS)
    random.shuffle(shuffled_links)

    links_injected = 0

    # Tokenize HTML to ensure replacement only happens in plain text (not inside tags or H2 blocks)
    tokens = re.split(r'(<h2 class="h2dav">.*?</h2>|<a\s+[^>]*>.*?</a>|<[^>]+>)', content, flags=re.IGNORECASE | re.DOTALL)

    for link_data in shuffled_links:
        if links_injected >= target_count:
            break

        link_html = link_data["html"]
        matched = False

        for kw in link_data["keywords"]:
            if matched or links_injected >= target_count:
                break

            for idx in range(len(tokens)):
                if tokens[idx].startswith('<'):
                    continue

                pattern = re.compile(r'\b(' + re.escape(kw) + r')\b', re.IGNORECASE)
                if pattern.search(tokens[idx]):
                    tokens[idx], count = pattern.subn(link_html, tokens[idx], count=1)
                    if count > 0:
                        links_injected += 1
                        matched = True
                        break

    result = "".join(tokens)

    # Fallback: If 0 links were injected, physically append exact fallback sentence
    if links_injected == 0:
        result = result.rstrip() + f"\n\n{FALLBACK_LINK_SENTENCE}"

    return result


def extract_yoast_description(content: str) -> str:
    """
    Dynamically generates the Yoast meta description:
    - Extracts the first paragraph from the article.
    - Extracts the last two sentences of that first paragraph.
    - Appends: ' Call us (747) 444-0040, or stop by, or schedule your estimate today.'
    """
    if not content:
        return "Call us (747) 444-0040, or stop by, or schedule your estimate today."

    # Strip HTML tags to inspect clean text paragraphs
    clean_paragraphs = []
    for match in re.finditer(r'<p>(.*?)</p>', content, flags=re.DOTALL | re.IGNORECASE):
        para_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        # Exclude shortcodes or fallback links
        if para_text and not para_text.startswith('[content_block') and len(para_text) > 40:
            clean_paragraphs.append(para_text)

    first_para = ""
    if clean_paragraphs:
        first_para = clean_paragraphs[0]
    else:
        # Fallback to general text split
        raw_text = re.sub(r'<[^>]+>', '', content).strip()
        first_para = raw_text.split('\n')[0] if raw_text else ""

    # Split paragraph into sentences
    sentences = re.split(r'(?<=[.!?])\s+', first_para.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    cta_suffix = "Call us (747) 444-0040, or stop by, or schedule your estimate today."

    if len(sentences) >= 2:
        last_two = " ".join(sentences[-2:])
        meta_desc = f"{last_two} {cta_suffix}"
    elif len(sentences) == 1:
        meta_desc = f"{sentences[0]} {cta_suffix}"
    else:
        meta_desc = f"Expert collision repair and body shop services in Glendale and Studio City. {cta_suffix}"

    return meta_desc.strip()


def process_and_format_article(content: str) -> str:
    """
    Complete Content Processor Pipeline:
    1. Standardizes 24/7 branding and eliminates em dashes (—).
    2. Strips markdown bold/italic asterisks.
    3. Enforces <h2 class="h2dav">Question?</h2> on all headings.
    4. Wraps body blocks in clean <p>...</p> tags.
    5. Randomly bolds key automotive keywords (<b> / <strong>).
    6. Shuffles and injects 3-4 internal links (with fallback).
    7. Evenly distributes the 7 shortcodes throughout the entire article.
    """
    if not content:
        return ""

    # 1. Standardization
    content = re.sub(r'\b24-7\b', '24/7', content, flags=re.IGNORECASE)
    content = content.replace("—", "-")

    # 2. Strip markdown asterisks
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    content = re.sub(r'\*(.*?)\*', r'\1', content)

    # 3. Format all headings as <h2 class="h2dav">Heading?</h2>
    content = format_h2_tags(content)

    # 4. Wrap text paragraphs
    content = format_paragraphs(content)

    # 5. Randomly bold important keywords
    content = bold_keywords(content)

    # 6. Inject 3-4 internal links with fallback
    content = inject_internal_links(content)

    # 7. Distribute 7 shortcodes evenly across the entire post
    content = distribute_shortcodes_evenly(content)

    return content


# Aliases for backward compatibility
clean_and_format_text = process_and_format_article
inject_shortcodes = distribute_shortcodes_evenly