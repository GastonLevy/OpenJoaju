# AGENTS.md

* Keep changes strictly limited to the requested scope.
* Do not add unrelated refactors, features, or architecture.
* Prefer simple, readable, and maintainable code.
* Avoid new dependencies unless clearly necessary.
* Do not make assumptions about future requirements.
* Avoid long explanations unless explicitly requested.

* Use the project virtual environment at `.venv` for Python commands and dependency installation.
* Python is the current implementation language.

* Follow the project architecture and conventions documented under `docs/`.
* Keep networking modules independent from each other. Do not introduce dependencies between modules unless explicitly required by the architecture.
* Keep discovery, monitoring, state management, and presentation concerns separated.

* OpenJoaju is currently read-only. Do not modify Linux networking configuration unless explicitly requested.

* Prefer Linux kernel interfaces and native Python standard-library functionality when practical.
* Avoid parsing external command output when the same information is directly available from the system or kernel.
* Prefer event-driven monitoring when Linux provides an appropriate event mechanism.
* Do not introduce polling when an appropriate event-driven mechanism is available.

* DTOs must contain structured data and remain independent from CLI or other presentation formatting.

* Preserve existing public behavior unless the requested change explicitly requires modifying it.