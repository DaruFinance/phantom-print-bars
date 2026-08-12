# Lock hashes

The plan file is frozen at the digest below. Editing it invalidates the hash. A revision
must be a new `-vN` sibling with its own row, never an in-place edit.

| File | SHA-256 | Stamped (UTC) |
|---|---|---|
| `analysis-plan-locked.md` | `fea07f417534bebe07c6e8513a16bf4453fd4b9dcfc462270009cacfebce3c79` | 2026-08-12T16:47:52Z |

Verify:

```bash
sha256sum preregistration/analysis-plan-locked.md
```

## Design freeze timeline

The digest above fixes the released text. The freeze itself is evidenced by the commit
history of the private research repository, summarised here so a reader can see the
ordering without access to it.

| Date | Event |
|---|---|
| 2026-06-26 | Endpoint and constants committed. The `PRE-SPECIFIED DEFAULTS` block naming the rank-IC gap as the primary endpoint is fixed on this date. |
| 2026-06-30 | Last commit that could have touched the design. The endpoint and constants are byte-identical to 2026-06-26. |
| 2026-07-23 | Full-universe walk-forward starts. |
| 2026-07-26 | Full-universe statistics stage completes, producing `reproduce/results.json`. |
| 2026-08-12 | Plan transcribed from the frozen source and hashed. |

Four weeks separate the last commit that could have changed the design from the start of
the full-universe run. Analyses added after the freeze are listed under "Post-lock
additions" in the plan and are marked in the paper as confirmatory rather than
pre-registered.
