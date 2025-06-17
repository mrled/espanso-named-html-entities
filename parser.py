#!/usr/bin/env python3
"""
Parse HTML entities table from an HTML file.
Looks for the first table in a div with id="named-character-references-table".
Outputs JSON to stdout or a specified file.
"""

import re
import html
import sys
import os
import json
import argparse
import logging


# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)
logger = logging.getLogger(__name__)


def find_table_in_div(html_content):
    """
    Find the first table within div#named-character-references-table.
    Returns the table HTML or None if not found.
    """
    # Pattern to find div with id="named-character-references-table"
    # and extract its content including nested tags
    div_pattern = (
        r'<div[^>]*\sid=["\']?named-character-references-table["\']?[^>]*>(.*?)</div>'
    )
    div_match = re.search(div_pattern, html_content, re.DOTALL | re.IGNORECASE)

    if not div_match:
        logger.error("Could not find div with id='named-character-references-table'.")
        return None

    div_content = div_match.group(1)
    table_pattern = r"<table[^>]*>.*?</table>"
    table_match = re.search(table_pattern, div_content, re.DOTALL | re.IGNORECASE)
    if not table_match:
        logger.error("Could not find any table in the specified div.")
        return None
    return table_match.group(0)


def parse_html_entities_table(table_html):
    """
    Parse HTML table containing entity definitions.
    Returns a dictionary mapping entity names to their Unicode glyphs.
    """
    entities = {}

    # Pattern to match table rows with entity information
    # <td> <code>entity_name</code> <td> unicode <td> <span ...>glyph</span>
    pattern = (
        r"<td>\s*<code>([^<]+)</code>\s*<td>\s*[^<]+\s*<td>\s*<span[^>]*>([^<]+)</span>"
    )

    matches = re.findall(pattern, table_html)

    for entity_name, glyph in matches:
        # Clean up entity name (remove semicolon if present)
        entity_name = entity_name.strip()

        # Some entity names are allowed with or without a semicolon at the end.
        # We don't need to support that in our espanso package,
        # so we just ignore legacy entities without a semicolon.
        if not entity_name.endswith(";"):
            continue

        # Unescape HTML entities in the glyph (e.g., &amp; -> &)
        # Most entities in the table have their actual glyphs,
        # but those that would mess up HTML parsing like &<" etc are escaped.
        glyph = html.unescape(glyph)

        # Store in dictionary
        entities[entity_name] = glyph

    return entities


def prefix_dict_keys(d, prefix):
    """
    Prefix all keys in the dictionary with the given prefix.
    Returns a new dictionary with prefixed keys.
    """
    return {f"{prefix}{k}": v for k, v in d.items()}


def main():
    parser = argparse.ArgumentParser(
        description="Parse HTML entities table from an HTML file and output JSON."
    )
    parser.add_argument("input_file", help="HTML file containing the entities table")
    parser.add_argument(
        "-o", "--output", help="Output file (default: stdout)", default=None
    )
    parser.add_argument(
        "-p",
        "--prefix",
        default=":",
        help="Prefix for entity names (default: %(default)s)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        logger.error(f"File '{args.input_file}' not found.")
        sys.exit(1)

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        sys.exit(1)

    table_html = find_table_in_div(html_content)
    if not table_html:
        logger.error("Could not find any table in the HTML file.")
        sys.exit(1)

    entities = parse_html_entities_table(table_html)

    if not entities:
        logger.error("No entities found in the table.")
        sys.exit(1)
    else:
        logger.info(f"Parsed {len(entities)} HTML entities from {args.input_file}")

    prefixed = prefix_dict_keys(entities, args.prefix)

    json_output = json.dumps(prefixed, ensure_ascii=False, indent=2)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_output)
            logger.info(f"Output written to '{args.output}'")
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            sys.exit(1)
    else:
        # Write to stdout
        print(json_output)


if __name__ == "__main__":
    main()
