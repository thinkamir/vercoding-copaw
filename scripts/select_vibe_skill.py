#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / 'config' / 'vibe-routing.json'


def load_config():
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def score_text(text, items):
    text_l = text.lower()
    scores = []
    for item in items:
        score = 0
        for kw in item.get('keywords', []):
            if kw.lower() in text_l:
                score += item.get('priority', 0)
        if score > 0:
            scores.append({
                'skill': item['skill'],
                'score': score,
                'matched_keywords': [kw for kw in item.get('keywords', []) if kw.lower() in text_l]
            })
    return scores


def apply_dedup(results, dedup):
    by_skill = {r['skill']: r for r in results}
    removed = set()
    for pair in dedup.get('pairs', []):
        a = pair['prefer']
        b = pair['avoid_with']
        if a in by_skill and b in by_skill:
            if by_skill[a]['score'] >= by_skill[b]['score']:
                removed.add(b)
            else:
                removed.add(a)
    return [r for r in results if r['skill'] not in removed]


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/select_vibe_skill.py "task text"')
        sys.exit(1)

    text = ' '.join(sys.argv[1:])
    config = load_config()
    all_items = []
    for layer_items in config['layers'].values():
        all_items.extend(layer_items)

    results = score_text(text, all_items)
    results = apply_dedup(results, config.get('dedup', {}))
    results.sort(key=lambda x: (-x['score'], x['skill']))

    if not results:
        print(json.dumps({
            'input': text,
            'recommended': [],
            'message': 'No direct Vibe skill match. Prefer standard CoPaw skill selection.'
        }, ensure_ascii=False, indent=2))
        return

    print(json.dumps({
        'input': text,
        'recommended': results[:5]
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
