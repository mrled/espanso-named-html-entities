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
import unicodedata


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


def entities_dict_to_espanso_package_dict(entities):
    """
    Convert entities dictionary to espanso package.yml contents,
    which contains a list of dictionaries with 'trigger' and 'replace' keys.
    """
    return {k: v for k, v in entities.items()}


def is_printable(char):
    """
    Determine if a character is printable.
    Returns True if the character is considered printable, False otherwise.
    """
    # Check if character is in a printable category
    category = unicodedata.category(char)
    # Control characters (Cc), Format characters (Cf), Surrogates (Cs), 
    # Private use (Co), and Unassigned (Cn) are considered non-printable
    if category in ['Cc', 'Cf', 'Cs', 'Co', 'Cn']:
        return False
    # Also check for specific non-printable characters
    if ord(char) < 32 and char not in '\t\n\r':
        return False
    return True


def filter_entities_by_class(entities, filter_class):
    """
    Filter entities based on the specified class.
    Returns a dictionary containing only entities matching the filter criteria.
    """
    if filter_class == "printable":
        return {k: v for k, v in entities.items() if all(is_printable(c) for c in v)}
    elif filter_class == "unprintable":
        return {k: v for k, v in entities.items() if any(not is_printable(c) for c in v)}
    else:
        # No filter or unknown filter - return all entities
        return entities


def prefix_dict_keys(d, prefix):
    """
    Prefix all keys in the dictionary with the given prefix.
    Returns a new dictionary with prefixed keys.
    """
    return {f"{prefix}{k}": v for k, v in d.items()}


def get_espanso_package_yml(d):
    """
    Write the espanso package.yml contents to the specified output file.

    json.dumps handles escaping for us, including:
    - Backslashes
    - Single and double quote characters
    - Special characters that contain things that need escaping, like `>⃒`
    """
    output = ["matches:"]
    for k, v in d.items():
        output.append(f"- trigger: {k}")
        quoted_v = json.dumps(v, ensure_ascii=False)
        output.append(f"  replace: {quoted_v}")
    return "\n".join(output)


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
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "espanso"],
        default="espanso",
        help="Output format. 'json' is just a JSON list of key/value pairs, while 'espanso' is a valid package.yml file. (Default: %(default)s)",
    )
    parser.add_argument(
        "-i",
        "--filter",
        choices=["printable", "unprintable"],
        default=None,
        help="Filter entities by character class. 'printable' includes only printable Unicode characters, 'unprintable' includes only non-printable characters.",
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

    # Apply filter if specified
    if args.filter:
        entities = filter_entities_by_class(entities, args.filter)
        logger.info(f"After filtering for {args.filter} characters: {len(entities)} entities")

    prefixed = prefix_dict_keys(entities, args.prefix)

    formatted = ""
    if args.format == "json":
        formatted = json.dumps(prefixed, indent=2, ensure_ascii=False)
    elif args.format == "espanso":
        formatted = get_espanso_package_yml(prefixed)
    else:
        logger.error(f"Unsupported format: {args.format}")
        sys.exit(1)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(formatted)
            logger.info(f"Output written to '{args.output}'")
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            sys.exit(1)
    else:
        # Write to stdout
        print(formatted)


if __name__ == "__main__":
    main()
