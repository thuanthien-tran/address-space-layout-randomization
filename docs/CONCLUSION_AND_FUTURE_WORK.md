# Conclusion and Future Work

## Conclusion

The project demonstrates a clear mitigation story for stack-based exploitation:

- With ASLR disabled, a stack-overflow payload is reliable in this controlled setup.
- With ASLR enabled, fixed-address exploitation fails consistently.
- With an information leak, exploit reliability recovers despite ASLR.
- Quantitatively, observed success probability drops from high/off to near-zero/on for fixed-address attacks.
- PIE increases code-address variability relative to non-PIE.

Overall, the experiments support the claim that ASLR materially reduces exploit reliability, but does not fully prevent exploitation when strong primitives (for example, information leaks) are present.

## Limitations

- Runtime-specific behavior (toolchain, libc, loader) affects exploit reliability.
- ROP phase may vary by available gadgets and libc/runtime details.
- Entropy estimates are empirical and finite-sample.

## Future Work

- Add an automated ret2win fallback path for environments where ret2libc is unstable.
- Extend evaluation to other architectures (ARM64) and 32-bit targets.
- Compare additional mitigations: canary, RELRO, CET/IBT, CFI.
- Add power-analysis-based sample sizing for entropy/probability studies.
- Integrate CI scripts that run quick-mode reproducibility checks on every commit.
