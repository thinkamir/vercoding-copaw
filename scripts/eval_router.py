#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / 'scripts'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from route_task import build_route  # noqa: E402

DEFAULT_CASES = ROOT / 'tests' / 'route_cases.json'
PRESET_TAGS = {
    'full': [],
    'smoke': ['smoke'],
    'native': ['native'],
    'vibe': ['vibe'],
    'risky': ['risky'],
    'edge': ['edge'],
}


def load_cases(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def filter_cases(cases, tags=None, case_ids=None):
    filtered = cases
    if tags:
        tag_set = set(tags)
        filtered = [c for c in filtered if tag_set.intersection(set(c.get('tags', [])))]
    if case_ids:
        id_set = set(case_ids)
        filtered = [c for c in filtered if c.get('id') in id_set]
    return filtered


def check_case(case):
    route = build_route(case['input'], top_n=5)
    expect = case.get('expect', {})
    failures = []

    def expect_equal(field, actual, expected):
        if actual != expected:
            failures.append(f"{field}: expected {expected!r}, got {actual!r}")

    if 'route_mode' in expect:
        expect_equal('route_mode', route.get('route_mode'), expect['route_mode'])

    primary = route.get('primary') or {}
    if 'primary_name' in expect:
        expect_equal('primary.name', primary.get('name'), expect['primary_name'])
    if 'primary_type' in expect:
        expect_equal('primary.type', primary.get('type'), expect['primary_type'])
    if 'primary_name_contains' in expect:
        needle = expect['primary_name_contains'].lower()
        actual = (primary.get('name') or '').lower()
        if needle not in actual:
            failures.append(f"primary.name should contain {needle!r}, got {primary.get('name')!r}")

    if 'requires_human_confirmation' in expect:
        expect_equal(
            'requires_human_confirmation',
            route.get('requires_human_confirmation'),
            expect['requires_human_confirmation'],
        )
    if 'can_auto_execute' in expect:
        expect_equal('can_auto_execute', route.get('can_auto_execute'), expect['can_auto_execute'])

    if 'min_confidence' in expect:
        actual = route.get('confidence', 0)
        if actual < expect['min_confidence']:
            failures.append(f"confidence should be >= {expect['min_confidence']}, got {actual}")

    if 'confirmation_reason_contains' in expect:
        actual_reasons = ' '.join(route.get('human_confirmation_reasons', [])).lower()
        for needle in expect['confirmation_reason_contains']:
            if needle.lower() not in actual_reasons:
                failures.append(f"human_confirmation_reasons should contain {needle!r}, got {route.get('human_confirmation_reasons')!r}")

    return {
        'id': case.get('id'),
        'tags': case.get('tags', []),
        'input': case.get('input'),
        'passed': not failures,
        'failures': failures,
        'actual': {
            'route_mode': route.get('route_mode'),
            'confidence': route.get('confidence'),
            'requires_human_confirmation': route.get('requires_human_confirmation'),
            'can_auto_execute': route.get('can_auto_execute'),
            'primary': route.get('primary'),
            'human_confirmation_reasons': route.get('human_confirmation_reasons'),
        }
    }


def format_text(results, selected_tags=None, selected_ids=None, preset=None):
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    scope_parts = []
    if preset:
        scope_parts.append('preset=' + preset)
    if selected_tags:
        scope_parts.append('tags=' + ','.join(selected_tags))
    if selected_ids:
        scope_parts.append('case_ids=' + ','.join(selected_ids))
    scope_text = f" ({'; '.join(scope_parts)})" if scope_parts else ''
    lines = [f"Router eval summary{scope_text}: total={total} passed={passed} failed={failed}"]
    for r in results:
        status = 'PASS' if r['passed'] else 'FAIL'
        tags = ','.join(r.get('tags', []))
        lines.append(f"- [{status}] {r['id']}" + (f" tags=[{tags}]" if tags else ''))
        if not r['passed']:
            for failure in r['failures']:
                lines.append(f"  - {failure}")
            lines.append(f"  - actual: {json.dumps(r['actual'], ensure_ascii=False)}")
    return '\n'.join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate route_task.py against expected routing cases.')
    parser.add_argument('--cases', default=str(DEFAULT_CASES), help='Path to route case JSON file.')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format.')
    parser.add_argument('--fail-on-error', action='store_true', help='Exit non-zero if any case fails.')
    parser.add_argument('--tag', action='append', default=[], help='Filter cases by tag. Can be repeated.')
    parser.add_argument('--case-id', action='append', default=[], help='Filter cases by exact case id. Can be repeated.')
    parser.add_argument('--preset', choices=list(PRESET_TAGS.keys()), help='Run a named preset suite.')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.preset and args.tag:
        print('Do not combine --preset with --tag. Use one filtering mode.', file=sys.stderr)
        sys.exit(1)

    selected_tags = PRESET_TAGS.get(args.preset, []) if args.preset else args.tag
    cases = load_cases(args.cases)
    cases = filter_cases(cases, tags=selected_tags, case_ids=args.case_id)
    if not cases:
        print('No cases matched the provided filters.', file=sys.stderr)
        sys.exit(1)

    results = [check_case(case) for case in cases]
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed

    payload = {
        'cases_file': args.cases,
        'selected_preset': args.preset,
        'selected_tags': selected_tags,
        'selected_case_ids': args.case_id,
        'total': total,
        'passed': passed,
        'failed': failed,
        'results': results,
    }

    if args.format == 'json':
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(results, selected_tags=selected_tags, selected_ids=args.case_id, preset=args.preset))

    if args.fail_on_error and failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
