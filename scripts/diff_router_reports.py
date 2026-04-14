#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def load_report(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def round_conf(value):
    if value is None:
        return None
    return round(float(value), 4)


def compare_case(old_case, new_case, confidence_threshold=0.0):
    changes = []
    old_actual = old_case.get('actual', {})
    new_actual = new_case.get('actual', {})

    old_primary = old_actual.get('primary') or {}
    new_primary = new_actual.get('primary') or {}

    if old_case.get('passed') != new_case.get('passed'):
        changes.append({
            'field': 'passed',
            'old': old_case.get('passed'),
            'new': new_case.get('passed'),
        })

    if old_actual.get('route_mode') != new_actual.get('route_mode'):
        changes.append({
            'field': 'route_mode',
            'old': old_actual.get('route_mode'),
            'new': new_actual.get('route_mode'),
        })

    if old_primary.get('name') != new_primary.get('name'):
        changes.append({
            'field': 'primary.name',
            'old': old_primary.get('name'),
            'new': new_primary.get('name'),
        })

    if old_primary.get('type') != new_primary.get('type'):
        changes.append({
            'field': 'primary.type',
            'old': old_primary.get('type'),
            'new': new_primary.get('type'),
        })

    old_conf = round_conf(old_actual.get('confidence'))
    new_conf = round_conf(new_actual.get('confidence'))
    if old_conf != new_conf:
        delta = None if old_conf is None or new_conf is None else round(new_conf - old_conf, 4)
        if delta is None or abs(delta) >= confidence_threshold:
            changes.append({
                'field': 'confidence',
                'old': old_conf,
                'new': new_conf,
                'delta': delta,
            })

    if old_actual.get('requires_human_confirmation') != new_actual.get('requires_human_confirmation'):
        changes.append({
            'field': 'requires_human_confirmation',
            'old': old_actual.get('requires_human_confirmation'),
            'new': new_actual.get('requires_human_confirmation'),
        })

    if old_actual.get('can_auto_execute') != new_actual.get('can_auto_execute'):
        changes.append({
            'field': 'can_auto_execute',
            'old': old_actual.get('can_auto_execute'),
            'new': new_actual.get('can_auto_execute'),
        })

    old_reasons = old_actual.get('human_confirmation_reasons') or []
    new_reasons = new_actual.get('human_confirmation_reasons') or []
    if old_reasons != new_reasons:
        changes.append({
            'field': 'human_confirmation_reasons',
            'old': old_reasons,
            'new': new_reasons,
        })

    return changes


def build_diff(old_report, new_report, confidence_threshold=0.0):
    old_results = {item['id']: item for item in old_report.get('results', [])}
    new_results = {item['id']: item for item in new_report.get('results', [])}

    old_ids = set(old_results)
    new_ids = set(new_results)

    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    common = sorted(old_ids & new_ids)

    changed = []
    unchanged = []
    for case_id in common:
        field_changes = compare_case(old_results[case_id], new_results[case_id], confidence_threshold=confidence_threshold)
        record = {
            'id': case_id,
            'input': new_results[case_id].get('input') or old_results[case_id].get('input'),
            'changes': field_changes,
        }
        if field_changes:
            changed.append(record)
        else:
            unchanged.append(record)

    old_failed = old_report.get('failed')
    new_failed = new_report.get('failed')

    return {
        'old_report': {
            'selected_preset': old_report.get('selected_preset'),
            'selected_tags': old_report.get('selected_tags'),
            'selected_case_ids': old_report.get('selected_case_ids'),
            'total': old_report.get('total'),
            'passed': old_report.get('passed'),
            'failed': old_failed,
        },
        'new_report': {
            'selected_preset': new_report.get('selected_preset'),
            'selected_tags': new_report.get('selected_tags'),
            'selected_case_ids': new_report.get('selected_case_ids'),
            'total': new_report.get('total'),
            'passed': new_report.get('passed'),
            'failed': new_failed,
        },
        'summary': {
            'added_cases': len(added),
            'removed_cases': len(removed),
            'changed_cases': len(changed),
            'unchanged_cases': len(unchanged),
            'failed_count_changed': old_failed != new_failed,
        },
        'added_case_ids': added,
        'removed_case_ids': removed,
        'changed_cases': changed,
        'unchanged_case_ids': [item['id'] for item in unchanged],
    }


def format_text(diff):
    old_report = diff['old_report']
    new_report = diff['new_report']
    summary = diff['summary']

    lines = [
        'Router report diff summary:',
        f"- old: total={old_report['total']} passed={old_report['passed']} failed={old_report['failed']} preset={old_report['selected_preset']}",
        f"- new: total={new_report['total']} passed={new_report['passed']} failed={new_report['failed']} preset={new_report['selected_preset']}",
        f"- added_cases={summary['added_cases']} removed_cases={summary['removed_cases']} changed_cases={summary['changed_cases']} unchanged_cases={summary['unchanged_cases']}",
    ]

    if diff['added_case_ids']:
        lines.append('- added_case_ids: ' + ', '.join(diff['added_case_ids']))
    if diff['removed_case_ids']:
        lines.append('- removed_case_ids: ' + ', '.join(diff['removed_case_ids']))

    if diff['changed_cases']:
        lines.append('Changed cases:')
        for case in diff['changed_cases']:
            lines.append(f"- {case['id']}")
            for change in case['changes']:
                delta = ''
                if 'delta' in change and change['delta'] is not None:
                    delta = f" (delta={change['delta']:+.4f})"
                lines.append(f"  - {change['field']}: {change.get('old')!r} -> {change.get('new')!r}{delta}")
    else:
        lines.append('Changed cases: none')

    return '\n'.join(lines)


def write_output(path_str, content):
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(description='Diff two router evaluation JSON reports.')
    parser.add_argument('old_report', help='Path to the baseline router-eval.json report.')
    parser.add_argument('new_report', help='Path to the current router-eval.json report.')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Console output format.')
    parser.add_argument('--output', help='Optional file path to write the diff report.')
    parser.add_argument('--output-format', choices=['json', 'text', 'match-console'], default='match-console', help='Output file format.')
    parser.add_argument('--confidence-threshold', type=float, default=0.0, help='Ignore confidence deltas smaller than this absolute value.')
    parser.add_argument('--fail-on-change', action='store_true', help='Exit non-zero if any case changed, was added, or was removed.')
    return parser.parse_args()


def main():
    args = parse_args()
    old_report = load_report(args.old_report)
    new_report = load_report(args.new_report)
    diff = build_diff(old_report, new_report, confidence_threshold=args.confidence_threshold)

    text_output = format_text(diff)
    json_output = json.dumps(diff, ensure_ascii=False, indent=2)

    if args.format == 'json':
        console_output = json_output
    else:
        console_output = text_output
    print(console_output)

    if args.output:
        output_format = args.output_format
        if output_format == 'match-console':
            output_format = args.format
        file_content = json_output if output_format == 'json' else text_output
        write_output(args.output, file_content)

    has_change = bool(diff['added_case_ids'] or diff['removed_case_ids'] or diff['changed_cases'])
    if args.fail_on_change and has_change:
        sys.exit(1)


if __name__ == '__main__':
    main()
