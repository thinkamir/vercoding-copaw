#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / 'config' / 'vibe-routing.json'


def load_config():
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def collect_alias_intents(text, aliases):
    text_l = text.lower()
    matched = {}
    for intent, words in aliases.items():
        hits = [w for w in words if w.lower() in text_l]
        if hits:
            matched[intent] = hits
    return matched


def score_item(text, item, matched_intents):
    text_l = text.lower()
    base_priority = item.get('priority', 0)
    matched_keywords = [kw for kw in item.get('keywords', []) if kw.lower() in text_l]
    negative_hits = [kw for kw in item.get('negative_keywords', []) if kw.lower() in text_l]
    matched_boosts = [intent for intent in item.get('intent_boosts', []) if intent in matched_intents]

    score = len(matched_keywords) * base_priority
    score += len(matched_boosts) * max(10, base_priority // 5)
    score -= len(negative_hits) * max(15, base_priority // 4)

    return {
        'skill': item['skill'],
        'score': score,
        'matched_keywords': matched_keywords,
        'negative_hits': negative_hits,
        'matched_intents': {k: matched_intents[k] for k in matched_boosts},
        'excluded': score <= 0,
    }


def apply_dedup(results, dedup):
    by_skill = {r['skill']: r for r in results}
    removed = {}
    for pair in dedup.get('pairs', []):
        a = pair['prefer']
        b = pair['avoid_with']
        if a in by_skill and b in by_skill and not by_skill[a]['excluded'] and not by_skill[b]['excluded']:
            if by_skill[a]['score'] >= by_skill[b]['score']:
                removed[b] = f"Removed by dedup rule: prefer {a} over {b} ({pair['rule']})"
            else:
                removed[a] = f"Removed by dedup rule: prefer {b} over {a} ({pair['rule']})"
    kept = [r for r in results if r['skill'] not in removed]
    return kept, removed


def explain(result):
    reasons = []
    if result['matched_keywords']:
        reasons.append(f"关键词命中: {', '.join(result['matched_keywords'])}")
    if result['matched_intents']:
        parts = []
        for intent, hits in result['matched_intents'].items():
            parts.append(f"{intent} <- {', '.join(hits)}")
        reasons.append("意图加权: " + '; '.join(parts))
    if result['negative_hits']:
        reasons.append(f"负向命中: {', '.join(result['negative_hits'])}")
    return reasons


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/select_vibe_skill.py "task text"')
        sys.exit(1)

    text = ' '.join(sys.argv[1:])
    config = load_config()
    matched_intents = collect_alias_intents(text, config.get('aliases', {}))

    all_items = []
    for layer_name, layer_items in config['layers'].items():
        for item in layer_items:
            item = dict(item)
            item['_layer'] = layer_name
            all_items.append(item)

    raw_results = []
    excluded = []
    for item in all_items:
        result = score_item(text, item, matched_intents)
        result['layer'] = item['_layer']
        result['reasons'] = explain(result)
        if result['excluded']:
            excluded.append(result)
        else:
            raw_results.append(result)

    deduped, removed = apply_dedup(raw_results, config.get('dedup', {}))
    deduped.sort(key=lambda x: (-x['score'], x['skill']))

    excluded_payload = []
    for r in excluded:
        excluded_payload.append({
            'skill': r['skill'],
            'reasons': r['reasons'],
            'score': r['score']
        })
    for skill, reason in removed.items():
        excluded_payload.append({
            'skill': skill,
            'reasons': [reason],
            'score': None
        })

    if not deduped:
        print(json.dumps({
            'input': text,
            'matched_intents': matched_intents,
            'recommended': [],
            'excluded': excluded_payload,
            'message': 'No direct Vibe skill match. Prefer standard CoPaw skill selection.'
        }, ensure_ascii=False, indent=2))
        return

    print(json.dumps({
        'input': text,
        'matched_intents': matched_intents,
        'recommended': [
            {
                'skill': r['skill'],
                'layer': r['layer'],
                'score': r['score'],
                'reasons': r['reasons']
            }
            for r in deduped[:5]
        ],
        'excluded': excluded_payload[:10]
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
