/* Apache-2.0. Native NocoBase UMD plugin entry; no custom UI or side effects. */
(function (root, factory) {
  if (typeof exports === 'object' && typeof module === 'object') {
    module.exports = factory(require('@nocobase/client'));
  } else if (typeof define === 'function' && define.amd) {
    define('@zati/plugin-maintenance', ['@nocobase/client'], factory);
  } else if (typeof exports === 'object') {
    exports['@zati/plugin-maintenance'] = factory(require('@nocobase/client'));
  } else {
    root['@zati/plugin-maintenance'] = factory(root['@nocobase/client']);
  }
})(typeof self !== 'undefined' ? self : globalThis, function (client) {
  'use strict';
  class MaintenanceClientPlugin extends client.Plugin {
    async load() {}
  }
  return { __esModule: true, default: MaintenanceClientPlugin };
});
