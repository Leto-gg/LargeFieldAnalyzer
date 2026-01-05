#!/usr/bin/env python3
"""
Simple YARA-based malware signature matcher.
Scans a folder for files matching YARA rules.
"""

import argparse
import os
import sys
import logging
from pathlib import Path

try:
    import yara
except ImportError:
    print("Error: yara-python not installed. Run: pip install yara-python")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def load_rules(rules_path: str) -> yara.Rules:
    """Load YARA rules from a file or directory."""
    path = Path(rules_path)
    
    if path.is_file():
        log.info(f"Loading rules from file: {rules_path}")
        return yara.compile(filepath=str(path))
    
    if path.is_dir():
        rule_files = {}
        for f in path.glob("*.yar"):
            rule_files[f.stem] = str(f)
        for f in path.glob("*.yara"):
            rule_files[f.stem] = str(f)
        
        if not rule_files:
            log.error(f"No .yar or .yara files found in {rules_path}")
            sys.exit(1)
        
        log.info(f"Loading {len(rule_files)} rule file(s) from: {rules_path}")
        return yara.compile(filepaths=rule_files)
    
    log.error(f"Rules path not found: {rules_path}")
    sys.exit(1)


def scan_file(rules: yara.Rules, filepath: Path) -> list:
    """Scan a single file and return matches."""
    try:
        matches = rules.match(str(filepath))
        return matches
    except yara.Error as e:
        log.warning(f"Could not scan {filepath}: {e}")
        return []


def scan_folder(rules: yara.Rules, folder: str, recursive: bool = True) -> dict:
    """Scan all files in a folder."""
    results = {}
    folder_path = Path(folder)
    
    if not folder_path.exists():
        log.error(f"Folder not found: {folder}")
        sys.exit(1)
    
    pattern = "**/*" if recursive else "*"
    files = [f for f in folder_path.glob(pattern) if f.is_file()]
    
    log.info(f"Scanning {len(files)} file(s) in: {folder}")
    
    for filepath in files:
        matches = scan_file(rules, filepath)
        if matches:
            results[str(filepath)] = [m.rule for m in matches]
            log.warning(f"MATCH: {filepath} -> {[m.rule for m in matches]}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Scan folder for malware using YARA rules")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("-r", "--rules", required=True, help="YARA rules file or directory")
    parser.add_argument("--no-recursive", action="store_true", help="Don't scan subdirectories")
    parser.add_argument("-q", "--quiet", action="store_true", help="Only show matches")
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    rules = load_rules(args.rules)
    results = scan_folder(rules, args.folder, recursive=not args.no_recursive)
    
    # summary
    if results:
        log.info(f"Scan complete. {len(results)} file(s) matched.")
        print("\n--- Summary ---")
        for filepath, matched_rules in results.items():
            print(f"  {filepath}: {', '.join(matched_rules)}")
    else:
        log.info("Scan complete. No matches found.")


if __name__ == "__main__":
    main()