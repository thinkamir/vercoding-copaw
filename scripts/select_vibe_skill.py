#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / 'config' / 'vibe-routing.json'

NATIVE_HINTS = [
    ("browser", ["浏览器", "网页", "点击", "表单", "截图", "browser", "playwright"], "Prefer native CoPaw browser/browser_use skills."),
    ("github", ["github", "pr", "issue", "pull request", "仓库", "commit", "push"], "Prefer native CoPaw Github skill for direct GitHub operations."),
    ("web-search", ["搜索", "查一下", "最新", "新闻", "web", "search", "google", "duckduckgo"], "Prefer native CoPaw web-search/tavily/duckduckgo-search skills."),
    ("cron", ["定时", "cron", "每周", "每天", "提醒", "heartbeat"], "Prefer native CoPaw cron/heartbeat workflow."),
    ("code", ["写代码", "改代码", "修复", "debug", "测试", "重构", "实现"], "CoPaw native Code/Agentic Coding may also be appropriate depending on task scope.")
]


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


def native_recommendation(text):
    text_l = text.lower()
    matched = []
    for name, words, reason in NATIVE_HINTS:
        hits = [w for w in words if w.lower() in text_l]
        if hits:
            matched.append({
                'native_skill_family': name,
                'matched_keywords': hits,
                'reason': reason,
                'score': len(hits)
            })
    matched.sort(key=lambda x: -x['score'])
    return matched


def build_payload(text, top_n):
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

    native = native_recommendation(text)
    top_vibe = deduped[:top_n]

    recommendation_mode = 'vibe'
    mode_reason = 'Matched one or more Vibe skills with positive routing score.'
    if native and (not top_vibe or native[0]['score'] >= 2 and (not top_vibe or top_vibe[0]['score'] < 100)):
        recommendation_mode = 'native_copaw_first'
        mode_reason = native[0]['reason']

    return {
        'input': text,
        'matched_intents': matched_intents,
        'recommendation_mode': recommendation_mode,
        'mode_reason': mode_reason,
        'recommended': [
            {
                'skill': r['skill'],
                'layer': r['layer'],
                'score': r['score'],
                'reasons': r['reasons']
            }
            for r in top_vibe
        ],
        'native_hints': native[:5],
        'excluded': excluded_payload[:10],
        'message': 'No direct Vibe skill match. Prefer standard CoPaw skill selection.' if not top_vibe else ''
    }


def format_text(payload):
    lines = []
    lines.append(f"Input: {payload['input']}")
    lines.append(f"Recommendation mode: {payload['recommendation_mode']}")
    lines.append(f"Reason: {payload['mode_reason']}")
    if payload['matched_intents']:
        lines.append("Matched intents:")
        for k, v in payload['matched_intents'].items():
            lines.append(f"- {k}: {', '.join(v)}")
    if payload['recommended']:
        lines.append("Recommended Vibe skills:")
        for i, item in enumerate(payload['recommended'], 1):
            lines.append(f"{i}. {item['skill']} [{item['layer']}] score={item['score']}")
            for reason in item['reasons']:
                lines.append(f"   - {reason}")
    else:
        lines.append("Recommended Vibe skills: none")
        if payload.get('message'):
            lines.append(f"- {payload['message']}")
    if payload['native_hints']:
        lines.append("Native CoPaw hints:")
        for item in payload['native_hints']:
            lines.append(f"- {item['native_skill_family']}: {', '.join(item['matched_keywords'])}")
            lines.append(f"  {item['reason']}")
    if payload['excluded']:
        lines.append("Excluded / suppressed:")
        for item in payload['excluded'][:5]:
            reason = '; '.join(item['reasons']) if item['reasons'] else 'score <= 0'
            lines.append(f"- {item['skill']}: {reason}")
    return '\n'.join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description='Recommend Vibe skills for a task text.')
    parser.add_argument('text', nargs='*', help='Task text. If omitted, stdin will be used.')
    parser.add_argument('--top', type=int, default=5, help='Number of top Vibe recommendations to return.')
    parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format.')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.text:
        text = ' '.join(args.text).strip()
    else:
        text = sys.stdin.read().strip()
    if not text:
        print('Usage: python3 scripts/select_vibe_skill.py [--format json|text] [--top N] "task text"', file=sys.stderr)
        sys.exit(1)

    payload = build_payload(text, max(1, args.top))
    if args.format == 'text':
        print(format_text(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
