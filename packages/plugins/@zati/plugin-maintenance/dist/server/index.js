'use strict';
const { Plugin } = require('@nocobase/server');
const { deny, present, sameId, validateContext, validateOrder } = require('./invariants');
const contextFields = ['propertyId', 'unitId', 'tenancyId'];
const criticalFields = [...contextFields, 'requestId', 'vendorId', 'state', 'approvalRequired', 'approvalGranted'];
const plain = model => model?.get({ plain: true });
class MaintenancePlugin extends Plugin {
  async load() {
    const requireTransaction = options => { if (!options?.transaction) deny('TRANSACTION_REQUIRED'); return options.transaction; };
    const read = async (name, id, options) => {
      if (!present(id)) return null;
      const transaction = requireTransaction(options);
      const model = this.db.getModel(name);
      if (!model) deny('SCHEMA_UNAVAILABLE');
      return plain(await model.findOne({ where: { id }, transaction, lock: transaction.LOCK.UPDATE }));
    };
    const validate = async (model, options, before) => {
      requireTransaction(options);
      const name = model.constructor.name;
      const order = name === 'zp_work_orders';
      if (before && model.isNewRecord && order) {
        for (const [key, value] of Object.entries({ state: 'new', approvalRequired: true, approvalGranted: false })) {
          if (model.get(key) === undefined || model.get(key) === null) model.set(key, value);
        }
      }
      const values = plain(model);
      let previous = null;
      if (before && !model.isNewRecord) {
        previous = await read(name, values.id, options);
        if (!previous) deny('RECORD_MISSING');
        for (const key of order ? criticalFields : contextFields) {
          if (!sameId(model.previous(key), previous[key])) deny('STALE_UPDATE');
        }
        for (const key of contextFields) if (!sameId(values[key], previous[key])) deny('CONTEXT_IMMUTABLE');
      }
      const property = await read('zp_properties', values.propertyId, options);
      const unit = await read('zp_units', values.unitId, options);
      const tenancy = await read('zp_tenancies', values.tenancyId, options);
      validateContext(values, { property, unit, tenancy });
      if (order) {
        const request = await read('zp_maintenance_requests', values.requestId, options);
        const vendor = await read('zp_vendors', values.vendorId, options);
        let vendorPermission = null;
        if (present(values.vendorId)) {
          const permissionModel = this.db.getModel('zp_vendor_properties');
          if (!permissionModel) deny('SCHEMA_UNAVAILABLE');
          vendorPermission = plain(await permissionModel.findOne({ where: { vendorId: values.vendorId, propertyId: values.propertyId }, transaction: options.transaction, lock: options.transaction.LOCK.UPDATE }));
        }
        // After association writes, revalidate the final values inside the same transaction.
        // Use the current state as the baseline; lifecycle was checked before persistence.
        validateOrder(values, { previous: before ? previous : values, checkLifecycle: before, request, vendor, vendorPermission });
      }
    };
    for (const name of ['zp_maintenance_requests', 'zp_work_orders']) {
      this.db.on(`${name}.beforeSave`, (model, options) => validate(model, options, true));
      this.db.on(`${name}.afterSaveWithAssociations`, (model, options) => validate(model, options, false));
      this.db.on(`${name}.beforeDestroy`, () => deny('DELETE_PROTECTED'));
      for (const hook of ['beforeBulkCreate', 'beforeBulkUpdate', 'beforeBulkDestroy']) this.db.on(`${name}.${hook}`, () => deny('BULK_WRITE_PROTECTED'));
    }
    // Preserve established hierarchy; moving a unit/tenancy needs a separate migration service.
    for (const [name, field] of [['zp_units', 'propertyId'], ['zp_tenancies', 'unitId']]) {
      this.db.on(`${name}.beforeUpdate`, async (model, options) => {
        const previous = await read(name, model.get('id'), options);
        if (!previous || !sameId(model.get(field), previous[field])) deny('HIERARCHY_IMMUTABLE');
      });
      this.db.on(`${name}.beforeBulkUpdate`, () => deny('BULK_WRITE_PROTECTED'));
    }
    // Context rows are retained while this protected slice is active. An archival/migration
    // service must explicitly account for all dependents before deletion can be supported.
    for (const name of ['zp_properties', 'zp_units', 'zp_tenancies', 'zp_vendors']) {
      this.db.on(`${name}.beforeDestroy`, () => deny('CONTEXT_DELETE_PROTECTED'));
      this.db.on(`${name}.beforeBulkDestroy`, () => deny('CONTEXT_DELETE_PROTECTED'));
    }
  }
}
module.exports = MaintenancePlugin;
module.exports.default = MaintenancePlugin;
