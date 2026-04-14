#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / 'scripts'
CONFIG = ROOT / 'config' / 'execution-adapters.json'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from route_task import build_route  # noqa: E402

SCHEMA_VERSION = '1.0.0'


def load_adapters(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def get_adapter(route, adapters):
    primary = route.get('primary') or {}
    if not primary:
        return None
    if primary.get('type') == 'vibe':
        return adapters.get('vibe_wrappers', {}).get(primary.get('name'))
    if primary.get('type') == 'native_copaw':
        return adapters.get('native_families', {}).get(primary.get('name'))
    return None


def build_dispatch(route, adapter):
    primary = route.get('primary') or {}
    invocation = route.get('invocation') or {}

    if not primary:
        return {
            'dispatch_status': 'manual_review_required',
            'dispatch_reason': 'No primary route selected.',
            'adapter': None,
            'target': None,
            'command_preview': None,
            'task_payload': {'text': route.get('input')},
        }

    if route.get('requires_human_confirmation'):
        return {
            'dispatch_status': 'blocked_confirmation',
            'dispatch_reason': 'Human confirmation is required before execution.',
            'adapter': adapter,
            'target': primary,
            'command_preview': invocation.get('command'),
            'task_payload': {'text': route.get('input')},
        }

    if not route.get('can_auto_execute'):
        return {
            'dispatch_status': 'manual_handoff',
            'dispatch_reason': 'Route exists but auto execution is disabled by confidence or policy gate.',
            'adapter': adapter,
            'target': primary,
            'command_preview': invocation.get('command'),
            'task_payload': {'text': route.get('input')},
        }

    if not adapter:
        return {
            'dispatch_status': 'adapter_missing',
            'dispatch_reason': 'No execution adapter configured for the selected route.',
            'adapter': None,
            'target': primary,
            'command_preview': invocation.get('command'),
            'task_payload': {'text': route.get('input')},
        }

    command_preview = None
    if adapter.get('dispatch_mode') == 'command_alias':
        command_preview = f"{adapter.get('command')} \"{route.get('input')}\""
    elif adapter.get('dispatch_mode') == 'skill_name':
        command_preview = f"skill:{primary.get('name')}"
    elif adapter.get('dispatch_mode') == 'skill_family':
        command_preview = f"native:{primary.get('name')}"

    status = 'ready_for_dispatch'
    if adapter.get('supports_auto_dispatch'):
        status = 'ready_for_auto_dispatch'

    return {
        'dispatch_status': status,
        'dispatch_reason': 'Adapter and policy gates allow dispatch.',
        'adapter': adapter,
        'target': primary,
        'command_preview': command_preview,
        'task_payload': {
            'text': route.get('input'),
            'route_mode': route.get('route_mode'),
            'confidence': route.get('confidence'),
        },
    }


def maybe_execute(dispatch, shell_execute=False, timeout=30):
    status = dispatch.get('dispatch_status')
    adapter = dispatch.get('adapter') or {}

    if status != 'ready_for_auto_dispatch':
        return {
            'executed': False,
            'execution_status': 'not_executed',
            'details': 'Dispatch is not in auto-dispatchable state.',
        }

    if not shell_execute:
        return {
            'executed': True,
            'execution_status': 'dispatched_stub',
            'details': 'Auto-dispatch eligible. Returned a dispatch stub without invoking external runtime.',
        }

    shell_command = adapter.get('shell_command')
    if not shell_command:
        return {
            'executed': False,
            'execution_status': 'shell_command_missing',
            'details': 'shell_execute was requested but no shell_command is configured for this adapter.',
        }

    try:
        completed = subprocess.run(
            shell_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            'executed': completed.returncode == 0,
            'execution_status': 'shell_executed' if completed.returncode == 0 else 'shell_failed',
            'details': {
                'returncode': completed.returncode,
                'stdout': completed.stdout,
                'stderr': completed.stderr,
            },
        }
    except subprocess.TimeoutExpired:
        return {
            'executed': False,
            'execution_status': 'shell_timeout',
            'details': f'Shell execution timed out after {timeout}s.',
        }


def build_result(text, top_n, adapters, execute=False, shell_execute=False, timeout=30):
    route = build_route(text, top_n)
    adapter = get_adapter(route, adapters)
    dispatch = build_dispatch(route, adapter)
    execution = maybe_execute(dispatch, shell_execute=shell_execute, timeout=timeout) if execute else {
        'executed': False,
        'execution_status': 'preview_only',
        'details': 'Execution not requested. This is a preview of the dispatch chain.',
    }

    return {
        'schema_version': SCHEMA_VERSION,
        'input': text,
        'route': route,
        'dispatch': dispatch,
        'execution': execution,
    }


def format_text(result):
    route = result['route']
    dispatch = result['dispatch']
    execution = result['execution']

    lines = []
    lines.append(f"Schema version: {result['schema_version']}")
    lines.append(f"Input: {result['input']}")
    lines.append(f"Route mode: {route['route_mode']}")
    lines.append(f"Primary: {(route.get('primary') or {}).get('name')}")
    lines.append(f"Confidence: {route['confidence']}")
    lines.append(f"Can auto execute: {route['can_auto_execute']}")
    lines.append(f"Requires human confirmation: {route['requires_human_confirmation']}")
    if route.get('human_confirmation_reasons'):
        lines.append('Human confirmation reasons:')
        for reason in route['human_confirmation_reasons']:
            lines.append(f"- {reason}")
    lines.append(f"Dispatch status: {dispatch['dispatch_status']}")
    lines.append(f"Dispatch reason: {dispatch['dispatch_reason']}")
    lines.append(f"Command preview: {dispatch.get('command_preview')}")
    if dispatch.get('adapter'):
        lines.append('Adapter:')
        for key in ['adapter_type', 'dispatch_mode', 'command', 'tool_family', 'supports_auto_dispatch']:
            if key in dispatch['adapter']:
                lines.append(f"- {key}: {dispatch['adapter'][key]}")
    lines.append(f"Execution status: {execution['execution_status']}")
    lines.append(f"Executed: {execution['executed']}")
    details = execution.get('details')
    if isinstance(details, dict):
        lines.append(f"Execution details: {json.dumps(details, ensure_ascii=False)}")
    else:
        lines.append(f"Execution details: {details}")
    return '\n'.join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description='Route a task and convert it into a dispatchable execution payload.')
    parser.add_argument('text', nargs='*', help='Task text. If omitted, stdin will be used.')
    parser.add_argument('--top', type=int, default=5, help='Number of top Vibe recommendations to inspect.')
    parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format.')
    parser.add_argument('--adapters', default=str(CONFIG), help='Path to execution adapter config.')
    parser.add_argument('--execute', action='store_true', help='Attempt to execute the dispatch chain after routing.')
    parser.add_argument('--shell-execute', action='store_true', help='Actually run adapter shell_command if configured. Use with care.')
    parser.add_argument('--timeout', type=int, default=30, help='Shell execution timeout in seconds.')
    parser.add_argument('--output', help='Optional file path to write the final execution payload.')
    parser.add_argument('--output-format', choices=['json', 'text', 'match-console'], default='match-console', help='Output file format.')
    return parser.parse_args()


def write_output(path_str, content):
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def main():
    args = parse_args()
    text = ' '.join(args.text).strip() if args.text else sys.stdin.read().strip()
    if not text:
        print('Usage: python3 scripts/execute_routed_task.py [options] "task text"', file=sys.stderr)
        sys.exit(1)

    adapters = load_adapters(args.adapters)
    result = build_result(
        text,
        max(1, args.top),
        adapters,
        execute=args.execute,
        shell_execute=args.shell_execute,
        timeout=args.timeout,
    )

    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    text_output = format_text(result)
    console_output = text_output if args.format == 'text' else json_output
    print(console_output)

    if args.output:
        output_format = args.output_format
        if output_format == 'match-console':
            output_format = args.format
        write_output(args.output, json_output if output_format == 'json' else text_output)


if __name__ == '__main__':
    main()
