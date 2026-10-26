# RFCReplay

A GenLayer WebSocket trace workbench. A creator freezes the complete official RFC 6455 document hash. Validators independently attest the cited basis of **five fixed rules**. Other wallets submit synthetic frame sequences against the exact immutable rule certificate. A predefined deterministic kernel produces `PASS`, `VIOLATION`, `INCOMPLETE` or `INPUT_ERROR`, the first violating frame, and the smallest failing prefix of the submitted sequence.

**This is a finite metadata exercise, not arbitrary RFC compilation or a certification of real WebSocket implementations.** No generated code is executed. The profile excludes byte encoding, masking, UTF-8, payload semantics, extensions, network authenticity and timing/liveness. It does not connect to real servers, move funds or award prizes.

## The trust problem

A local test result can silently change with its assumed rules, and a convincing quote can fail to support the rule attributed to it. RFCReplay separates source capture, independent semantic support and deterministic execution. The creator cannot replace the source after capture or edit the accepted rule vector. A trace receipt binds the input bytes, profile digest, rule version, submitting wallet and complete replay result. An incomplete or unsupported rule profile cannot be consumed as complete. Replays are immutable and available to other wallets.

The GenLayer consensus concerns the meaning and cited support of the fixed rule profile. It is **not** used to pick an arbitrary label for each trace. Every trace is replayed in ordinary deterministic code, and the browser independently recomputes the same result.

## Five fixed rules

1. A fragmented message is tracked separately for client and server; a continuation requires an open message and another data message cannot interleave without an extension.
2. Control frames may occur between fragments without becoming data continuations.
3. Control frames have `FIN=true` and payload length at most 125 bytes.
4. A sender cannot send data frames after **it sent** Close. Receiving a peer's Close is not treated as an automatic ban on finishing its current message.
5. After both directions sent Close the bounded connection state is closed; later frames violate the profile.

An unfinished fragmented message is `INCOMPLETE`, even when both sides sent Close. A one-sided Close is also incomplete. A passing finite open trace means only that no covered violation was found in that submitted prefix; it does not prove a complete connection.

## Use the application

The **Trace studio** supports editable JSON exercises, direction-aware frame steps, before/after state inspection and export. Local exercises are visibly labelled and make no chain calls. **Rule evidence** creates, captures and attests a live profile. **Chain ledger** reads immutable trace receipts and distinguishes archived snapshots from live RPC reads.

Live workflow:

1. Inspect the captured official full-document hash and exact selected sections.
2. Connect MetaMask to Studionet 61999. The creator opens a new profile with that hash.
3. Capture the source. Every validator retrieves the fixed official URL and checks the complete-document hash before retaining exact bounded sections.
4. Attest all five rules. The model selects numbered original line spans; code reconstructs exact quotations. Every validator independently derives the support/condition vector and substantively checks the reconstructed passages. `UNKNOWN` yields an immutable incomplete profile, not an implicit pass or automatic reroll.
5. Another wallet loads the complete profile, edits a synthetic frame sequence and records a new trace. Review `PASS`, `VIOLATION`, `INCOMPLETE` or `INPUT_ERROR`, not just the transaction lifecycle.
6. Read the trace ID from another session and verify its profile binding, content digest and exact deterministic replay.

Current actual-chain status: **the repaired v2 workflow and independent expected-rejection test are verified** on [Studionet contract 0x2628ee871f5a0A0391D851C181B493faD3666feb](https://explorer-studio.genlayer.com/address/0x2628ee871f5a0A0391D851C181B493faD3666feb). Its source matched the reviewed SHA. The five-rule profile is `READY`; four immutable traces record `PASS`, `VIOLATION`, `INCOMPLETE` and `INPUT_ERROR` under seven majority-agreed successful recording calls. The wrong-digest call is separately retained as expected `ERROR` rollback. `npm run verify` passes. The earlier v1 quotation failure remains archived. Browser wallet QA, hosting and contribution submission are still pending; see [the execution record](docs/validation.md).

## Run locally

```sh
npm ci
npm test
npm run test:contract
npm run dev
npm run build
```

Use the Sites dependency helper when working in this task's managed Sites workflow. Static output is `dist/`. No private key is bundled. `.local/`, `node_modules/` and `dist/` are ignored.

## Contract interface

```text
open_profile(profile_id, expected_document_sha256)    # creator freezes source identity
capture_source(profile_id)                          # creator; independent fixed-host fetch
attest_profile(profile_id)                          # creator; one-shot semantic certificate
replay_trace(trace_id, profile_id, digest, trace_json) # any wallet; immutable result
get_profile(profile_id)
get_trace(trace_id)
```

Each frame has exactly `sender`, `opcode`, `fin`, `length`. Supported opcodes are text, binary, continuation, ping, pong and close. Valid input is 1–64 frames, at most 20,000 UTF-8 bytes, payload lengths 0–65,535. The entire input schema is checked before protocol replay. Unknown opcodes or fields are `INPUT_ERROR`, not alleged RFC violations. The storage call rejects an input over its bound instead of silently truncating it.

## Live evidence harness

The default is **plan-only**. No chain call is made by `npm run plan`.

```sh
npm run source
npm run plan
node scripts/live-test.mjs --deploy --source-sha=<reviewed-exact-contract-sha256>
node scripts/live-test.mjs --run
node scripts/live-test.mjs --negative
npm run verify
```

The harness only supports Studionet 61999, `value:0n` and `leaderOnly:false`. It creates new project-controlled test actors in ignored `.local/` with restrictive file permissions. Never use a mainnet or funded key. Intent is saved before broadcast; hash is saved before waiting. An uncertain outcome never causes automatic rebroadcast. Resume with the same flags, or match an independently identified transaction using the explicit recovery flags. `FINALIZED` alone is not a successful call: receipts must establish majority agreement and successful VM execution. Negative tests retain their `ERROR` rollback outcome separately.

See [architecture](docs/architecture.md), [validation](docs/validation.md) and [submission draft](docs/submission-draft.md).

## Attribution and source rights

Transport, receipt parsing, paced reads and resumable journal patterns are adapted from the same author's IncidentDesk. RFCReplay's bounded protocol state machine, rule attestation, trace receipts, interface and tests are new work. It is not a starter-template fork or a resubmission of the author's other contracts.

Application code is MIT licensed. Captured RFC material retains its original IETF Trust copyright and [RFC document license](https://www.rfc-editor.org/rfc/rfc6455.html); it is not relicensed as application code. The capture retains the complete original text and notices.
