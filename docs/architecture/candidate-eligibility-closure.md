# Candidate eligibility closure

Track 6C reassesses the five Track 4 families and selects none. Every weighted score stays null. `scoringApplied` stays false. `qualifyingCandidateCount` is 0.

`Qwen/Qwen2.5-1.5B-Instruct` at `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` has an Apache-2.0 LICENSE file in the pinned revision. Weight use, commercial use, and redistribution pass for that weight instrument. The same text does not name the tokenizer files, so tokenizer provenance fails. The pinned card has no limitations section, and the official Qwen2.5 blog does not add one. Series prose says 128K context. The checkpoint says 32,768 tokens. Use 32,768, and keep the evaluation cap at 8,192. `bounded-subprocess-compatibility` stays fail.

`Qwen/Qwen2.5-3B-Instruct` at `aa8e72537993ba99e69dfaafa59ed015b17504d1` uses a different instrument, the Qwen Research License. Non-commercial weight use is granted. Commercial weight use requires a separate license. That position is clear and does not authorize acquisition. The research text does not name the tokenizer files, so tokenizer provenance fails and is not inferred from the 1.5B Apache-2.0 file. The pinned card has no limitations section.

`HuggingFaceTB/SmolLM2-1.7B-Instruct` at `31b70e2e869a7173562077fd711b654946d38674` still has no LICENSE file. The card's Apache-2.0 section is not the weight license, so weight use, commercial use, and redistribution stay unresolved. The limitations section stands. The published ONNX directory exceeds the artifact cap, so local resource fit fails.

`allenai/OLMo-2-0425-1B-Instruct` at `48d788eca847d4d7548f375ad03d3c9312f6139e` has no LICENSE file. The card states research and educational use, and that restrictive position controls. It does not supply the missing license or a redistribution instrument. The limitations section stands.

`google/gemma-3-1b-it` at `dcc83ea841ab6100d6b47a070329e1ba4cf78752` is covered by the Gemma terms last modified 2026-04-01. Weight use, commercial use, and redistribution are clear and restricted. Section 3.2 reserves remote restriction, so fully offline runtime support fails. The terms do not license source code as a separate instrument, and no safetensors digest is accepted. The model card states limitations and assigns 32K context to the 1B size.

No family passes every mandatory criterion. Selection stays `no-selection`. Acquisition stays `not-acquired`. Conversion stays `not-performed`. Execution stays `not-executed`. `realModelExecuted` and `productionReady` stay false.

The command is `candidate-eligibility-validation`. License instruments are summarized in [candidate-license-closure.md](../provenance/candidate-license-closure.md).
