# Candidate evidence closure

Track 5 records a new closure in [candidate-evidence-closure.json](../../candidates/authorization/candidate-evidence-closure.json). The accepted shortlist in [candidate-shortlist.json](../../candidates/authorization/candidate-shortlist.json) stays the Track 4 record.

The closure revisits the five pinned revisions. One gap changes: `Qwen/Qwen2.5-3B-Instruct` at `aa8e72537993ba99e69dfaafa59ed015b17504d1` now has an agreed upstream identity for each safetensors shard. The pinned revision API lists one SHA-256 per shard. No concatenated digest is published. Those values are upstream identities. This repository has not downloaded the files.

The other Track 4 gaps stay unresolved. A model card, a related model, a mirror, or a directory listing does not close a license or tokenizer gap. Qwen limitations stay failed. SmolLM and OLMo still have no LICENSE file in the pinned tree, and their tokenizer licenses stay unresolved. Gemma still lacks a tokenizer grant, a single accepted digest, and an offline grant that does not reserve remote restriction. The disputed Gemma hash is not stored.

Qwen tokenizer provenance stays pass. The residual is recorded: the LICENSE text does not enumerate tokenizer filenames, and the files are in the licensed revision. The Qwen 3B research license states a clear non-commercial position. That position is not acquisition authorization.

`bounded-subprocess-compatibility` stays fail while the isolation profile has an acquisition blocker. Every weighted score stays null. The selection stays `no-selection`. Acquisition stays `not-acquired`, execution stays `not-executed`, and `productionReady` stays false.
