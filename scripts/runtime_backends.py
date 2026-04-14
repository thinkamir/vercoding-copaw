#!/usr/bin/env python3
import json
import shlex
import subprocess


def maybe_run_shell(command_template, replacements, allow_shell_execute=False, timeout=30, supports_shell_execution=False):
    if not allow_shell_execute:
        return {
            'executed': False,
            'execution_mode': 'backend_prepare_only',
            'details': 'Shell execution disabled. Backend prepared invocation only.',
        }
    if not supports_shell_execution:
        return {
            'executed': False,
            'execution_mode': 'backend_prepare_only',
            'details': 'Backend does not allow shell execution.',
        }
    if not command_template:
        return {
            'executed': False,
            'execution_mode': 'backend_prepare_only',
            'details': 'No command_template configured for this backend.',
        }

    shell_command = command_template
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


def handle_vibe_wrapper(invocation_payload, handler, allow_shell_execute=False, timeout=30):
    command = invocation_payload.get('command')
    text = invocation_payload.get('task_payload', {}).get('text')
    backend_payload = {
        'backend_family': 'vibe_wrapper',
        'dispatch_target': command,
        'arguments': [text],
        'command_line_preview': f'{command} "{text}"' if command and text else command,
    }
    execution = maybe_run_shell(
        handler.get('command_template'),
        {
            '{command}': command or '',
            '{text}': text or '',
            '{command_preview}': invocation_payload.get('command_preview') or '',
        },
        allow_shell_execute=allow_shell_execute,
        timeout=timeout,
        supports_shell_execution=handler.get('supports_shell_execution', False),
    )
    return {
        'backend_status': 'backend_prepared_vibe_wrapper',
        'backend_payload': backend_payload,
        'execution': execution,
    }


def handle_vibe_skill(invocation_payload, handler, allow_shell_execute=False, timeout=30):
    target_name = invocation_payload.get('target_name')
    text = invocation_payload.get('task_payload', {}).get('text')
    backend_payload = {
        'backend_family': 'vibe_skill',
        'skill_name': target_name,
        'input_text': text,
        'dispatch_contract': {
            'skill': target_name,
            'text': text,
        },
    }
    execution = maybe_run_shell(
        handler.get('command_template'),
        {
            '{target_name}': target_name or '',
            '{text}': text or '',
            '{command_preview}': invocation_payload.get('command_preview') or '',
        },
        allow_shell_execute=allow_shell_execute,
        timeout=timeout,
        supports_shell_execution=handler.get('supports_shell_execution', False),
    )
    return {
        'backend_status': 'backend_prepared_vibe_skill',
        'backend_payload': backend_payload,
        'execution': execution,
    }


def handle_native_family(invocation_payload, handler, allow_shell_execute=False, timeout=30):
    target_name = invocation_payload.get('target_name')
    text = invocation_payload.get('task_payload', {}).get('text')

    family_payload = {
        'browser': {
            'backend_status': 'backend_prepared_browser',
            'backend_payload': {
                'backend_family': 'browser',
                'recommended_tools': ['browser', 'browser_use'],
                'action_hint': 'open_or_navigate_then_snapshot_or_click',
                'text': text,
            },
        },
        'github': {
            'backend_status': 'backend_prepared_github',
            'backend_payload': {
                'backend_family': 'github',
                'recommended_tools': ['github'],
                'action_hint': 'gh_cli_or_github_skill_dispatch',
                'text': text,
            },
        },
        'web-search': {
            'backend_status': 'backend_prepared_web_search',
            'backend_payload': {
                'backend_family': 'web-search',
                'recommended_tools': ['web-search', 'tavily', 'duckduckgo-search'],
                'action_hint': 'search_then_summarize',
                'text': text,
            },
        },
        'cron': {
            'backend_status': 'backend_prepared_cron',
            'backend_payload': {
                'backend_family': 'cron',
                'recommended_tools': ['cron'],
                'action_hint': 'schedule_or_manage_periodic_task',
                'text': text,
            },
        },
        'code': {
            'backend_status': 'backend_prepared_code',
            'backend_payload': {
                'backend_family': 'code',
                'recommended_tools': ['Code', 'Agentic Coding'],
                'action_hint': 'plan_implement_verify_loop',
                'text': text,
            },
        },
    }

    selected = family_payload.get(target_name, {
        'backend_status': 'backend_prepared_native_generic',
        'backend_payload': {
            'backend_family': 'native-generic',
            'recommended_tools': [invocation_payload.get('tool_family')],
            'action_hint': 'generic_native_dispatch',
            'text': text,
        },
    })

    execution = maybe_run_shell(
        handler.get('command_template'),
        {
            '{tool_family}': invocation_payload.get('tool_family') or '',
            '{target_name}': target_name or '',
            '{text}': text or '',
            '{command_preview}': invocation_payload.get('command_preview') or '',
        },
        allow_shell_execute=allow_shell_execute,
        timeout=timeout,
        supports_shell_execution=handler.get('supports_shell_execution', False),
    )

    selected['execution'] = execution
    return selected


def dispatch_backend(invocation_payload, handler, allow_shell_execute=False, timeout=30):
    adapter_type = invocation_payload.get('adapter_type')
    if adapter_type == 'vibe_wrapper':
        return handle_vibe_wrapper(invocation_payload, handler, allow_shell_execute=allow_shell_execute, timeout=timeout)
    if adapter_type == 'vibe_skill':
        return handle_vibe_skill(invocation_payload, handler, allow_shell_execute=allow_shell_execute, timeout=timeout)
    if adapter_type == 'native_copaw':
        return handle_native_family(invocation_payload, handler, allow_shell_execute=allow_shell_execute, timeout=timeout)
    return {
        'backend_status': 'backend_unknown_adapter_type',
        'backend_payload': {
            'adapter_type': adapter_type,
            'invocation_payload': invocation_payload,
        },
        'execution': {
            'executed': False,
            'execution_mode': 'backend_prepare_only',
            'details': 'Unknown adapter type. No backend handler dispatched.',
        },
    }
