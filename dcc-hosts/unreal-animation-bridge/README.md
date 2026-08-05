# Unreal Animation Bridge

Public-safe bridge from Maya animation continuity facts to Unreal AnimSequence readiness.

R24 scope:

- Read the R23 Maya Animation Continuity L3 artifact.
- Compare Maya take facts against a public Unreal animation bridge fixture.
- Probe Unreal Python runtime for animation APIs and expected AnimSequence / Skeleton assets.
- Export contract and readiness artifacts without creating production assets.

The first runtime gate is intentionally allowed to be `Blocked`: the public Unreal project has StaticMesh evidence today, but no committed skeletal animation fixture yet.
