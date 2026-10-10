#!/usr/bin/env python3
"""Initial composition only. Never replay uncertain writes or apply final refinements."""
import json, os, pathlib
from loom_mcp import Loom


def compose_once(client, args, receipt, journal):
    if receipt.exists() or journal.exists():
        raise RuntimeError('Prior composition or attempt exists; reconcile native state before any new write')
    uid = args['requestBody']['target']['uid']
    before = client.call('loom_native_flow_surfaces_get_5ce19daccb56cc79', {'uid': uid})
    tree = before['data']['tree']
    if tree.get('subModels', {}).get('items'):
        raise RuntimeError('Target grid is not empty; refusing append')
    # Exclusive, durable intent precedes dispatch. Any later failure leaves a replay fence.
    with journal.open('x') as handle:
        json.dump({'state': 'pending-or-unknown', 'target': uid, 'request': args}, handle)
        handle.flush()
        os.fsync(handle.fileno())
    directory_fd = os.open(journal.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    result = client.call('loom_native_flow_surfaces_compose_fcc21dedb4accf41', args)
    readback = client.call('loom_native_flow_surfaces_get_5ce19daccb56cc79', {'uid': uid})
    temp = receipt.with_suffix('.json.pending')
    with temp.open('x') as handle:
        json.dump({'result': result, 'readback': readback}, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    temp.replace(receipt)
    return readback


def main():
    root = pathlib.Path(__file__).resolve().parents[1]
    client = Loom()
    for key in ['maintenance', 'work-orders']:
        args = json.loads((root / f'generation/pages/{key}.json').read_text())
        compose_once(client, args, root / f'generation/bindings/{key}-composition.json',
                     client.runtime / f'{key}-composition-attempt.json')
        print(key + ': initial native composition read back; final overlay remains required')


if __name__ == '__main__':
    main()
