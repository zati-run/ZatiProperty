'use strict';
const crypto = require('node:crypto');
function deny(code) { const e = new Error(code); e.code = code; throw e; }
const id = value => { if (!Number.isSafeInteger(Number(value)) || Number(value) < 1 || !/^[1-9][0-9]*$/.test(String(value))) deny('INVALID_ID'); return String(value); };
const same = (a,b) => String(a) === String(b);
function date(value, nullable=false) {
  if (nullable && (value === null || value === undefined)) return null;
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().slice(0,10)!==value) deny('INVALID_DATE');
  return value;
}
function interval(start,end) { start=date(start);end=date(end,true);if(end && end<=start) deny('INVALID_INTERVAL');return [start,end]; }
const overlaps = (a,b) => (!a[1] || b[0]<a[1]) && (!b[1] || a[0]<b[1]);
function integer(value,min,max) { if(!Number.isInteger(value)||value<min||value>max) deny('INVALID_INTEGER');return value; }
function string(value,max=200) {if(typeof value!=='string'||!value.trim()||value.length>max) deny('INVALID_TEXT');return value.trim();}
function keys(value, allowed) {if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).some(k=>!allowed.includes(k)))deny('UNKNOWN_INPUT');}
function canonical(value) {
  if(value===null || typeof value!=='object')return JSON.stringify(value);
  if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
  return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
}
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
function tenancyInput(input) {
  interval(input.startDate,input.endDate);
  keys(input.term,['effectiveFrom','effectiveTo','currency','rentMinor','depositMinor','rentFrequency','dueDay','prorationPolicy']);
  const t=input.term;interval(t.effectiveFrom,t.effectiveTo);
  if(t.effectiveFrom!==input.startDate || (t.effectiveTo||null)!==(input.endDate||null))deny('TERM_PERIOD_MISMATCH');
  if(!/^[A-Z]{3}$/.test(t.currency)||!['weekly','fortnightly','monthly','quarterly','annually'].includes(t.rentFrequency))deny('INVALID_TERMS');
  integer(t.rentMinor,0,2147483647);integer(t.depositMinor,0,2147483647);integer(t.dueDay,1,31);string(t.prorationPolicy,64);
  if(!Array.isArray(input.parties)||input.parties.length<1||input.parties.length>20)deny('INVALID_PARTIES');
  let primary=0;
  const userIds=new Set();
  for(const p of input.parties) {
    keys(p,['displayName','userId','partyRole','effectiveFrom','effectiveTo']);
    string(p.displayName,200);interval(p.effectiveFrom,p.effectiveTo);
    if(p.effectiveFrom!==input.startDate||(p.effectiveTo||null)!==(input.endDate||null))deny('PARTY_PERIOD_MISMATCH');
    if(!['primary','cotenant','guarantor','occupant'].includes(p.partyRole))deny('INVALID_PARTY_ROLE');
    if(p.partyRole==='primary') {primary++;if(!p.userId)deny('PRIMARY_USER_REQUIRED');}
    if(p.userId) {const key=id(p.userId);if(userIds.has(key))deny('DUPLICATE_PARTY_USER');userIds.add(key);}
  }
  if(primary!==1)deny('PRIMARY_PARTY_REQUIRED');
}
function interestsInput(values) {
  if(!Array.isArray(values)||values.length<1||values.length>20)deny('INVALID_INTERESTS');
  let total=0;const owners=new Set();
  for(const row of values) {
    keys(row,['ownerContactId','shareBasisPoints']);const key=id(row.ownerContactId);
    if(owners.has(key))deny('DUPLICATE_OWNER');owners.add(key);total+=integer(row.shareBasisPoints,1,10000);
  }
  if(total!==10000)deny('OWNERSHIP_TOTAL');
}
function verifyEvents(events,head) {
  let previous='0'.repeat(64),sequence=0;
  for(const event of events) {
    if(Number(event.sequence)!==++sequence||event.previousHash!==previous)deny('AUDIT_CHAIN');
    let parsed;try{parsed=JSON.parse(event.canonicalPayload);}catch{deny('AUDIT_CHAIN');}
    if(canonical(parsed)!==event.canonicalPayload||hash(previous+'\n'+event.canonicalPayload)!==event.eventHash)deny('AUDIT_CHAIN');
    previous=event.eventHash;
  }
  if(Number(head.headSequence)!==sequence||head.headHash!==previous)deny('AUDIT_HEAD');
  return {valid:true,sequence};
}
module.exports={deny,id,same,date,interval,overlaps,integer,string,keys,canonical,hash,tenancyInput,interestsInput,verifyEvents};
