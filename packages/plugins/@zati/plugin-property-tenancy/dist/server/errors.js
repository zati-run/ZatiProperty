'use strict';
const messages=Object.freeze({
 STALE_VERSION:'This record changed. Reload it and review the current values before making a new decision.',
 VERSION_CONFLICT:'This record changed. Reload it and review the current values before making a new decision.',
 REQUEST_ID_COLLISION:'This request identifier belongs to different values. Reconcile the original request before starting another command.',
 INVALID_REQUEST_ID:'A valid request identifier is required. Reload the form before starting a new command.',
 PARTY_ACCOUNT_NOT_PERMITTED:'Choose an account authorized for this property manager.',
 OCCUPANCY_OVERLAP:'These dates overlap an existing tenancy. Review the dates and existing occupancy.',
 TENANCY_OVERLAP:'These dates overlap an existing tenancy. Review the dates and existing occupancy.',
 OWNER_SCOPE:'This record is unavailable to your current account.',
 NOT_FOUND:'This record is unavailable to your current account.',
 PROPERTY_SCOPE:'This record is unavailable to your current account.',
 PARTY_SCOPE_MIGRATION_REQUIRED:'The current tenant account configuration cannot be changed yet. Keep the existing account configuration.',
 OWNER_SCOPE_MIGRATION_REQUIRED:'The current owner account configuration cannot be changed yet. Keep the existing account configuration.',
 CONSTRUCTOR_REQUIRED:'This setup action requires an authorized application constructor.',
 INVALID_TEXT:'Enter the required text within the permitted length.',
 UNKNOWN_INPUT:'The submitted form contains unsupported values. Reload the form and review the fields.'
});
function safeFailure(error){
 const code=typeof error?.code==='string'&&/^[A-Z_]{3,64}$/.test(error.code)?error.code:'DOMAIN_OPERATION_FAILED';
 return {code,status:['PROPERTY_SCOPE','CONSTRUCTOR_REQUIRED'].includes(code)?403:409,
 message:messages[code]||'The operation could not be confirmed. Check its recorded outcome before making another request.'};
}
module.exports={safeFailure};

