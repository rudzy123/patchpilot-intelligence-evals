# Linux isolation capabilities

Command presence is not enforcement. A probe is `enforced` only when a harmless behavioral check succeeds and the evidence class is `behavior-proven`. A present command with no successful behavior check stays `unsupported` with evidence `command-present-unproven`. A missing command stays `unavailable` with evidence `command-missing`. A probe that runs and fails stays `failed` with evidence `probe-failed`.

The committed record is [sandbox-capability-report.json](../../candidates/authorization/sandbox-capability-report.json). It records Linux `x86_64`, `realModelExecuted` false, and `productionReady` false. It omits host names, user names, addresses, environment values, and identity-bearing paths.

Proven on the evaluation host with bubblewrap `0.11.1`:

- user, mount, pid, network, ipc, uts, and cgroup namespaces
- bubblewrap itself
- a transient systemd user scope, systemd `259`
- cgroup v2
- `RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_FSIZE`, and `RLIMIT_NOFILE`

`RLIMIT_AS` is virtual address space. It is not the resident-memory control.

Recorded without enforcement:

- rootless Podman and rootless Docker are `unavailable` because the commands are missing
- `unshare` `2.41.3` is `failed`; `unshare --user --map-root-user` did not establish a user namespace
- direct writes to this process's cgroup `memory.max`, `pids.max`, and `subtree_control` are `failed`
- `RLIMIT_NPROC` is `unsupported` because it is per-user, with evidence `per-user-not-private`
- bubblewrap's seccomp flag is `unsupported` with evidence `command-present-unproven`; the flag alone is not a filter

The user namespace that bubblewrap established is a one-UID identity map with `setgroups` denied. `newuidmap` and `newgidmap` are absent. Effective capabilities inside that namespace are empty. The sandbox command is not required to be PID 1; bubblewrap's supervisor occupies PID 1 and the fixture is PID 2.

These probes do not change AppArmor, sysctl, groups, packages, or services. A non-Linux host records every probe `unavailable` and does not launch a fixture. A skip on a runner without bubblewrap or a user systemd session is not stored as `enforced`.
