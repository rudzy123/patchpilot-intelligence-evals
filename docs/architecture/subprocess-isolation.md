# Subprocess isolation

Candidate code runs in a child process. The evaluator does not import the fixture into the parent process. The child is started with an argument array and `shell=False`.

## Enforced by this harness

- The entry point is a repository-relative `.py` file. Absolute paths, `..`, shell metacharacters, and path parts named `patchpilot` or `neural-from-scratch` are rejected before launch.
- The working directory is a temporary directory that contains only the copied fixture files. The repository corpus, prior result artifacts, and sibling repository names are not placed there.
- The child environment is limited to `PATH`, `LANG`, `LC_ALL`, `PYTHONUTF8`, `PYTHONIOENCODING`, and `PYTHONDONTWRITEBYTECODE`. Provider credentials are not copied.
- Standard input is one canonical request. The wall-clock limit is 15 seconds. Standard output is limited to 64 KiB and standard error to 16 KiB.
- The runner sends `SIGKILL` to the child process group on timeout or oversize output when the platform permits. If that signal is denied, it kills the direct child.
- There is no retry.
- The child installs the in-process hook on `socket.socket`, `socket.create_connection`, `socket.getaddrinfo`, and `urllib.request.urlopen`. A hooked call exits 86 and is recorded as `network-policy-failure`.
- The child also installs an in-process open hook. It rejects lexical paths for `corpus`, `build` result artifacts, and path parts named `patchpilot` or `neural-from-scratch` before the real open runs.

These limits are evaluation controls. They are not production service-level objectives.

## Not enforced

The runner is not an operating-system sandbox. A later control would be required for:

- process namespaces
- seccomp
- container isolation
- cgroups
- filesystem mount isolation
- user-namespace isolation
- operating-system outbound network enforcement

The open hook does not cover a private system call, a file descriptor opened before the hook, or a nested executable. Those gaps are why this boundary is not an operating-system sandbox.
