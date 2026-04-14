#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / 'config' / 'runtime-host.json'
SCHEMA_VERSION = '1.0.0'


def load_config(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def build_invocation_payload(result):
    dispatch = result.get('dispatch') or {}
    adapter = dispatch.get('adapter') or {}
    target = dispatch.get('target') or {}
    task_payload = dispatch.get('task_payload') or {}

    return {
        'adapter_type': adapter.get('adapter_type'),
        'dispatch_mode': adapter.get('dispatch_mode'),
        'command': adapter.get('command'),
        'tool_family': adapter.get('tool_family'),
        'target_name': target.get('name'),
        'target_type': target.get('type'),
        'task_payload': task_payload,
        'command_preview': dispatch.get('command_preview'),
    }


def validate_for_host(result):
    dispatch = result.get('dispatch') or {}
    status = dispatch.get('dispatch_status')
    if status != 'ready_for_auto_dispatch':
        return False, {
            'accepted': False,
            'host_status': 'rejected_by_policy',
            'details': f'Dispatch status {status!r} is not auto-dispatchable.',
        }
    adapter = dispatch.get('adapter') or {}
    if not adapter.get('adapter_type'):
        return False, {
            'accepted': False,
            'host_status': 'rejected_missing_adapter',
            'details': 'Dispatch payload does not include a valid adapter_type.',
        }
    return True, None


def maybe_run_template(handler, invocation_payload, allow_shell_execute=False, timeout=30):
    template = handler.get('command_template')
    if not allow_shell_execute:
        return {
            'executed': False,
            'execution_mode': 'host_dispatch_only',
            'details': 'Shell execution disabled. Host accepted and normalized the invocation.',
        }
    if not handler.get('supports_shell_execution'):
        return {
            'executed': False,
            'execution_mode': 'host_dispatch_only',
            'details': 'Handler does not allow shell execution.',
        }
    if not template:
        return {
            'executed': False,
            'execution_mode': 'host_dispatch_only',
            'details': 'No command_template configured for this handler.',
        }

    replacements = {
        '{command}': invocation_payload.get('command') or '',
        '{tool_family}': invocation_payload.get('tool_family') or '',
        '{target_name}': invocation_payload.get('target_name') or '',
        '{text}': invocation_payload.get('task_payload', {}).get('text') or '',
        '{command_preview}': invocation_payload.get('command_preview') or '',
    }
    shell_command = template
    for old, new in replacements.items():
        shell_command = shell_command.replace(old, shlex.quote(str(new)))

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
            'execution_mode': 'shell_command',
            'details': {
                'returncode': completed.returncode,
                'stdout': completed.stdout,
                'stderr': completed.stderr,
                'shell_command': shell_command,
            },
        }
    except subprocess.TimeoutExpired:
        return {
            'executed': False,
            'execution_mode': 'shell_command_timeout',
            'details': f'Shell execution timed out after {timeout}s.',
        }


def dispatch_result(result, config, allow_shell_execute=False, timeout=None):
    ok, rejection = validate_for_host(result)
    if not ok:
        return rejection

    dispatch = result.get('dispatch') or {}
    adapter = dispatch.get('adapter') or {}
    adapter_type = adapter.get('adapter_type')
    handlers = config.get('handlers', {})
    handler = handlers.get(adapter_type)
    if not handler:
        return {
            'accepted': False,
            'host_status': 'rejected_missing_handler',
            'details': f'No handler configured for adapter_type={adapter_type!r}.',
        }

    invocation_payload = build_invocation_payload(result)
    timeout = timeout or config.get('default_timeout', 30)
    execution = maybe_run_template(
        handler,
        invocation_payload,
        allow_shell_execute=allow_shell_execute,
        timeout=timeout,
    )

    host_status_map = {
        'command_alias_host': 'host_dispatched_command_alias',
        'skill_name_host': 'host_dispatched_skill_name',
        'native_family_host': 'host_dispatched_native_family',
    }

    return {
        'accepted': True,
        'host_status': host_status_map.get(handler.get('handler_type'), 'host_dispatched'),
        'handler': handler,
        'invocation_payload': invocation_payload,
        'execution': execution,
    }


def format_text(payload):
    lines = []
    lines.append(f"Schema version: {payload.get('schema_version', SCHEMA_VERSION)}")
    lines.append(f"Accepted: {payload.get('accepted')}")
    lines.append(f"Host status: {payload.get('host_status')}")
    if payload.get('handler'):
        lines.append('Handler:')
        for key in ['handler_type', 'supports_shell_execution', 'command_template']:
            if key in payload['handler']:
                lines.append(f"- {key}: {payload['handler'][key]}")
    if payload.get('invocation_payload'):
        lines.append('Invocation payload:')
        for key, value in payload['invocation_payload'].items():
            lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value}")
    details = payload.get('execution') or payload.get('details')
    if details:
        lines.append('Execution / details:')
        if isinstance(details, dict):
            lines.append(json.dumps(details, ensure_ascii=False))
        else:
            lines.append(str(details))
    return '\n'.join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description='Local runtime host for routed task dispatch.')
    parser.add_argument('--input', help='Path to a JSON file containing the execute_routed_task payload.')
    parser.add_argument('--config', default=str(CONFIG), help='Path to runtime host config.')
    parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format.')
    parser.add_argument('--allow-shell-execute', action='store_true', help='Allow handler shell execution when configured.')
    parser.add_argument('--timeout', type=int, default=0, help='Override host timeout in seconds.')
    parser.add_argument('--output', help='Optional file path to write host result.')
    parser.add_argument('--output-format', choices=['json', 'text', 'match-console'], default='match-console', help='Output file format.')
    return parser.parse_args()


def write_output(path_str, content):
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def main():
    args = parse_args()
    if args.input:
        raw = Path(args.input).read_text(encoding='utf-8')
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        print('runtime_host.py expects JSON input via --input or stdin.', file=sys.stderr)
        sys.exit(1)

    result = json.loads(raw)
    config = load_config(args.config)
    host_result = dispatch_result(
        result,
        config,
        allow_shell_execute=args.allow_shell_execute,
        timeout=args.timeout or None,
    )
    payload = {
        'schema_version': SCHEMA_VERSION,
        **host_result,
    }
    json_output = json.dumps(payload, ensure_ascii=False, indent=2)
    text_output = format_text(payload)
    print(text_output if args.format == 'text' else json_output)

    if args.output:
        output_format = args.output_format
        if output_format == 'match-console':
            output_format = args.format
        write_output(args.output, json_output if output_format == 'json' else text_output)


if __name__ == '__main__':
    main()
