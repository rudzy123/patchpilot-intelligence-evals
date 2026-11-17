# Corpus continuation boundary

Track 9 authorizes one future corpus-only Session in principle. The record is [corpus-continuation-authorization.json](../../candidates/authorization/corpus-continuation-authorization.json).

That later Session reuses the accepted memory evidence and does not repeat the 4,096-token or 8,192-token measurements. It uses the same verified runtime, candidate, corpus, prompt template, response schema, metrics, and gates. It runs all 24 cases, three repetitions each, for 72 runs, under one new result identity.

Raw candidate output is retained inside the existing 65,536-byte stdout limit. It stays external during execution, immutable, digest-identified, and associated with the case and repetition. Raw output is distinguished from extracted and parsed output. Parse errors, response-schema errors, truncation, and output-limit behavior are recorded, and failure authority is classified. Gold and evaluator records stay hidden from the candidate and from later runs. Host paths and machine identity stay out of the retained evidence.

The later Session needs a new specification, a new plan digest, a fresh empty result root, and a new operator checkpoint. This record does not issue that plan, that digest, or that approval. The Session stops on memory, network, isolation, output, cleanup, identity, or telemetry failure.

`selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. The later Session does not select or promote the candidate.

Prerequisites are in [corpus-only-continuation-prerequisites.md](../operations/corpus-only-continuation-prerequisites.md).
