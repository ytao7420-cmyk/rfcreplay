export const RULE_VERSION='rfc6455-bounded-lines-v2';
export const SOURCE_URL='https://www.rfc-editor.org/rfc/rfc6455.txt';
export const RULES=[
  {id:'FRAGMENT_SEQUENCE',section:'5.4',condition:'ONE_OPEN_MESSAGE_PER_SENDER',title:'One fragmented message per sender',explanation:'A continuation needs an open fragmented message; a second data message cannot start inside it.'},
  {id:'CONTROL_INTERLEAVING',section:'5.4',condition:'MAY_INTERLEAVE_NO_FRAGMENT_CHANGE',title:'Control frames may interleave',explanation:'Ping, Pong and Close do not become data continuations.'},
  {id:'CONTROL_FIN_LENGTH',section:'5.5',condition:'FIN_TRUE_MAX125',title:'Control frames stay whole and small',explanation:'Control frames must have FIN set and payload length at most 125 bytes.'},
  {id:'POST_CLOSE_DATA',section:'5.5.1',condition:'SENDER_DATA_FORBIDDEN_AFTER_CLOSE',title:'No data after sending Close',explanation:'The sender of a Close cannot send further data frames, including continuations.'},
  {id:'CLOSE_COMPLETION',section:'5.5.1',condition:'BOTH_ENDPOINTS_CLOSE_CLOSES_CONNECTION',title:'Two-sided Close ends the connection',explanation:'After both directions have sent Close, subsequent frames fall outside an open connection.'}
];
export function canonical(value){if(Array.isArray(value))return'['+value.map(canonical).join(',')+']';if(value&&typeof value==='object')return'{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';return JSON.stringify(value);}
export async function digest(value){const raw=typeof value==='string'?value:canonical(value);const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw));return[...new Uint8Array(bytes)].map(b=>b.toString(16).padStart(2,'0')).join('');}
export function extractSections(text){const headings={'5.4':'\n5.4.  Fragmentation\n','5.5':'\n5.5.  Control Frames\n','5.5.1':'\n5.5.1.  Close\n','5.5.2':'\n5.5.2.  Ping\n'};const starts=Object.fromEntries(Object.entries(headings).map(([k,h])=>[k,text.lastIndexOf(h)]));if(Object.values(starts).some(i=>i<0)||!(starts['5.4']<starts['5.5']&&starts['5.5']<starts['5.5.1']&&starts['5.5.1']<starts['5.5.2']))throw Error('Official section headings are missing or out of order.');const sections={'5.4':text.slice(starts['5.4']+1,starts['5.5']),'5.5':text.slice(starts['5.5']+1,starts['5.5.1']),'5.5.1':text.slice(starts['5.5.1']+1,starts['5.5.2'])};if(Object.values(sections).some(s=>s.length<80||s.length>18000)||new TextEncoder().encode(canonical(sections)).length>26000)throw Error('Exact selected sections are outside the bounded profile; no truncation performed.');return sections;}
export function sourceLines(text){const parts=text.split('\n');return[...parts.slice(0,-1).map(part=>part+'\n'),...(parts.at(-1)?[parts.at(-1)]:[])];}
export function reconstructQuotes(spans,section){
  if(!Array.isArray(spans)||spans.length<1||spans.length>4)throw Error('Each rule needs one to four source line spans.');
  const lines=sourceLines(section),quotes=[];let previousEnd=0;
  for(const span of spans){if(!span||typeof span!=='object'||Array.isArray(span)||Object.keys(span).sort().join(',')!=='end_line,start_line')throw Error('Citation span fields differ.');const start=span.start_line,end=span.end_line;if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||!(previousEnd<start&&start<=end&&end<=lines.length))throw Error('Citation spans must be in range, ordered and non-overlapping.');const quote=lines.slice(start-1,end).join('');if(!section.includes(quote))throw Error('Reconstructed quote is not an exact passage from its frozen section.');quotes.push(quote);previousEnd=end;}
  // Match Python code point counts rather than JS UTF-16 code units.
  const length=quotes.reduce((count,quote)=>count+[...quote].length,0);if(length<20||length>1800)throw Error('Reconstructed citations exceed the 20-1800 character rule bound.');return quotes;
}
const OPS=['text','binary','continuation','ping','pong','close'];
const snapshot=s=>({client:{...s.client},server:{...s.server}});
function inputError(code,index,message){return{status:'INPUT_ERROR',code,index,message,checked_frames:0,prefix_length:0,timeline:[],final_state:null};}
export function replayTrace(input){
  let frames=input;
  if(typeof input==='string'){if(new TextEncoder().encode(input).length>20000)return inputError('TRACE_SIZE_LIMIT',null,'Trace text exceeds 20000 bytes.');try{frames=JSON.parse(input);}catch{return inputError('INVALID_JSON',null,'Trace must be a JSON array.');}}
  if(!Array.isArray(frames)||frames.length<1||frames.length>64)return inputError('FRAME_COUNT',null,'Trace requires 1–64 frames.');
  for(let i=0;i<frames.length;i++){const f=frames[i];if(!f||typeof f!=='object'||Array.isArray(f)||Object.keys(f).sort().join(',')!=='fin,length,opcode,sender')return inputError('FRAME_FIELDS',i,'Each frame needs exactly sender, opcode, fin and length.');if(!['client','server'].includes(f.sender))return inputError('UNKNOWN_SENDER',i,'Sender must be client or server.');if(!OPS.includes(f.opcode))return inputError('UNKNOWN_OPCODE',i,'Opcode is outside this bounded profile.');if(typeof f.fin!=='boolean')return inputError('FIN_TYPE',i,'FIN must be a boolean.');if(!Number.isSafeInteger(f.length)||f.length<0||f.length>65535)return inputError('LENGTH_RANGE',i,'Length must be an integer from 0 to 65535.');}
  const state={client:{fragment:null,sent_close:false},server:{fragment:null,sent_close:false}},timeline=[];
  const fail=(code,i,message,before)=>({status:'VIOLATION',code,index:i,message,checked_frames:i+1,prefix_length:i+1,timeline:[...timeline,{index:i,frame:frames[i],before,after:snapshot(state),result:code}],final_state:snapshot(state)});
  for(let i=0;i<frames.length;i++){const f=frames[i],own=state[f.sender],before=snapshot(state),control=['ping','pong','close'].includes(f.opcode);
    if(state.client.sent_close&&state.server.sent_close)return fail('FRAME_AFTER_HANDSHAKE_CLOSED',i,'Both directions already sent Close.',before);
    if(control&&!f.fin)return fail('CONTROL_FRAGMENTED',i,'A control frame cannot be fragmented.',before);
    if(control&&f.length>125)return fail('CONTROL_TOO_LARGE',i,'A control frame cannot exceed 125 bytes.',before);
    if(!control&&own.sent_close)return fail('DATA_AFTER_SENT_CLOSE',i,'This sender already sent Close.',before);
    if(f.opcode==='continuation'){if(!own.fragment)return fail('ORPHAN_CONTINUATION',i,'No fragmented message is open in this direction.',before);if(f.fin)own.fragment=null;}
    else if(f.opcode==='text'||f.opcode==='binary'){if(own.fragment)return fail('INTERLEAVED_DATA_MESSAGE',i,'A new data message starts before this sender finishes its fragmented message.',before);if(!f.fin)own.fragment=f.opcode;}
    else if(f.opcode==='close')own.sent_close=true;
    timeline.push({index:i,frame:f,before,after:snapshot(state),result:'ACCEPTED_STEP'});
  }
  const open=Object.entries(state).filter(([,s])=>s.fragment).map(([side])=>side);
  if(open.length)return{status:'INCOMPLETE',code:'OPEN_FRAGMENT',index:null,message:'Trace ends with an unfinished fragmented message: '+open.join(', ')+'.',checked_frames:frames.length,prefix_length:null,timeline,final_state:snapshot(state)};
  if(state.client.sent_close!==state.server.sent_close)return{status:'INCOMPLETE',code:'CLOSE_HANDSHAKE_PENDING',index:null,message:'Only one direction sent Close; completion is not established.',checked_frames:frames.length,prefix_length:null,timeline,final_state:snapshot(state)};
  return{status:'PASS',code:state.client.sent_close?'CLOSED_TRACE':'OPEN_TRACE',index:null,message:state.client.sent_close?'Both Close directions are present within the bounded trace.':'No violation of the attested finite profile was found in these frames.',checked_frames:frames.length,prefix_length:null,timeline,final_state:snapshot(state)};
}
export const PRESETS={
  interleaved:{title:'Ping inside a fragmented message',frames:[{sender:'client',opcode:'text',fin:false,length:3},{sender:'server',opcode:'text',fin:false,length:2},{sender:'client',opcode:'ping',fin:true,length:5},{sender:'server',opcode:'continuation',fin:true,length:2},{sender:'client',opcode:'continuation',fin:true,length:4}]},
  orphan:{title:'Continuation without a first fragment',frames:[{sender:'client',opcode:'continuation',fin:true,length:4}]},
  fragmentedPing:{title:'A fragmented Ping',frames:[{sender:'server',opcode:'ping',fin:false,length:10}]},
  afterClose:{title:'Data after sending Close',frames:[{sender:'client',opcode:'close',fin:true,length:2},{sender:'client',opcode:'text',fin:true,length:3}]},
  unfinished:{title:'An unfinished fragmented message',frames:[{sender:'server',opcode:'binary',fin:false,length:8},{sender:'client',opcode:'ping',fin:true,length:0}]},
  close:{title:'A complete two-sided close',frames:[{sender:'client',opcode:'close',fin:true,length:2},{sender:'server',opcode:'close',fin:true,length:2}]}
};
export async function verifyProfile(profile){
  if(profile.source){if(profile.source.document_sha256!==profile.expected_document_sha256)throw Error('Source document commitment mismatch.');if(profile.source.url!==SOURCE_URL)throw Error('Source URL differs from the fixed profile.');if(await digest(profile.source)!==profile.source_digest)throw Error('Source digest mismatch.');}
  if(profile.certificate){
    const {digest:hash,...body}=profile.certificate;
    if(await digest(body)!==hash)throw Error('Profile certificate digest mismatch.');
    if(body.profile_id!==profile.id||body.owner!==profile.owner||body.source_digest!==profile.source_digest||body.rule_version!==RULE_VERSION||body.document_sha256!==profile.expected_document_sha256)throw Error('Profile certificate identity mismatch.');
    if(!Array.isArray(body.rules)||body.rules.length!==RULES.length)throw Error('Profile rule set is incomplete.');
    for(let i=0;i<RULES.length;i++){
      const rule=body.rules[i],fixed=RULES[i];
      if(!rule||Object.keys(rule).sort().join(',')!=='condition,id,quotes,reason,section,spans,support'||rule.id!==fixed.id||rule.section!==fixed.section||!['SUPPORTED','UNKNOWN'].includes(rule.support))throw Error('Rule evidence mismatch.');
      const quotes=reconstructQuotes(rule.spans,profile.source.sections[fixed.section]);
      if(canonical(rule.quotes)!==canonical(quotes))throw Error('Rule quote bytes differ from exact source line reconstruction.');
      if(rule.condition!==(rule.support==='SUPPORTED'?fixed.condition:'UNKNOWN'))throw Error('Rule condition mismatch.');
      if(typeof rule.reason!=='string'||[...rule.reason].length<1||[...rule.reason].length>600)throw Error('Rule explanation is empty or too long.');
    }
    if((body.rules.every(r=>r.support==='SUPPORTED')?'READY':'INCOMPLETE')!==profile.state)throw Error('Profile readiness differs from its complete rule vector.');
  }
  return profile;
}
export async function verifyTrace(record){const {digest:hash,...body}=record;if(await digest(body)!==hash)throw Error('Trace receipt digest mismatch.');if(body.rule_version!==RULE_VERSION)throw Error('Trace rule version mismatch.');if(body.input_digest!==await digest(body.trace_json))throw Error('Input digest mismatch.');if(canonical(body.result)!==canonical(replayTrace(body.trace_json)))throw Error('Chain result differs from deterministic local replay.');return record;}
