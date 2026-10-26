import test from 'node:test';
import assert from 'node:assert/strict';
import {assertZeroValue} from '../lib/zero-value.js';
const hash='0x'+'a'.repeat(64);
test('observable zero needs no raw RPC read',async()=>{for(const value of [0,0n,'0','0x0'])assert.equal(await assertZeroValue({request:()=>{throw Error('Should not read');}},{value},hash),true);});
test('SDK-normalized zero is recovered only from same-hash raw transaction',async()=>{let calls=0;const reader={request:async request=>{calls++;assert.deepEqual(request,{method:'eth_getTransactionByHash',params:[hash]});return{hash,value:0};}};assert.equal(await assertZeroValue(reader,{value:undefined},hash),true);assert.equal(calls,1);});
test('nonzero, wrong hash, absent and invalid raw values cannot be assumed zero',async()=>{for(const raw of [{hash,value:1},{hash:'0x'+'b'.repeat(64),value:0},{hash},{hash,value:false},{hash,value:null},{hash,value:0.1}])await assert.rejects(assertZeroValue({request:async()=>raw},{},hash));});
test('unobservable or failed raw RPC keeps value unresolved',async()=>{await assert.rejects(assertZeroValue({request:async()=>{throw Error('Read unavailable');}},{},hash),/Read unavailable/);});
