# Template compatibility

Chat-template compatibility is a closed check. It verifies the template digest, parses one explicit subset, renders a bounded synthetic user turn, checks the rendered prompt shape, and records the rendered-output digest.

The check fails closed for an identity mismatch, an unsupported template construct, a rendering failure, an invalid rendered prompt, or a tokenizer failure. Spaces around supported operators do not decide compatibility. The verified template bytes stay the publisher bytes.

The check does not create a model session, call Run, load the model graph, or contact a model hub.
