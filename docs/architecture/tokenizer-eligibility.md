# Tokenizer eligibility

Tokenizer license is not inferred from a model card or from another checkpoint.

`Qwen/Qwen2.5-1.5B-Instruct` at `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` lists `merges.txt`, `tokenizer.json`, `tokenizer_config.json`, and `vocab.json`. Its LICENSE file is Apache-2.0. That text covers a Work indicated by an attached copyright notice, and the notice does not name those tokenizer files. Weight use stays a separate decision. Tokenizer commercial use, redistribution, and modification stay unresolved. Eligibility fails.

`Qwen/Qwen2.5-3B-Instruct` at `aa8e72537993ba99e69dfaafa59ed015b17504d1` lists the same four tokenizer filenames. Its LICENSE file is the Qwen Research License, not the 1.5B Apache-2.0 file. The research grant is non-commercial for Materials, and Materials names trained weights and code. It does not name the tokenizer files. Tokenizer commercial status stays unresolved rather than inherited from the weight grant. Eligibility fails.

`HuggingFaceTB/SmolLM2-1.7B-Instruct` at `31b70e2e869a7173562077fd711b654946d38674` includes tokenizer files and no LICENSE file. `HuggingFaceTB/cosmo2-tokenizer` at `4ce2318a3628e77279c939ed6a9f3f03034402de` has no license field and no LICENSE file. The card's Apache line does not license the tokenizer. Eligibility fails.

`allenai/OLMo-2-0425-1B-Instruct` at `48d788eca847d4d7548f375ad03d3c9312f6139e` includes tokenizer files and no LICENSE file. `allenai/dolma2-tokenizer` at `5292e5d6c0f40b67cc765fe41bec991cf4345b5c` has no license file. Eligibility fails.

`google/gemma-3-1b-it` at `dcc83ea841ab6100d6b47a070329e1ba4cf78752` lists `tokenizer.json` and `tokenizer.model`. The Gemma terms define Gemma as trained weights and parameters and do not name those files. Eligibility fails.

File sizes stay null. No tokenizer file was downloaded. The command is `tokenizer-eligibility-validation`.
