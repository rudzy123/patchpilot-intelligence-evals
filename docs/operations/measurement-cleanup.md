# Measurement cleanup

The hardened launcher reaps the systemd user scope after each phase. Cleanup is `reaped` only when the scope is inactive and no cgroup task remains. A remaining task is `cleanup: failed`, and the session stops.

The external result root is the retained measurement record. It is not committed. The work directory created for one launch is removed after the report is read. Promoted runtime and candidate trees are not deleted by measurement. Quarantine archives stay unexecuted.

Cleanup does not change `selectionOutcome`, `calibrationStatus`, `installationAuthorized`, or `productionReady`.
