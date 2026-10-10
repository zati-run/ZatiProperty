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

