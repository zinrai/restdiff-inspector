#!/usr/bin/env python3

"""
RestDiff Inspector

A flexible tool for comparing data from two different REST API endpoints.
This tool allows users to specify different key paths for each API,
making it adaptable to various API structures and response formats.

Usage:
    python restdiff_inspector.py -u1 <url1> -u2 <url2> -k1 <keys1> -k2 <keys2> [-t <timeout>]

For more information, use the --help option.
"""

import json
import urllib.request
import sys
import argparse
from typing import List, Dict, Any
from urllib.error import URLError


def fetch_data(url: str, timeout: int = 5) -> Dict:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read())
    except URLError as e:
        print(f"Error fetching data from {url}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_data(data: Dict, keys: List[str]) -> List[Any]:
    result = []
    def extract_recursive(current_data, current_keys):
        if not current_keys:
            return current_data
        key = current_keys[0]
        if isinstance(current_data, dict):
            return extract_recursive(current_data.get(key, {}), current_keys[1:])
        elif isinstance(current_data, list):
            return [extract_recursive(item, current_keys) for item in current_data]
        else:
            return None

    extracted = extract_recursive(data, keys)
    if isinstance(extracted, list):
        result.extend([item for item in extracted if item is not None])
    elif extracted is not None:
        result.append(extracted)
    return result


def compare_data(data1: List[Any], data2: List[Any]) -> Dict[str, List[Any]]:
    set1 = set(map(str, data1))  # Convert to strings for comparison
    set2 = set(map(str, data2))
    return {
        "only_in_first": sorted(set1 - set2),
        "only_in_second": sorted(set2 - set1)
    }


def main():
    parser = argparse.ArgumentParser(description="RestDiff Inspector: Compare data from two REST API endpoints with different structures")
    parser.add_argument("-u1", "--url1", required=True, help="URL for the first API endpoint")
    parser.add_argument("-u2", "--url2", required=True, help="URL for the second API endpoint")
    parser.add_argument("-k1", "--keys1", required=True, help="Comma-separated list of keys to extract data from the first API")
    parser.add_argument("-k2", "--keys2", required=True, help="Comma-separated list of keys to extract data from the second API")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout for API requests in seconds (default: 5)")
    args = parser.parse_args()

    keys1 = args.keys1.split(',')
    keys2 = args.keys2.split(',')

    data1 = fetch_data(args.url1, args.timeout)
    data2 = fetch_data(args.url2, args.timeout)

    extracted1 = extract_data(data1, keys1)
    extracted2 = extract_data(data2, keys2)

    diff = compare_data(extracted1, extracted2)

    print(f"Data only in {args.url1}:")
    for item in diff["only_in_first"]:
        print(f"  - {item}")

    print(f"\nData only in {args.url2}:")
    for item in diff["only_in_second"]:
        print(f"  - {item}")

    if not diff["only_in_first"] and not diff["only_in_second"]:
        print("No differences found between the two API endpoints.")


if __name__ == '__main__':
    main()
