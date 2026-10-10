'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require.resolve('../dist/client/index'), 'utf8');
class NativePlugin { constructor(app) { this.app = app; } }
async function verify(exports) {
  assert.equal(exports.__esModule, true);
  const app = Object.freeze({ marker: 'native-runtime' });
  const instance = new exports.default(app);
  assert.ok(instance instanceof NativePlugin);
  assert.equal(instance.app, app);
  assert.equal(await instance.load(), undefined);
  assert.deepEqual(Object.keys(instance), ['app']);
}
test('client entry is a no-op native plugin under CommonJS loader', async () => {
  const module = { exports: {} };
  vm.runInNewContext(source, { exports: module.exports, module, require(name) { assert.equal(name, '@nocobase/client'); return { Plugin: NativePlugin }; } });
  await verify(module.exports);
});
test('client entry registers the exact named AMD module and native dependency', async () => {
  let exported;
  function define(name, dependencies, factory) {
    assert.equal(name, '@zati/plugin-maintenance');
    assert.deepEqual(Array.from(dependencies), ['@nocobase/client']);
    exported = factory({ Plugin: NativePlugin });
  }
  define.amd = {};
  vm.runInNewContext(source, { define });
  await verify(exported);
});
test('client entry attaches only its native module to browser global', async () => {
  const self = { '@nocobase/client': { Plugin: NativePlugin } };
  vm.runInNewContext(source, { self });
  assert.deepEqual(Object.keys(self), ['@nocobase/client', '@zati/plugin-maintenance']);
  await verify(self['@zati/plugin-maintenance']);
});
