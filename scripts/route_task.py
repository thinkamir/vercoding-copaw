#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / 'scripts'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from select_vibe_skill import build_payload  # noqa: E402


MODE_TEMPLATES = {
    'vibe': {
        'summary': 'Task is suitable for Vibe-routed execution.',
        'next_action': 'Start with the top-ranked Vibe skill or wrapper command.',
    },
    'native_copaw_first': {
        'summary': 'Task is better handled by a native CoPaw skill first.',
        'next_action': 'Prefer the top native skill family, then optionally use Vibe for governed execution layers.',
    },
}


def build_route(text, top_n):
    payload = build_payload(text, top_n)
    recommended = payload.get('recommended', [])
    native_hints = payload.get('native_hints', [])
    mode = payload.get('recommendation_mode', 'vibe')

    primary = None
    if mode == 'native_copaw_first' and native_hints:
        hint = native_hints[0]
        primary = {
            'type': 'native_copaw',
            'name': hint['native_skill_family'],
            'reason': hint['reason'],
            'matched_keywords': hint['matched_keywords'],
        }
    elif recommended:
        top = recommended[0]
        primary = {
            'type': 'vibe',
            'name': top['skill'],
            'layer': top['layer'],
            'score': top['score'],
            'reason': '; '.join(top['reasons']) if top['reasons'] else payload.get('mode_reason', ''),
        }

    fallbacks = []
    if mode == 'native_copaw_first':
        for item in native_hints[1:3]:
            fallbacks.append({
                'type': 'native_copaw',
                'name': item['native_skill_family'],
                'reason': item['reason'],
            })
        for item in recommended[:2]:
            fallbacks.append({
                'type': 'vibe',
                'name': item['skill'],
                'reason': '; '.join(item['reasons']) if item['reasons'] else '',
            })
    else:
        for item in recommended[1:4]:
            fallbacks.append({
                'type': 'vibe',
                'name': item['skill'],
                'reason': '; '.join(item['reasons']) if item['reasons'] else '',
            })
        for item in native_hints[:2]:
            fallbacks.append({
                'type': 'native_copaw',
                'name': item['native_skill_family'],
                'reason': item['reason'],
            })

    invocation = suggest_invocation(primary, text)

    return {
        'input': text,
        'route_mode': mode,
        'mode_summary': MODE_TEMPLATES.get(mode, {}).get('summary', payload.get('mode_reason', '')),
        'mode_reason': payload.get('mode_reason', ''),
        'next_action': MODE_TEMPLATES.get(mode, {}).get('next_action', ''),
        'primary': primary,
        'invocation': invocation,
        'fallbacks': fallbacks[:5],
        'router_evidence': {
            'matched_intents': payload.get('matched_intents', {}),
            'recommended': recommended,
            'native_hints': native_hints,
            'excluded': payload.get('excluded', []),
        },
    }


def suggest_invocation(primary, text):
    if not primary:
        return {
            'style': 'manual_review',
            'command': None,
            'notes': ['No confident route. Review task manually or use normal CoPaw routing.']
        }

    if primary['type'] == 'vibe':
        skill_name = primary['name']
        wrapper_map = {
            'Vibe Command - vibe': '/vibe',
            'Vibe Command - vibe-do-it': 'vibe-do-it',
            'Vibe Command - vibe-how-do-we-do': 'vibe-how-do-we-do',
            'Vibe Command - vibe-implement': 'vibe-implement',
            'Vibe Command - vibe-review': 'vibe-review',
            'Vibe Command - vibe-what-do-i-want': 'vibe-what-do-i-want',
        }
        command = wrapper_map.get(skill_name)
        notes = []
        if command:
            notes.append(f'Invoke the mapped wrapper command: {command}')
        else:
            notes.append(f'Use skill directly: {skill_name}')
        notes.append('Pass the original task text into the selected workflow.')
        return {
            'style': 'vibe_skill',
            'command': command,
            'skill': skill_name,
            'task_text': text,
            'notes': notes,
        }

    return {
        'style': 'native_copaw',
        'command': None,
        'skill_family': primary['name'],
        'task_text': text,
        'notes': [
            f"Route to native CoPaw skill family: {primary['name']}",
            'If execution becomes multi-stage/governed later, re-run through Vibe routing.',
        ],
    }


def format_text(route):
    lines = []
    lines.append(f"Input: {route['input']}")
    lines.append(f"Route mode: {route['route_mode']}")
    lines.append(f"Mode summary: {route['mode_summary']}")
    lines.append(f"Reason: {route['mode_reason']}")
    lines.append(f"Next action: {route['next_action']}")
    lines.append('Primary route:')
    if route['primary']:
        primary = route['primary']
        lines.append(f"- type: {primary['type']}")
        lines.append(f"- name: {primary['name']}")
        if primary.get('reason'):
            lines.append(f"- reason: {primary['reason']}")
    else:
        lines.append('- none')
    lines.append('Invocation:')
    inv = route['invocation']
    for key in ['style', 'command', 'skill', 'skill_family', 'task_text']:
        if inv.get(key) is not None:
            lines.append(f"- {key}: {inv.get(key)}")
    if inv.get('notes'):
        for note in inv['notes']:
            lines.append(f"  - {note}")
    if route['fallbacks']:
        lines.append('Fallbacks:')
        for item in route['fallbacks']:
            lines.append(f"- [{item['type']}] {item['name']}: {item['reason']}")
    evidence = route.get('router_evidence', {})
    if evidence.get('matched_intents'):
        lines.append('Matched intents:')
        for k, v in evidence['matched_intents'].items():
            lines.append(f"- {k}: {', '.join(v)}")
    return '\n'.join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description='Task pre-router for Vibe vs native CoPaw execution.')
    parser.add_argument('text', nargs='*', help='Task text. If omitted, stdin will be used.')
    parser.add_argument('--top', type=int, default=5, help='Number of top Vibe recommendations to inspect.')
    parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format.')
    return parser.parse_args()


def main():
    args = parse_args()
    text = ' '.join(args.text).strip() if args.text else sys.stdin.read().strip()
    if not text:
        print('Usage: python3 scripts/route_task.py [--format json|text] [--top N] "task text"', file=sys.stderr)
        sys.exit(1)

    route = build_route(text, max(1, args.top))
    if args.format == 'text':
        print(format_text(route))
    else:
        print(json.dumps(route, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
