# FP32 memory measurement

The resident ceiling is cgroup `MemoryMax` `12884901888` with `MemorySwapMax=0` and `TasksMax=32`. `RLIMIT_AS` is address space. Measurement sets it to `25769803776`, twice the resident ceiling, so the address-space limit is not the resident control.

The host samples the systemd user scope every 100 milliseconds. The sample reads `memory.current`, `memory.peak`, and `memory.events`, plus `VmRSS` and `VmSize` for every PID in that scope. RSS, cgroup current, cgroup peak, and virtual size are separate fields. `ru_maxrss` may be recorded and is not the peak. A missing `memory.peak` is unresolved and stops the session.

The child is in a cgroup namespace, so it cannot observe the host `memory.peak`. The parent samples. After the scope is reaped, any remaining cgroup process is `cleanup: failed`.

Context phases use batch size 1, an input of the stated token-id count, and at most one new token. Token count is the length of the token-id vector. Each context phase records one cold session invocation and one warm session invocation in the same process. The 8,192-token phase is withheld when the 4,096-token record did not pass. An out-of-memory event is a measured failure. The ceiling is not raised.

Intra-op threads are 8 and inter-op threads are 1 so `TasksMax=32` stays above the thread pools. Those caps are a deviation from library-default session options and are part of the sealed plan. Telemetry is disabled. No execution provider is appended.
