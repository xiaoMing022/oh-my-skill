# Adapting a design language to each client

Read only the section matching clients in scope. Locate the existing native
theme owner and installed platform versions first. Use current official or
Context7 documentation for platform/library syntax when needed. The notes here
guide inspection; they do not replace version-specific platform guidance.

## Shared roles, native values

Carry over confirmed meanings such as action, danger, surface, text, focus,
and density. Reuse existing identifiers; matching role names across clients is
helpful but not a reason to rename stable native APIs. Record each native owner
and any necessary mapping. Do not copy Web pixel values mechanically or add a
second active palette. No universal touch-target number/unit applies to all
clients; follow the target platform's guidance and project accessibility needs.

## Responsive Web

Consume the existing CSS/utility/provider tokens. Reflow content using current
breakpoints; preserve keyboard focus, portal theming, and non-hover access.
Check viewport scaling, long text, relevant zoom/reflow, and primary actions at
wide and narrow sizes. Use the existing browser inspection mechanism when
available; HTTP success alone is not visual or interaction verification.

## iOS / Android

Consume the project's native semantic assets/theme values and components.
Use platform layout and type units; respect safe areas/insets, text scaling,
keyboard occlusion, and native back/modal conventions. Match platform guidance
for touch targets rather than interpreting CSS px as pt or dp.
Inspect the implemented screen in an available simulator/device/preview and
exercise its relevant action and navigation states. A Web mockup supports a
visual decision but does not verify a native implementation.

## Mini-program

Consume the actual WXSS/theme owner and observe page/component style scope.
Check the project's px/rpx conventions, safe areas, custom or platform
navigation, keyboard/form behavior, and touch reachability. Prefer existing
platform components and their real event bindings. Use the available target
developer tool/device for runtime evidence; a browser illustration cannot prove
that mini-program lifecycle, styles, or navigation work.

## Desktop client

Identify whether the surface is native or embeds Web content, then use its
actual theme owner. Check resizable window limits, keyboard shortcuts, focus,
menus/dialogs, and platform chrome where affected. Web content inspection alone
does not verify native menus, window behavior, or process bridges.

## Unavailable client tools

Continue authorized source work using the existing stack and readable platform
configuration. Report source inspection, available build checks, and missing
runtime evidence separately. Do not introduce a different platform or claim
native behavior was verified through a browser-only preview.
