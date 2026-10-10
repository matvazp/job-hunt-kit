#!/usr/bin/env python3
"""Filter candidate job-posting URLs against everything already collected.

Reads candidate URLs from stdin (one per line, blank lines and '- ' bullet
prefixes tolerated), prints the ones not seen before to stdout, and a summary
to stderr.

Seen = any URL anywhere in the postings list, plus any URL in any Markdown file
under the applications folder (vacancy notes carry the posting link).

Usage:
    python dedupe.py --workspace PATH < candidates.txt
    python dedupe.py --postings FILE --applications DIR < candidates.txt
    python dedupe.py --workspace PATH --show-seen   # print the normalised seen set

--workspace defaults to the current directory, with the postings list at
postings/job-postings-list.md and applications at applications/ (the
job-hunt.yaml defaults). Pass --postings / --applications to override.
Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

URL_RE = re.compile(r"https?://[^\s<>\"'\]\)|]+")

# Query parameters that carry the posting's identity rather than tracking noise.
# Everything else is stripped: utm_*, LinkedIn refId/trackingId, Workday
# location filters, etc.
IDENTITY_PARAMS = {
    "show",       # e.g. university vacancy pages: /all-vacancies/?show=166551
    "gh_jid",     # greenhouse
    "jobid", "job_id", "jid", "id", "reqid", "requisitionid",
    "vacancyid", "offerid", "positionid", "currentjobid",
}

LINKEDIN_JOB_RE = re.compile(r"/jobs/view/(?:[^/]*?-)?(\d+)")
LINKEDIN_GUEST_RE = re.compile(r"/jobs-guest/jobs/api/jobPosting/(\d+)")


def normalise(url: str) -> str:
    """Reduce a URL to a stable identity key."""
    url = url.strip().rstrip(".,;")
    try:
        parts = urlsplit(url)
    except ValueError:
        return url.lower()

    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    path = parts.path

    # LinkedIn: the numeric job id is the whole identity, whichever surface it came from.
    if host.endswith("linkedin.com"):
        for rx in (LINKEDIN_JOB_RE, LINKEDIN_GUEST_RE):
            m = rx.search(path)
            if m:
                return f"linkedin.com/jobs/view/{m.group(1)}"
        q = dict(parse_qsl(parts.query))
        if "currentJobId" in q:
            return f"linkedin.com/jobs/view/{q['currentJobId']}"

    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=False)
            if k.lower() in IDENTITY_PARAMS]
    kept.sort()
    query = urlencode(kept)

    path = path.rstrip("/")
    # Percent-encoding case varies between sources; fold it.
    path = re.sub(r"%[0-9a-fA-F]{2}", lambda m: m.group(0).upper(), path)

    return urlunsplit(("", host, path, query, "")).lstrip("/")


def seen_urls(postings: Path, applications: Path) -> dict[str, str]:
    """Normalised key -> where it was found."""
    seen: dict[str, str] = {}

    if postings.exists():
        for raw in URL_RE.findall(postings.read_text(encoding="utf-8")):
            seen.setdefault(normalise(raw), "postings list")
    else:
        print(f"warning: postings list not found at {postings}", file=sys.stderr)

    if applications.is_dir():
        for note in applications.rglob("*.md"):
            for raw in URL_RE.findall(note.read_text(encoding="utf-8", errors="replace")):
                seen.setdefault(normalise(raw), f"application: {note.parent.name}/{note.name}")
    else:
        print(f"warning: applications folder not found at {applications}", file=sys.stderr)

    return seen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--workspace", type=Path, default=Path.cwd())
    ap.add_argument("--postings", type=Path)
    ap.add_argument("--applications", type=Path)
    ap.add_argument("--show-seen", action="store_true")
    args = ap.parse_args()

    postings = args.postings or args.workspace / "postings" / "job-postings-list.md"
    applications = args.applications or args.workspace / "applications"
    seen = seen_urls(postings, applications)

    if args.show_seen:
        for key in sorted(seen):
            print(key)
        print(f"{len(seen)} seen URLs", file=sys.stderr)
        return 0

    candidates: list[str] = []
    for line in sys.stdin:
        line = line.strip().lstrip("-").strip()
        candidates.extend(URL_RE.findall(line))

    survivors: list[str] = []
    dropped: list[tuple[str, str]] = []
    within_batch: set[str] = set()

    for url in candidates:
        key = normalise(url)
        if key in seen:
            dropped.append((url, seen[key]))
        elif key in within_batch:
            dropped.append((url, "duplicate within this batch"))
        else:
            within_batch.add(key)
            survivors.append(url)

    for url in survivors:
        print(url)

    print(
        f"\n{len(candidates)} candidates -> {len(survivors)} new "
        f"({len(dropped)} dropped, {len(seen)} URLs already on file)",
        file=sys.stderr,
    )
    for url, why in dropped:
        print(f"  dropped: {url}  [{why}]", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
