# Architecture and boundaries

## State and authority

Each profile has `OPEN → SOURCE_READY → READY | INCOMPLETE`. Only its creator can capture and attest it. Source capture is single-shot; attestation is single-shot. There is no override of `UNKNOWN`, no model-supplied executable code and no mutable rule definition.

The official endpoint is fixed to `https://www.rfc-editor.org/rfc/rfc6455.txt`. The full 1,000–300,000-byte response is hashed before exact section extraction. Selected sections 5.4, 5.5 and 5.5.1 must be present, ordered, individually bounded and collectively within 26,000 encoded bytes. Over-limit or changed content aborts; nothing is silently truncated. The state retains the full-document hash plus exact selected sections, not just a convenient quotation.

For every semantic attestation each validator independently interprets the complete selected source. The normalized five-row `id/support/condition` vector must match. A separate substantive check evaluates the leader's actual quotes against qualifiers and complete context. Literal membership alone is insufficient. Embedded source text is untrusted data and cannot change the prompt, vocabulary or state machine.

The `rfc6455-bounded-lines-v2` evidence encoding supplies every original selected line with a one-based LF line number. The model selects one to four ordered, non-overlapping inclusive spans per fixed rule. It never retypes a quotation. Contract code reconstructs each quotation directly from those lines and still requires exact membership in the designated frozen section and 20–1,800 combined original characters. LF is the only delimiter: indentation, CR, form-feed page breaks and terminal newlines remain unchanged. The validator reconstructs all proposed bytes again before independent semantic interpretation and the separate substantive audit. A real source location is necessary but does not itself establish support.

Certificate rows retain `spans` and the corresponding code-reconstructed `quotes` array. Browser/archive verification reconstructs the spans independently and rejects changed quote bytes even when an altered certificate has a newly computed digest. The rule meanings and deterministic replay kernel are unchanged from v1. The new evidence format requires a new source hash and deployment; the v1 exact-quote failure, source and deployment records are retained separately.

The certificate digest binds creator, profile ID, source digest, document hash, rule version, and all five semantic rows including their citations. An incomplete vector remains an explicitly incomplete certificate, unavailable for chain replay.

## Trace execution

Any wallet can replay against a `READY` profile by its exact digest. A trace ID cannot be overwritten. Receipts bind input bytes, submitting wallet and profile digest. The input has no arbitrary URL, script, expression or dynamically interpreted opcode. Lengths are bounded integer metadata, not real payload bytes.

Input validation precedes protocol interpretation. An unsupported opcode or malformed field anywhere makes the result `INPUT_ERROR`; it is not used to fabricate a protocol failure. Otherwise the deterministic kernel processes frames in order, maintaining separate `{fragment, sent_close}` state for each sender. It returns at the first violating frame and includes exactly that prefix in the step log. Open fragments or a half-complete Close handshake produce `INCOMPLETE`. Only absence of covered violations with no pending modeled obligation yields `PASS`.

The JS and Python implementations are checked against an independently labelled shared case corpus and against one another's complete replay outputs. Receipt export and verification recompute these results rather than trusting a stored display label.

## Browser lifecycle

Before a write the app checks the deployed source SHA, wallet network and current account. It persists the exact zero-value call intent before entering the SDK, then saves the returned hash before waiting. It never retries broadcasts. Reload recovery only reads the saved transaction, checking sender, destination, exact encoded ABI calldata, zero value and full-validator mode. Completion additionally checks committed majority agreement, successful VM execution and exact immutable read-back data. A known EIP-1193 user rejection is retained and can release an unbroadcast intent; ambiguous errors cannot.

Browser local storage must remain intact. A storage record that cannot be read is not treated as permission to send a replacement. A terminal failed receipt can be retained as failure; a successful call cannot be cleared by calling it failed. Cross-tab storage checks detect changed intents, but the app does not claim a distributed cross-device write lock.

## Claims the system does not make

- It does not compile arbitrary prose or arbitrary RFCs into executable code.
- It does not authenticate packet captures or prove that submitted frame metadata happened on a real network.
- It does not validate masking, byte framing, close-code payload structure, UTF-8, compression, extensions, ping payload equality, timing or liveness.
- It does not certify complete RFC conformance, actual implementations, security, measured uptime or compensation.
- Project demonstrations use synthetic traces and project-controlled wallets; they are not independent user adoption.
- Two implementations sharing a design can share a bug; parity tests are drift checks, not a formal proof or an external certification.
