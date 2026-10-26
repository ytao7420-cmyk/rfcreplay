# Validation record

Current phase: **source-verified v2 Studionet deployment, complete seven-call application workflow and separate expected-rejection test completed.** `public/evidence/demo.json` is `verified:true`, `npm run verify` passes, and the old v1 source/deployment/failure history remains intact. No browser wallet QA or contribution submission has been performed by this worker.

Local results: **60 JavaScript tests and 29 Python tests pass**, including 23 shared labelled kernel cases and full JS/Python result parity. `npm run build`, `npm run plan` and syntax checks pass. Vite reports a non-fatal main SDK bundle warning above 500 KB.

## Verified v2 execution — 2026-10-26

Contract: [0x2628ee871f5a0A0391D851C181B493faD3666feb](https://explorer-studio.genlayer.com/address/0x2628ee871f5a0A0391D851C181B493faD3666feb); source SHA-256 `08ad96fe2642be5008066637f3d31a6bac96ccab1471cb3493a25cc46e2c6595` was checked against deployed code. All broadcasts use Studionet 61999, zero value and full validators (`leaderOnly:false`). The first attestation on this source version succeeded; no failed calldata was rebroadcast.

| Step | Actual result | Transaction |
| --- | --- | --- |
| Deploy v2 | FINALIZED, SUCCESS, MAJORITY_AGREE | [0x6d60810c899458197c5c626b45f41dec22bdd0240caade568dfe4a25358df284](https://explorer-studio.genlayer.com/tx/0x6d60810c899458197c5c626b45f41dec22bdd0240caade568dfe4a25358df284) |
| open-profile | FINALIZED, SUCCESS, MAJORITY_AGREE | [0x4d0b98b8cb8ca073544cf072c33f349f5860428f02605d09e30c193c345a1781](https://explorer-studio.genlayer.com/tx/0x4d0b98b8cb8ca073544cf072c33f349f5860428f02605d09e30c193c345a1781) |
| capture-official-source | FINALIZED, SUCCESS, MAJORITY_AGREE | [0x3cc78a02a35fdb3f65e1707152d7339173838c8403a4089cf5303ec3db810465](https://explorer-studio.genlayer.com/tx/0x3cc78a02a35fdb3f65e1707152d7339173838c8403a4089cf5303ec3db810465) |
| attest-five-rules | FINALIZED, SUCCESS, MAJORITY_AGREE | [0x2cad896d07a6f76a072e5688e845658437dbf60ed94e56d041ae17188376ec35](https://explorer-studio.genlayer.com/tx/0x2cad896d07a6f76a072e5688e845658437dbf60ed94e56d041ae17188376ec35) |
| legal-interleaved | FINALIZED, SUCCESS, MAJORITY_AGREE | [0xee5726df01b017e68e1ea5db74cd1173c4f1eb7c3aba6fa4224c05f7285bc2f3](https://explorer-studio.genlayer.com/tx/0xee5726df01b017e68e1ea5db74cd1173c4f1eb7c3aba6fa4224c05f7285bc2f3) |
| orphan-violation | FINALIZED, SUCCESS, MAJORITY_AGREE | [0x8321d0c162483c311e288ebd76a699b48788a45d8975c6b4b8293b3a7b0c2e4b](https://explorer-studio.genlayer.com/tx/0x8321d0c162483c311e288ebd76a699b48788a45d8975c6b4b8293b3a7b0c2e4b) |
| unfinished-message | FINALIZED, SUCCESS, MAJORITY_AGREE | [0x40714118d53b580cae2608e7e21d88e05f69334703bc0d39b9d6c9ce248fa91e](https://explorer-studio.genlayer.com/tx/0x40714118d53b580cae2608e7e21d88e05f69334703bc0d39b9d6c9ce248fa91e) |
| unsupported-input | FINALIZED, SUCCESS, MAJORITY_AGREE | [0x75f55cb3f6eea5e6f6ae82c361410c86bc23cbd15c8516c7d73ede602dc466b8](https://explorer-studio.genlayer.com/tx/0x75f55cb3f6eea5e6f6ae82c361410c86bc23cbd15c8516c7d73ede602dc466b8) |
| Wrong profile digest (separate negative) | ACCEPTED, **ERROR**, MAJORITY_AGREE; expected rollback `Profile digest mismatch` verified | [0x816241cfad2141aff3ae90a745d9bdccf9c3f5327ec8bd90ba4f0ddb2c0ac455](https://explorer-studio.genlayer.com/tx/0x816241cfad2141aff3ae90a745d9bdccf9c3f5327ec8bd90ba4f0ddb2c0ac455) |

Profile `rfcreplay-rfc6455-lines-v2` is `READY`, certificate digest `9f41e582076da31762e8c546870225c94afdadf2df83112017571408a1c6bb12`. The five actual rows are all `SUPPORTED`; exact reconstructed quote totals are 469, 263, 101, 731 and 702 characters. The independently audited line spans and complete source bytes are stored in `public/evidence/demo.json`.

The four immutable trace outcomes are `PASS / OPEN_TRACE`, `VIOLATION / ORPHAN_CONTINUATION`, `INCOMPLETE / OPEN_FRAGMENT` and `INPUT_ERROR / UNKNOWN_OPCODE`. Each recording call executed successfully; those application outcomes are not VM execution errors. The separate wrong-digest negative remains VM ERROR and is not counted among the seven successful application calls.

Proof files: `public/deployment.json`, `public/source/rfcreplay.py`, `public/evidence/demo.json`, `public/evidence/negative.json` and the compact `public/evidence/validation-summary.json`. `npm run verify` validates one complete profile, four trace contents/results and seven successful receipts. The full negative receipt is retained privately and its public summary verifies the exact expected rollback.

Read recovery: intermittent RPC fetch/proxy timeouts occurred before initial application calls and again at the final trace read. Known hashes stayed journaled. The recovery run read the same seven hashes and emitted no replacement application transaction. An ignored process-local preload routed whitelisted read-only RPC methods through `curl` and the user's existing localhost proxy; original SDK write transport and system network settings were unchanged.

## Preserved v1 failed execution — 2026-10-26

Reviewed contract SHA-256: `4de625814bedadbfc31b701b9ef90ee2549331281f4a10c64c3e692c36a1047c`.

Official RFC source: `https://www.rfc-editor.org/rfc/rfc6455.txt`, 162,067 bytes, full document SHA-256 `765775326aee0ecca9b04bde3fd1f52932d498e33e34e428bd61b8a24da0fa3b`. The 9,170-byte canonical selected-section payload has source digest `ef7a38c3d45d79f328f99015ee5276d8bd5d57bf38938c2450ee888705c1aeed`.

Studionet contract: [0x7fFF6f6a36fc65854EEf20b5BD0E943C9b814aDE](https://explorer-studio.genlayer.com/address/0x7fFF6f6a36fc65854EEf20b5BD0E943C9b814aDE). Deployed source was read back and matched the reviewed SHA. All calls used chain 61999, zero value and `leaderOnly: false`, with newly generated project-controlled, unfunded actors.

| Step | Actual result | Transaction |
| --- | --- | --- |
| Deploy | Successful execution and validator majority agreement; deployed source matched | [0x098f78…ceaf6](https://explorer-studio.genlayer.com/tx/0x098f78e5c715dd093e56cda58a72e5103666ae5a723821974936c079265ceaf6) |
| Open profile | ACCEPTED, SUCCESS, MAJORITY_AGREE | [0x6262a5…f3a03](https://explorer-studio.genlayer.com/tx/0x6262a52ff25b2be231342e9c7d636462b5707efc857ec0f495f99f504e6f3a03) |
| Capture official source | ACCEPTED, SUCCESS, MAJORITY_AGREE | [0xb15713…37202](https://explorer-studio.genlayer.com/tx/0xb157132a3fd0cd6e9e2c97bb05f2e020eeeacec8e4f024ba461ee5f7e3737202) |
| Attest five fixed rules | **UNDETERMINED, MAJORITY_DISAGREE**; leader execution ERROR/rollback | [0x21c6fa…b7ddd](https://explorer-studio.genlayer.com/tx/0x21c6fa1119c2ee4787d9059e6ca0b3cf64d6aab6d10f53c71811aa3037ab7ddd) |

The retained leader error is exactly `Rule quote is not an exact passage from its frozen section`. Validators disagreed; this is neither a successful attestation nor a planned successful negative test. A fresh view after the failed call returned `SOURCE_READY`, the expected source digest, and `certificate: null`.

The harness stopped automatically. It did not broadcast any trace, did not run `--negative`, did not reroll the unchanged proposal and did not alter a rule or evidence outcome to force acceptance. `npm run verify` correctly exits 1 with `No complete verified demonstration is recorded.`

Retained public artifacts: `public/evidence/failed-attestation.json` contains the small actual failure record and votes; `public/evidence/profile-last-attempt.json` contains the real read-back profile and transaction summaries. The restricted `.local/failed-receipt-<hash>.json` retains the full original failed receipt and the workflow journal retains every known hash. No test private keys are published.

## Implemented representation repair — reviewed and deployed

Repaired contract SHA-256: `08ad96fe2642be5008066637f3d31a6bac96ccab1471cb3493a25cc46e2c6595`; rule evidence version `rfc6455-bounded-lines-v2`.

The model now selects one to four ordered, non-overlapping inclusive spans from one-based LF-numbered original section lines. Code reconstructs the quotations, with the original 20–1,800 combined-character bound, strict exact membership and no whitespace normalization. Multiple spans can include a definition and its distant qualifier without copying unrelated source or weakening a condition. Validators reconstruct the actual proposed quotations, independently interpret the complete five-rule vector and separately audit substantive support in the full frozen source. Arbitrary generated quotes, extra fields, out-of-range/overlapping spans, changed section IDs and changed stored quote bytes are rejected. The five rules and replay kernel are unchanged.

The complete official document and selected-source digests above are unchanged. The old source is preserved at `public/source/attempts/rfcreplay-4de625814bedadbfc31b701b9ef90ee2549331281f4a10c64c3e692c36a1047c.py`; its deployment and readback are archived under `public/evidence/deployment-0x7fFF6f6a36fc65854EEf20b5BD0E943C9b814aDE.json` and `profile-attempt-0x7fFF6f6a36fc65854EEf20b5BD0E943C9b814aDE.json`. The original failure record, private full failed receipt and workflow journal remain unchanged. Active public source and deployment now point to the reviewed v2 contract above; the old address remains only in archived historical evidence.

The parent reviewed this repaired source/hash before authorizing its new deployment and single-version workflow. The harness uses new versioned profile/trace IDs and a new deployment-bound journal; a known failed calldata hash is read only for diagnosis, never sent again. Failed or unresolved attestation attempts retain their exact transaction summary and actual readback where available before the harness stops. No retry loop or rule deletion was introduced.


## Meaningful offline checks

- Shared independently labelled trace corpus checks both per-direction fragmentation states, control interleaving, FIN and 125-byte boundaries, forbidden new data messages, sent-versus-received Close semantics, completed/half-complete closing and incomplete fragments.
- Malformed JSON, NaN, unsupported opcodes/fields, invalid FIN/length types, excessive counts/bytes and integer-valued JSON numbers distinguish input failures from protocol findings.
- Node tests invoke the Python contract kernel and compare complete outputs, including before/after state logs and shortest failing prefixes.
- Mocked GenVM tests cover creator authority, source hash/HTTP/size/section bounds, line-bound exact reconstruction, LF/CR/form-feed preservation, disjoint spans, aggregate citation bounds, source-location and stored-quote tampering, substantive citation checks, independent vector disagreement, single-shot source/attestation, UNKNOWN readiness, digest substitution, immutable trace IDs and cross-wallet consumption.
- These mocks exercise deterministic state and callback rejection. They do not prove real model reliability, source availability or validator agreement.

## Reproduction and remaining review

1. Capture the exact official complete RFC source, retaining its bytes and source manifest.
2. Review the exact source SHA before `--deploy`; verify returned deployed code matches it.
3. Run the seven-step application workflow with two distinct project-controlled actors under full validator mode.
4. Retain the actual five-rule profile, four immutable trace records and full execution summaries. Expected trace outcomes are PASS, VIOLATION, INCOMPLETE and INPUT_ERROR; transaction execution is successful for all four because recording a negative trace is a normal application operation.
5. Execute the separate wrong-profile-digest negative test. Its accepted rollback remains VM ERROR and must never be counted as a successful application write.
6. Run archive verification and browser QA of genuine wallet writes, reads, failure handling and recovery. Check source/actor/profile/input bindings and label published snapshots separately from fresh RPC reads.

Steps 1–5 are recorded above. Remaining work is hosted browser wallet QA, external publication and submission by the parent task. A `FINALIZED` badge alone is never treated as VM success; the artifacts retain execution, consensus and immutable readback evidence.
