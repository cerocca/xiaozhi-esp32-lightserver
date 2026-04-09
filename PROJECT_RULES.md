# Project Rules - Xiaozhi ESP32 Server

## Fundamental Rule

Markdown files (`.md`) are updated only on explicit user request.

## Project Philosophy

- do not break what already works
- prefer simplicity and control
- avoid unnecessary or closed dependencies
- keep the design clean, stable, and understandable

## Working Method

- working first, improvement second
- every change must be verifiable
- debug before adding new features
- logs stay high priority
- keep changes small and reversible

## What To Avoid

- unnecessary refactors
- multiple untested changes at once
- introducing unnecessary complexity
- coupling the runtime server too tightly to admin tooling

## Boundary With Admin UI

`xiaozhi-admin-ui` is separate from `xiaozhi-esp32-server`.

Rule:

- the server remains the voice/runtime backend
- the Admin UI remains management tooling

Avoid:

- moving runtime logic into the Admin UI
- treating the Admin UI as part of the server runtime
- introducing strong server dependencies on the UI

## Approach

- iterative
- conservative
- oriented toward a real system, not a demo
- documentation and real runtime state must stay aligned
