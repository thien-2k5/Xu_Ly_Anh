# Project Design And Figma-To-Code Rules

These rules were created for the FaceTrust codebase using the installed Figma design-system workflow skills. No Figma MCP file is connected in this workspace yet, so these rules define how future Figma-driven implementation should map into this project.

## Product Tone

- FaceTrust is a serious security and evidence product, not a playful photo editor.
- The first screen must be the usable console.
- Avoid landing-page hero sections unless explicitly requested.
- Avoid decorative visual noise, gimmicks, masks, glasses, face grids, or claims that are not backed by proof.

## UI Structure

- Use `src/anti_deepfake/static/index.html`, `src/anti_deepfake/static/styles.css`, and `src/anti_deepfake/static/app.js` for the current vanilla frontend.
- Keep components as clear page regions: topbar, upload workflow, candidate list, proof recorder, report actions.
- Do not put cards inside cards.
- Use 8px radius or less for panels and controls.
- Keep dense operational layouts readable on desktop and mobile.

## Design Tokens

- Define colors, spacing, radii, and shadows as CSS custom properties in `:root`.
- IMPORTANT: Do not hardcode repeated hex colors throughout the CSS. Add or reuse a token.
- Use neutral backgrounds with a limited accent palette for actions and verdicts.
- Avoid one-note purple, dark-blue-only, beige, or orange/brown palettes.

## Interaction Rules

- Upload controls must be real labels or buttons, not non-clickable visual blocks.
- Every generated candidate must have a clear download action.
- Every protection claim must point to either an internal metric or an external proof record.
- Pass, fail, and invalid states must be visually distinct and textually explicit.

## Figma MCP Integration Rules

When a Figma file or selected node is provided later:

1. Run `get_design_context` for the exact node.
2. Run `get_screenshot` for visual reference.
3. If context is too large, run `get_metadata`, then fetch only the required nodes.
4. Download assets returned by the Figma MCP server.
5. Translate Figma output into this vanilla HTML/CSS/JS structure unless the project framework changes.
6. Map Figma colors and spacing to CSS variables.
7. Validate implemented UI against the screenshot before completion.

## Accessibility

- All interactive controls need accessible labels.
- Buttons and links must have visible focus states.
- Text must not overflow buttons, cards, or narrow mobile viewports.
- Color must not be the only signal for verdicts.

## Testing

- Run `ruff check src tests`.
- Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` to avoid plugin-related hangs.
- For frontend changes, start the local web server and verify the console in a browser.
