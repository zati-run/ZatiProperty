# Independent popup scope review

Reviewed exact source 2cdf330445c53bf95156fccca8e8183566928643 in an isolated reviewer checkout. Twenty property UI tests passed on DGX. The minimal change replaces unregistered implicit propertyId/unitId filter paths with registered property.id/unit.id relations, and uses the qualified popup.record namespace for contextual IDs.

Independent read-only Loom field discovery confirmed zp_units.property and zp_tenancies.unit are registered belongsTo fields, while their implicit foreign keys are absent. Terms and parties tenancyId are explicitly registered bigInt fields. Native context for existing popup grid xavei31sxda returns no record variable and does return popup.record as Current popup record. popup.record.id itself is absent from context metadata, as are other implicit primary IDs.

Approved for bounded construction only. Actual relation primary-ID filter validation, popup.record.id runtime resolution, nested popup scoping and browser rendering remain verification gates. This review performed no app mutations and claims no live page acceptance.
