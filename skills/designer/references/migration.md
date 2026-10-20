# Migrating a design system in stages

Read only for a broad rebrand, theme cleanup, or shared component migration.
A local feature does not need this workflow. Use current authorization and
incoming decisions; this plan is not an additional approval gate.

## Inventory the affected surface

Identify the target apps/clients, consumed theme owners, shared primitives,
representative screens, overlays, supported modes, and intentional exceptions.
Find actual imports/providers and consumers before replacing a token or API.
Record a compact table in the existing design record:

| Source or primitive | Consumers in scope | Target owner | Compatibility/removal condition | Representative check |
| --- | --- | --- | --- | --- |
| Current semantic role/component | Actual app/screens | Existing native theme or shared primitive | Consumers migrated; old role no longer used | Main screen plus another shared consumer |

Distinguish intended branding differences from accidental drift. Do not migrate
a neighboring app merely because it shares a repository.

## Execute by dependency

1. Confirm the target rules from current project authority, supplied references,
   or a single missing-theme fork. Reuse a supplied/delegated direction.
2. Plan small batches: semantic roles and compatibility mapping, shared
   primitives, one representative screen, remaining consumers, obsolete sources.
   Keep the app usable between batches. Avoid a repository-wide text replacement
   of raw colors, sizes, or class names whose meanings differ.
3. Where both APIs must coexist temporarily, map the old names to the target
   native authority with a documented removal condition. A temporary alias is
   not a second palette. Do not create compatibility machinery if one atomic
   scoped edit safely covers all consumers.
4. Migrate one representative slice including a meaningful interaction/error
   state. Inspect another consumer of any changed shared primitive, and relevant
   layout/theme variants, before propagating the pattern.
5. Track each batch as pending/migrated/checked/deferred with source paths.
   Remove obsolete definitions only after confirming no relevant consumers
   remain; retain deliberate exceptions with reasons.

If a batch introduces a regression, isolate and correct or revert only your
batch's edits. Preserve pre-existing and concurrent work; never reset the entire
working tree. A newly discovered app or requirement that expands scope belongs
under `Pending`, with its effect explained.

## Completion

Check the affected import paths, consumers, key interactions, theme modes, and
representative layouts in proportion to the migration. Record what was actually
inspected/run and what could not be checked. Complete only the requested scope;
name any deferred consumers and remaining compatibility aliases. Pass these
details using the six-field handoff when work continues elsewhere.
