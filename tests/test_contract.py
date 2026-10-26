"""Offline state-machine and mocked nondeterministic boundary tests; NOT live evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

ROOT=Path(__file__).resolve().parents[1]
OWNER='0x'+'1'*40
OTHER='0x'+'2'*40
class UserError(Exception): pass
class Disagreement(Exception): pass
class TreeMap(dict): pass
class Return:
    def __init__(self,value): self.calldata=value
class Contract:
    def __new__(cls):
        obj=object.__new__(cls)
        for name in cls.__annotations__:setattr(obj,name,TreeMap())
        return obj

FRAG='A fragmented message begins with the FIN bit clear and an opcode other than 0, followed by continuation frames; the fragments of one message MUST NOT be interleaved between the fragments of another message unless an extension has been negotiated. Control frames MAY be injected in the middle of a fragmented message.'
CONTROL='All control frames MUST have a payload length of 125 bytes or less and MUST NOT be fragmented.'
CLOSE='The application MUST NOT send any more data frames after sending a Close frame. After both sending and receiving a Close message, an endpoint considers the WebSocket connection closed and MUST close the underlying TCP connection.'
FIXTURE=('Request for Comments: 6455\nThe WebSocket Protocol\n'+'fixture-not-official-document\n'*45+'\n5.4.  Fragmentation\n'+FRAG+'\n5.5.  Control Frames\n'+CONTROL+'\n5.5.1.  Close\n'+CLOSE+'\n5.5.2.  Ping\nFixture end.').encode()

class Runtime:
    def __init__(self):
        self.answers=[];self.bodies=[FIXTURE];self.fetches=[];self.status=200;self.prompts=[];self.transform=lambda value:value
        self.gl=types.SimpleNamespace(Contract=Contract,public=types.SimpleNamespace(view=lambda f:f,write=lambda f:f),message=types.SimpleNamespace(sender_address=types.SimpleNamespace(as_hex=OWNER)),nondet=types.SimpleNamespace(web=types.SimpleNamespace(get=self.fetch),exec_prompt=self.prompt),eq_principle=types.SimpleNamespace(strict_eq=self.strict),vm=types.SimpleNamespace(UserError=UserError,Return=Return,run_nondet_unsafe=self.run))
    def fetch(self,url,headers):
        self.fetches.append(url);body=self.bodies.pop(0) if len(self.bodies)>1 else self.bodies[0]
        return types.SimpleNamespace(status=self.status,body=body)
    def prompt(self,*args,**kwargs):
        self.prompts.append(args[0]);return copy.deepcopy(self.answers.pop(0))
    def strict(self,fn):
        a,b=fn(),fn()
        if a!=b:raise Disagreement('Independent sources differ')
        return a
    def run(self,leader,validator):
        result=leader()
        if not validator(Return(self.transform(copy.deepcopy(result)))):raise Disagreement('Independent semantics or substantive citations differ')
        return result
    def load(self):
        module=types.ModuleType('genlayer');module.__all__=['gl','TreeMap'];module.gl=self.gl;module.TreeMap=TreeMap
        old=sys.modules.get('genlayer');sys.modules['genlayer']=module
        try:
            spec=importlib.util.spec_from_file_location('rfcreplay_test',ROOT/'contracts/rfcreplay.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
        finally:
            if old:sys.modules['genlayer']=old
            else:del sys.modules['genlayer']

class ContractTests(unittest.TestCase):
    def setUp(self):self.r=Runtime();self.m=self.r.load();self.c=self.m.RFCReplay();self.sha=self.m.hashlib.sha256(FIXTURE).hexdigest()
    def profile(self):return json.loads(self.c.get_profile('p'))
    def opened(self):self.c.open_profile('p',self.sha)
    def captured(self):self.opened();self.c.capture_source('p')
    def answers(self,unknown=None):
        p=self.profile();rows=[]
        for rid,section,condition in self.m.RULES:
            rows.append({'id':rid,'support':'UNKNOWN' if rid==unknown else 'SUPPORTED','condition':'UNKNOWN' if rid==unknown else condition,'spans':[{'start_line':2,'end_line':2}],'reason':'Explicit offline fixture interpretation, not a real validator result'})
        answer={'rules':rows};self.r.answers.extend([copy.deepcopy(answer),copy.deepcopy(answer),{'supported':[True]*5}]);return answer
    def ready(self):self.captured();self.answers();self.c.attest_profile('p')
    def trace(self,frames,tid='t',digest=None):self.c.replay_trace(tid,'p',digest or self.profile()['certificate']['digest'],json.dumps(frames))
    def test_open_binds_creator_and_source(self):
        self.opened();p=self.profile();self.assertEqual(p['owner'],OWNER);self.assertEqual(p['expected_document_sha256'],self.sha)
        with self.assertRaises(UserError):self.opened()
    def test_invalid_ids_hashes(self):
        for pid,sha in [('!','a'*64),('ok','A'*64),('ok','')]:
            with self.assertRaises(UserError):self.c.open_profile(pid,sha)
    def test_source_captured_independently_and_exactly(self):
        self.captured();p=self.profile();self.assertEqual(len(self.r.fetches),2);self.assertTrue(all(u==self.m.SOURCE_URL for u in self.r.fetches));self.assertEqual(p['source_digest'],self.m._hash(self.m._json(p['source'])))
    def test_source_hash_change_is_not_silently_accepted(self):
        self.opened();self.r.bodies=[FIXTURE+b'changed']
        with self.assertRaises(UserError):self.c.capture_source('p')
        self.assertEqual(self.profile()['state'],'OPEN')
    def test_missing_http_or_sections_do_not_capture(self):
        self.opened();self.r.status=500
        with self.assertRaises(UserError):self.c.capture_source('p')
        with self.assertRaises(UserError):self.m._sections('No complete source')
    def test_no_silent_source_truncation(self):
        text=FIXTURE.decode().replace(FRAG,FRAG+'x'*19000)
        with self.assertRaises(UserError):self.m._sections(text)
    def test_non_creator_cannot_capture_or_attest(self):
        self.opened();self.r.gl.message.sender_address.as_hex=OTHER
        with self.assertRaises(UserError):self.c.capture_source('p')
        self.r.gl.message.sender_address.as_hex=OWNER;self.c.capture_source('p');self.r.gl.message.sender_address.as_hex=OTHER
        with self.assertRaises(UserError):self.c.attest_profile('p')
    def test_source_and_attestation_single_shot(self):
        self.ready()
        with self.assertRaises(UserError):self.c.capture_source('p')
        with self.assertRaises(UserError):self.c.attest_profile('p')
    def test_complete_profile_has_bound_certificate(self):
        self.ready();p=self.profile();cert=p['certificate'];h=cert.pop('digest');self.assertEqual(p['state'],'READY');self.assertEqual(h,self.m._hash(self.m._json(cert)));self.assertEqual(cert['source_digest'],p['source_digest']);self.assertEqual(cert['document_sha256'],self.sha)
    def test_missing_rule_rejected(self):
        self.captured();self.answers();self.r.answers[0]['rules'].pop()
        with self.assertRaises(UserError):self.c.attest_profile('p')
    def test_generated_rule_or_condition_rejected(self):
        self.captured();self.answers();self.r.answers[0]['rules'][0]['condition']='exec(malicious_code)'
        with self.assertRaises(UserError):self.c.attest_profile('p')
    def test_model_cannot_type_a_free_quote(self):
        self.captured();self.answers();self.r.answers[0]['rules'][0]['quote']='This invented statement is not in the source.'
        with self.assertRaises(UserError):self.c.attest_profile('p')
    def test_quotes_reconstruct_exact_lf_lines_without_normalization(self):
        text='Header\n   A substantive source passage.\r\n\x0cPage break stays here\nLast line without LF'
        lines=self.m._source_lines(text);self.assertEqual(''.join(lines),text);self.assertEqual(len(lines),4)
        quotes=self.m._quotes([{'start_line':2,'end_line':3}],text)
        self.assertEqual(quotes,['   A substantive source passage.\r\n\x0cPage break stays here\n'])
        self.assertIn(quotes[0],text)
    def test_reconstruction_preserves_multiple_disjoint_support_passages(self):
        text='   Fragment definition is exact.\n\n   Another unrelated source paragraph.\n\n   No interleaving without an extension.\n'
        spans=[{'start_line':1,'end_line':1},{'start_line':5,'end_line':5}]
        quotes=self.m._quotes(spans,text)
        self.assertEqual(quotes,[text.splitlines(keepends=True)[0],text.splitlines(keepends=True)[4]])
    def test_span_bounds_types_order_overlap_and_count(self):
        text='A substantive source line with enough characters.\n'*6
        cases=[[],[{'start_line':0,'end_line':2}],[{'start_line':1,'end_line':7}],[{'start_line':3,'end_line':2}],[{'start_line':True,'end_line':2}],[{'start_line':1.0,'end_line':2}],[{'start_line':1,'end_line':2,'quote':'ignored'}],[{'start_line':1,'end_line':3},{'start_line':3,'end_line':4}],[{'start_line':4,'end_line':4},{'start_line':2,'end_line':2}],[{'start_line':n,'end_line':n} for n in range(1,6)]]
        for spans in cases:
            with self.subTest(spans=spans),self.assertRaises(UserError):self.m._quotes(spans,text)
    def test_aggregate_quote_bound_is_not_relaxed(self):
        with self.assertRaises(UserError):self.m._quotes([{'start_line':1,'end_line':1}],'short\n')
        with self.assertRaises(UserError):self.m._quotes([{'start_line':1,'end_line':1}],'x'*1801)
        with self.assertRaises(UserError):self.m._quotes([{'start_line':1,'end_line':1},{'start_line':3,'end_line':3}],'x'*900+'\nskip\n'+'x'*900)
    def test_stored_quotes_and_fixed_section_cannot_be_substituted(self):
        self.captured();answer=self.answers();source=self.profile()['source'];rows=self.m._claims(answer,source)
        self.assertEqual(rows[0]['quotes'],[source['sections']['5.4'].split('\n',1)[1]])
        for field,value in [('quotes',['   Paraphrased but semantically similar.']),('section','5.5'),('unexpected',True)]:
            altered=copy.deepcopy(rows);altered[0][field]=value
            with self.subTest(field=field),self.assertRaises(UserError):self.m._stored_claims(altered,source)
    def test_validator_rejects_tampered_leader_citation_even_with_same_vector(self):
        self.captured();self.answers()
        def alter(rows):rows[0]['quotes'][0]+='\n';return rows
        self.r.transform=alter
        with self.assertRaises(Disagreement):self.c.attest_profile('p')
        self.assertEqual(self.profile()['state'],'SOURCE_READY')
    def test_prompts_include_complete_numbered_source_and_separate_audit(self):
        self.ready();source=self.profile()['source']
        for prompt in self.r.prompts[:2]:
            data=json.loads(prompt.split('UNTRUSTED_DATA_JSON:\n',1)[1])
            for section,original in source['sections'].items():
                numbered=data['source']['sections'][section]
                self.assertEqual([row['line'] for row in numbered],list(range(1,len(numbered)+1)))
                self.assertEqual(''.join(row['text'] for row in numbered),original)
        audit=json.loads(self.r.prompts[-1].split('UNTRUSTED_DATA_JSON:\n',1)[1]);self.assertEqual(audit['source'],source);self.assertEqual(len(audit['candidate']),5)
    def test_correct_line_membership_does_not_replace_substantive_audit(self):
        self.captured();self.answers();self.r.answers[0]['rules'][0]['spans']=[{'start_line':1,'end_line':2}];self.r.answers[-1]['supported'][0]=False
        with self.assertRaises(Disagreement):self.c.attest_profile('p')
    def test_substantive_support_must_be_verified(self):
        self.captured();self.answers();self.r.answers[-1]['supported'][0]=False
        with self.assertRaises(Disagreement):self.c.attest_profile('p')
        self.assertEqual(self.profile()['state'],'SOURCE_READY')
    def test_independent_rule_vector_must_match(self):
        self.captured();self.answers();self.r.answers[1]['rules'][1]['support']='UNKNOWN';self.r.answers[1]['rules'][1]['condition']='UNKNOWN'
        with self.assertRaises(Disagreement):self.c.attest_profile('p')
    def test_unknown_profile_is_explicitly_incomplete_not_retryable(self):
        self.captured();self.answers('CLOSE_COMPLETION');self.c.attest_profile('p');self.assertEqual(self.profile()['state'],'INCOMPLETE')
        with self.assertRaises(UserError):self.trace([{'sender':'client','opcode':'text','fin':True,'length':3}])
        with self.assertRaises(UserError):self.c.attest_profile('p')
    def test_wrong_digest_refuses_replay(self):
        self.ready()
        with self.assertRaisesRegex(UserError,'Profile digest mismatch'):self.trace([],digest='a'*64)
    def test_other_wallet_can_replay_exact_certificate(self):
        self.ready();self.r.gl.message.sender_address.as_hex=OTHER;frames=[{'sender':'client','opcode':'text','fin':True,'length':3}];self.trace(frames);record=json.loads(self.c.get_trace('t'));self.assertEqual(record['submitted_by'],OTHER);self.assertEqual(record['result']['status'],'PASS');digest=record.pop('digest');self.assertEqual(digest,self.m._hash(self.m._json(record)))
    def test_trace_is_immutable_and_input_bound(self):
        self.ready();self.trace([{'sender':'server','opcode':'ping','fin':False,'length':1}]);first=self.c.get_trace('t')
        with self.assertRaises(UserError):self.trace([])
        self.assertEqual(first,self.c.get_trace('t'));record=json.loads(first);self.assertEqual(record['input_digest'],self.m._hash(record['trace_json']));self.assertEqual(record['result']['code'],'CONTROL_FRAGMENTED')
    def test_input_error_is_recorded_not_protocol_violation(self):
        self.ready();self.trace([{'sender':'client','opcode':'reserved','fin':True,'length':0}]);self.assertEqual(json.loads(self.c.get_trace('t'))['result']['status'],'INPUT_ERROR')
    def test_storage_limit_rejects_before_state_write(self):
        self.ready()
        with self.assertRaises(UserError):self.c.replay_trace('t','p',self.profile()['certificate']['digest'],'x'*20001)
        with self.assertRaises(UserError):self.c.get_trace('t')

class KernelTests(unittest.TestCase):
    def test_shared_oracle_cases(self):
        kernel=Runtime().load()._replay
        for case in json.loads((ROOT/'tests/kernel-cases.json').read_text()):
            with self.subTest(case['name']):
                result=kernel(case.get('raw',case.get('frames')));self.assertEqual(result['status'],case['status']);self.assertEqual(result['code'],case['code'])
                if 'index' in case:self.assertEqual(result['index'],case['index'])
                if result['status']=='VIOLATION':self.assertEqual(result['prefix_length'],result['index']+1)

if __name__=='__main__':unittest.main()
