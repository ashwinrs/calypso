# Calypso

Use the [Calypso Podcast Clips skill](.agents/skills/calypso-podcast-clips/SKILL.md) for podcast work, including step-by-step guidance. Run the commands documented in [README.md](README.md) from the repository root.

Keep transcription local and preserve the source recording. Propose clip IDs and wait for the user's selection before rendering final exports. Treat all clip and speaker-turn timestamps as seconds from the start of the source, including when a clip starts partway through a speaker turn.

Build episode context before proposing clips. Flag complete story arcs that span multiple source intervals and identify the material to keep and cut.

Ask the user to choose whenever there is more than one viable way to plan, script, or render a clip. Recommend an option and wait before implementing the unresolved choice. Record reusable editing preferences in the repository skill.

Use synthetic media for regression checks. Keep recordings, transcripts, local models, and exports out of Git.

## Git workflow

Create a dedicated branch from `main` before editing Calypso. Validate and commit the changes on that branch, then merge the branch back into `main`.
