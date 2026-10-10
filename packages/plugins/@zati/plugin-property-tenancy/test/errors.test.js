'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {safeFailure}=require('../dist/server/errors');
test('expected failures preserve code and give bounded recovery guidance',()=>{
 for(const [code,pattern] of [['STALE_VERSION',/Reload/],['PARTY_ACCOUNT_NOT_PERMITTED',/authorized/],['OCCUPANCY_OVERLAP',/overlap/],['PROPERTY_SCOPE',/unavailable/],['OWNER_SCOPE_MIGRATION_REQUIRED',/cannot be changed yet/],['PARTY_SCOPE_MIGRATION_REQUIRED',/cannot be changed yet/]]){
  const result=safeFailure({code,message:'private SQL and submitted values'});
  assert.equal(result.code,code);assert.match(result.message,pattern);assert.doesNotMatch(result.message,/private|SQL|submitted values/);
 }
});
test('unexpected errors expose neither raw messages nor retry instruction',()=>{
 const result=safeFailure(new Error('SQL secret token private path'));
 assert.equal(result.code,'DOMAIN_OPERATION_FAILED');assert.doesNotMatch(result.message,/SQL|secret|token|private path|retry/i);
});


test('allowlisted hook denials expose safe 403 and stable code',()=>{
 const {denyHook}=require('../dist/server/errors');
 for(const code of ['DOMAIN_ACTION_REQUIRED','CONTEXT_IMMUTABLE','CONTEXT_DELETE_PROTECTED']){
  assert.throws(()=>denyHook(code),error=>{
   assert.equal(error.status,403);assert.equal(error.statusCode,403);assert.equal(error.expose,true);assert.equal(error.code,code);
   assert.match(error.message,/No changes were saved/);assert.doesNotMatch(error.message,/SQL|SELECT|password|token|stack/);return true;
  });
 }
});
test('unknown hook errors are not normalized into an authorization denial',()=>{
 const {denyHook}=require('../dist/server/errors');
 assert.throws(()=>denyHook('UNEXPECTED_DATABASE_ERROR'),error=>error instanceof TypeError&&error.status===undefined&&error.expose===undefined);
});
