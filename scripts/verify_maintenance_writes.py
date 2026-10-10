#!/usr/bin/env python3
"""Role-specific maintenance write acceptance, exclusively through Loom MCP.

Preparation only unless --run is supplied. Requires ZP_RUNTIME_DIR, ZP_LOOM_DIR,
and optionally ZP_LOOM_CONFIG (defaults to the private runtime's loom.json).
Each role bridge uses a synthetic-user token, fresh client token and temporary TLS
identity. Never retry a mutation: read root state after any failure, record it,
and stop on transport/ambiguous outcome. Private working directories are retained.
"""
import argparse
import contextlib
import datetime
import json
import os
import pathlib
import re
import secrets
import socket
import subprocess
import time
import urllib.error
from loom_mcp import Loom

PORT = 18461
ROLES = {role + '.1': role for role in ['zp_property_manager', 'zp_tenant', 'zp_vendor']}


def private_json(path, value):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def tool(lo, name):
    matches = [entry['name'] for entry in lo.tools if entry['name'] == name or entry['name'].startswith('loom_native_' + name + '_')]
    if len(matches) != 1:
        raise RuntimeError('required MCP tool unavailable or ambiguous: ' + name)
    return matches[0]


def unwrap(value):
    for _ in range(3):
        if isinstance(value, dict) and 'data' in value:
            value = value['data']
        else:
            break
    return value


def record(lo, resource, identifier):
    value = unwrap(lo.call(tool(lo, 'resource_get'), {'resource': resource, 'filterByTk': identifier}))
    if not isinstance(value, dict) or str(value.get('id')) != str(identifier):
        raise RuntimeError('native readback did not return expected record')
    return value


def safe_error(error):
    message = str(error)
    code = re.search(r'ZP_MAINTENANCE_[A-Z_]+', message)
    if code:
        return code.group(0)
    if 'outcome-unknown' in message:
        return 'outcome-unknown'
    if any(word in message.lower() for word in ['unavailable:', 'invalid-response:', 'deadline', 'timeout', 'catalog changed']):
        return 'transport-unknown'
    if isinstance(error, (urllib.error.URLError, TimeoutError, ConnectionError)):
        return 'transport-unknown'
    return 'MCP-rejected'


def signin(root, account):
    # Live schema qualification is required; no guessed credential argument names.
    name = tool(root, 'auth_sign_in')
    schema = next(entry['inputSchema'] for entry in root.tools if entry['name'] == name)
    properties = schema.get('properties', {})
    if 'requestBody' not in properties:
        raise RuntimeError('auth_sign_in requestBody schema not qualified')
    body_properties = properties['requestBody'].get('properties', {})
    if not {'email', 'password'} <= set(body_properties):
        raise RuntimeError('auth_sign_in credential fields not qualified')
    value = unwrap(root.call(name, {'X-Authenticator': 'basic', 'requestBody': {'email': account['email'], 'password': account['password']}}))
    if not isinstance(value, dict) or not isinstance(value.get('token'), str) or len(value['token']) < 32:
        raise RuntimeError('synthetic sign-in did not return qualified token')
    return value['token']


@contextlib.contextmanager
def role_bridge(root, runtime, loom_dir, source_config, actor, account, run_dir):
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', PORT))
    directory = run_dir / actor
    directory.mkdir(mode=0o700)
    token = signin(root, account)
    cert = directory / 'tls-cert.pem'
    key = directory / 'tls-key.pem'
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', str(key), '-out', str(cert), '-days', '1', '-subj', '/CN=localhost', '-addext', 'subjectAltName=DNS:localhost,IP:127.0.0.1'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    key.chmod(0o600)
    cfg = {name: source_config[name] for name in ['backendURL', 'allowInsecureLoopback', 'limits'] if name in source_config}
    cfg.update({'read': {'enabled': False}, 'listenHost': '127.0.0.1', 'port': PORT, 'allowedHosts': ['localhost:' + str(PORT)], 'nativeMcp': {**source_config['nativeMcp'], 'enabled': True, 'role': ROLES[actor], 'catalogPath': str(directory / 'catalog.json'), 'maxConcurrent': 1}})
    private_json(directory / 'loom.json', cfg)
    env = {name: value for name, value in os.environ.items() if not name.startswith('LOOM_')}
    env.update({'LOOM_NATIVE_BACKEND_TOKEN': token, 'LOOM_NATIVE_CLIENT_TOKEN': secrets.token_hex(32), 'LOOM_TLS_CERT_FILE': str(cert), 'LOOM_TLS_KEY_FILE': str(key)})
    descriptor = os.open(directory / 'native-client-token', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        stream.write(env['LOOM_NATIVE_CLIENT_TOKEN'] + '\n')
    # Capturing the actual role catalog uses Loom's existing capability qualification.
    completed = subprocess.run(['node', str(loom_dir / 'scripts/capture-native-catalog.mjs'), str(directory / 'loom.json')], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
    if completed.returncode:
        raise RuntimeError('role catalog capture failed; credentials and raw errors withheld')
    with (directory / 'server.log').open('xb') as log:
        os.chmod(directory / 'server.log', 0o600)
        child = subprocess.Popen(['node', str(loom_dir / 'src/cli.js'), str(directory / 'loom.json')], env=env, stdout=log, stderr=log)
        try:
            ready = False
            for _ in range(40):
                if child.poll() is not None:
                    raise RuntimeError('role bridge stopped before ready')
                try:
                    bridge = Loom(str(directory))
                    ready = True
                    break
                except (urllib.error.URLError, ConnectionError, TimeoutError):
                    time.sleep(.25)
            if not ready:
                raise RuntimeError('role bridge startup deadline exceeded')
            effective = unwrap(bridge.call(tool(bridge, 'roles_check')))
            if not isinstance(effective, dict) or effective.get('role') != ROLES[actor] or effective.get('allowAll') is not False:
                raise RuntimeError('role bridge effective role differs or has unrestricted authority')
            bridge.verified_role = {'requestedRole': ROLES[actor], 'effectiveRole': effective['role'], 'allowAll': effective['allowAll']}
            yield bridge
        finally:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)


def write_case(root, bridge, report, name, identifier, values, allowed):
    update_tool = tool(bridge, 'resource_update')
    before = record(root, 'zp_work_orders', identifier)
    error = None
    try:
        bridge.call(update_tool, {'resource': 'zp_work_orders', 'filterByTk': identifier, 'values': values})
    except Exception as failure:
        error = safe_error(failure)
    # Always reconcile through a separate root read; no mutation replay.
    after = record(root, 'zp_work_orders', identifier)
    changed = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    if allowed:
        passed = error is None and bool(changed & set(values)) and all((str(after.get(key)) == str(value) if key.endswith('Id') else after.get(key) == value) for key, value in values.items())
    else:
        passed = not changed
    report.append({'case': name, 'passed': passed, 'error': error, 'role': bridge.verified_role, 'changedFields': sorted(changed), 'expectedAllowed': allowed, 'stateBefore': before.get('state'), 'stateAfter': after.get('state')})
    if error in ('outcome-unknown', 'transport-unknown'):
        raise RuntimeError('uncertain write reconciled; stop without retry')
    if not passed:
        raise RuntimeError('write acceptance failed: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        print(json.dumps({'status': 'prepared-not-executed', 'actors': list(ROLES), 'port': PORT, 'ledger': 'not-tested; absence is not permission evidence'}))
        return
    runtime = pathlib.Path(os.environ['ZP_RUNTIME_DIR']).resolve()
    loom_dir = pathlib.Path(os.environ['ZP_LOOM_DIR']).resolve()
    source_config = json.loads(pathlib.Path(os.environ.get('ZP_LOOM_CONFIG', runtime / 'loom.json')).read_text())
    accounts = json.loads((runtime / 'maintenance-test-accounts.json').read_text())
    identifiers = json.loads((runtime / 'maintenance-fixture-ids.json').read_text())
    root = Loom(str(runtime))
    run_dir = runtime / 'role-bridges' / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + secrets.token_hex(3))
    run_dir.mkdir(parents=True, mode=0o700)
    report = {'evidence': 'live-role-specific-Loom-MCP', 'cases': [], 'ledger': 'not-tested; absence is not permission evidence', 'status': 'running'}
    try:
        first = identifiers['1']['zp_work_orders']
        second = identifiers['2']['zp_work_orders']
        initial = record(root, 'zp_work_orders', first)
        if initial.get('state') != 'new':
            raise RuntimeError('manager acceptance requires prequalified New baseline; no automatic reset')
        for actor in ROLES:
            with role_bridge(root, runtime, loom_dir, source_config, actor, accounts[actor], run_dir) as bridge:
                if actor == 'zp_property_manager.1':
                    write_case(root, bridge, report['cases'], 'manager-own-assignment', first, {'vendorId': identifiers['1']['zp_vendors'], 'state': 'quote'}, True)
                    write_case(root, bridge, report['cases'], 'manager-other-property-denied', second, {'state': 'quote', 'vendorId': identifiers['2']['zp_vendors']}, False)
                    write_case(root, bridge, report['cases'], 'manager-forged-approval-denied', first, {'approvalGranted': True}, False)
                else:
                    write_case(root, bridge, report['cases'], actor + '-workorder-update-denied', first, {'state': 'new'}, False)
        report['status'] = 'passed'
    except Exception as failure:
        report['status'] = 'failed-stop-no-retry'
        report['failureClass'] = safe_error(failure)
        raise RuntimeError('maintenance role write acceptance stopped; inspect sanitized receipt') from None
    finally:
        private_json(run_dir / 'write-acceptance.json', report)
        print(json.dumps(report))


if __name__ == '__main__':
    main()
