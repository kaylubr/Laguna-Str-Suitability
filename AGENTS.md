# Memory

## Project Overview

See @README.md for project overview and @package.json for available npm/pnpm commands for this project.

## Code Style Guidelines

- Use descriptive variable names
- Follow existing patterns in the codebase
- Extract complex conditions into meaningful boolean variables
- Do not use comments
- Keep implementation concise and avoid unnecessary abstractions

## Architecture Notes

- The system follows the research workflow: data collection and integration → preprocessing → spatial grid construction → spatial feature engineering → Random Forest regression → model evaluation and feature importance → indicator normalization → Entropy Weight Method → composite suitability scoring → suitability classification → geographic visualization.
- Keep Random Forest prediction separate from composite suitability scoring. Random Forest predicts STR revenue and occupancy; it does not directly produce the final suitability score.
- Use grid cells as the primary spatial units for the final suitability assessment.
- Keep data-processing, model-training, suitability-scoring, and visualization responsibilities separated.
- External datasets should be integrated through well-defined data transformations rather than hardcoded values.
- Avoid introducing variables, methods, or outputs that are not part of the research methodology without documenting the architectural reason.

## Common Workflows

- The commits should be atomic, 1 feature per commit. Make sure to commit per feature, not all at once.
- Do not use trailing commits. Be concise with commits.
- Run the relevant tests or validation checks before committing.
- Keep commits focused on one logical change.
