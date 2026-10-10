'use strict';
const messages=Object.freeze({
 INVALID_REASON_CODE:'Choose a supported reason for this decision.',
 DUPLICATE_OWNER:'Include each owner once in the complete ownership set.',
 DUPLICATE_PARTY_USER:'Include each linked account once in the tenancy parties.',
 INVALID_ID:'Choose a valid available record.',
 INVALID_INTERESTS:'Review the complete ownership set.',
 INVALID_PARTY_ROLE:'Choose a supported tenancy party role.',
 OWNERSHIP_TOTAL:'Ownership shares must total exactly 100 percent.',
 PARTY_PERIOD_MISMATCH:'Party dates must fall within the tenancy dates.',
 PRIMARY_PARTY_REQUIRED:'Choose exactly one primary tenancy party.',
 PRIMARY_USER_REQUIRED:'Choose an authorized account for the primary tenancy party.',
 OWNERSHIP_OVERLAP:'These dates overlap an approved ownership set. Review its dates.',
 END_EXTENSION_FORBIDDEN:'The end date cannot extend the existing tenancy period.',
 PRIMARY_IDENTITY_IMMUTABLE:'The existing primary account cannot be changed here.',
 INVALID_DATE:'Enter a valid calendar date.',
 INVALID_INTERVAL:'The end date must be after the start date.',
 INVALID_INTEGER:'Enter a whole number within the permitted range.',
 INVALID_TERMS:'Review the contract currency, frequency and amounts.',
 INVALID_PARTIES:'Review the tenancy parties and required primary party.',
 TERM_PERIOD_MISMATCH:'The contract term dates must match the tenancy dates.',
 NOT_DRAFT:'This record is no longer a draft. Reload and review its current state.',
 NOT_ACTIVE:'This tenancy is not active. Reload and review its current state.',
 COMPLETE_SET_CONFIRMATION:'Review and explicitly confirm the complete ownership set.',

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
const hookMessages=Object.freeze({
 DOMAIN_ACTION_REQUIRED:'Use the approved property or tenancy action to change this record. No changes were saved.',
 CONTEXT_IMMUTABLE:'The ownership or property relationship cannot be changed through this action. No changes were saved.',
 CONTEXT_DELETE_PROTECTED:'This property context cannot be deleted through this action. No changes were saved.'
});
function denyHook(code){
 if(!Object.hasOwn(hookMessages,code))throw new TypeError('Unknown protected hook failure');
 const error=new Error(hookMessages[code]);
 error.code=code;error.status=403;error.statusCode=403;error.expose=true;
 throw error;
}
module.exports={safeFailure,denyHook};


