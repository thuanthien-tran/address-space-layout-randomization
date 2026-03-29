# Threats to Validity

This section summarizes key validity risks for the ASLR evaluation and how we mitigated them.

## Internal Validity

- **Exploit reliability depends on local runtime details.** Small changes in compiler, flags, libc, and stack layout can change exploit behavior.
- **Mitigation:** We fixed environment parameters, documented flags in `REPRODUCIBILITY.md`, and used repeated trials (`N=200` or `N=500`) instead of single-run claims.

## Construct Validity

- **Success signal definition can be ambiguous.** Interactive shell output may vary across environments.
- **Mitigation:** We use an explicit marker format (`uid=\d+`) for success detection and document that this is a code-execution indicator in the demo context.

## External Validity

- **Results are environment-specific.** Findings were produced on Linux x86-64 with specific toolchain/runtime.
- **Mitigation:** We report assumptions and limitations explicitly and avoid broad claims beyond the tested setup.

## Statistical Conclusion Validity

- **Finite sample uncertainty.** Entropy and success rates are estimates from finite runs.
- **Mitigation:** We report sample sizes, Shannon/unique entropy estimates, and bootstrap confidence intervals.

## Reproducibility Risk

- **Manual setup errors (CRLF/LF, permissions, local edits) can break scripts.**
- **Mitigation:** Added one-shot runners, quick runner, and artifact packing script; documented common failures and fixes.
