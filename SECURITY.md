# Security

This repository stores synthetic evaluation fixtures and an offline harness. It is not a production service and it does not hold tenant data by design.

## Accidental sensitive data

If a case, result, log, or commit contains a real credential, tenant identifier, customer record, raw SBOM, or raw advisory payload:

1. Report it to the repository maintainers through a private GitHub security advisory.
2. Do not open a public issue that contains the data.
3. Do not paste the data into chat, logs, or a pull request description.
4. Remove the data in a follow-up change after a maintainer reviews it.
5. Leave published history unchanged unless a maintainer decides otherwise. A report does not mean existing clones have been purged.

## What the controls actually do

- Corpus validation rejects probable credential patterns, connection strings, email addresses, IP addresses, and `http` or `https` URLs whose host does not end in `.invalid`. A rejected pattern is not proof that no real identifier exists.
- Evaluation and tests install an in-process hook on `socket.socket`, `socket.create_connection`, `socket.getaddrinfo`, and `urllib.request.urlopen`. Direct use of the private socket implementation, a subprocess that does not go through the candidate runner, or a socket opened before the hook is outside this control. This is not seccomp, a network namespace, or a firewall.
- Paths that lexically leave the repository root are rejected before this package opens them. The check does not resolve `../patchpilot` or `../neural-from-scratch`. Symlinks and already-open file descriptors are outside this control.
- Application code in this package reads environment variables only through an explicit tooling allowlist. The interpreter and development tools still see the process environment. Provider credentials are not on the allowlist.
- Logs from evaluation may contain case identifiers, metric names, and statuses. They omit assistance-request text and explanation bodies.

## Candidate subprocess

The candidate runner is a separate Python process. It is not a container and it is not an operating-system sandbox.

The harness enforces an argument array with `shell=False`, a temporary working directory that contains only the copied fixture files, a minimal environment, a 15-second wall-clock limit, a 64 KiB standard-output limit, a 16 KiB standard-error limit, one request, and no retry. On timeout or oversize output it sends `SIGKILL` to the child process group when the platform permits, and otherwise kills the direct child. The child installs the same Python socket, DNS, and urllib hook, and an open hook that rejects corpus paths, prior result artifacts, and sibling repository names. A hooked network call exits 86 and is classified as `network-policy-failure`.

The harness does not enforce process namespaces, seccomp, containers, cgroups, filesystem mount isolation, user namespaces, or operating-system outbound network policy. Symlinks, raw system calls, file descriptors opened before the hook, and a nested executable are outside the Python hook.

## Real-candidate boundary

Track 5 does not acquire a model or execute one. The cache policy stores rules only. A caller passes a repository-external root, and quarantine cannot execute, load a tokenizer, or load a model.

Artifact verification compares expected and observed names, sizes, and SHA-256 values. Executable detection is limited to mode bits, a shebang, and ELF magic. That check is not malware detection.

The real-candidate profile can set `RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_FSIZE`, `RLIMIT_NOFILE`, and `RLIMIT_NPROC` on a child. `RLIMIT_AS` limits address space, not resident memory. `RLIMIT_NPROC` is a per-user limit. Read-only mounts, hidden home and credential files, and operating-system network denial are deferred acquisition blockers on that profile. Those limits and the Python hooks are not an operating-system sandbox.

## Hardened fixture launcher

Synthetic fixtures can run through a separate launcher: bubblewrap namespaces inside a transient systemd user scope. That launcher is the operating-system boundary for those fixtures. It does not replace the candidate runner above. The candidate runner still has no namespace, cgroup, or operating-system network denial.

The launcher keeps a private network namespace. Host loopback, external IPv4, external IPv6, DNS, and host Unix sockets outside the mount are denied. Sandbox-local loopback comes up with the namespace; a connection there is refused by the absence of a listener, and seccomp does not currently block `socket`. Seccomp stays unproven. `MemoryMax` limits cgroup memory. `RLIMIT_AS` limits address space. `TasksMax` limits process count. `RLIMIT_NPROC` is not used as a private process limit.

The launcher mounts a staged interpreter, the fixture, read-only synthetic inputs, and a private result directory. It does not mount the repository root, home directory, or credential directories. The child environment is an allowlist. Attestations omit host names, user names, addresses, and environment values. The launcher does not execute a model. `productionReady` stays false.

## External runtime root

A future ONNX Runtime archive would be staged outside this repository, outside the model-artifact cache, and outside the output directory. The committed policy stores no host path. Quarantine and rejected trees cannot be executed. Promotion requires a verified inventory. Shared libraries must be ELF. Other staged files must not be executable. `malwareDetectionClaimed` stays false. These checks are not an operating-system sandbox. No runtime archive is present, and installation stays unauthorized.

## Track 6D readiness

Track 6D acquisition readiness is `not-ready`. The record does not authorize runtime installation, model or tokenizer acquisition, model conversion, candidate selection, or real inference. Validation reads local records only.

## Supported use

Offline harness checks and future offline candidate runs inside this repository. Do not use these fixtures for production decisions.
