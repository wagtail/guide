# Content Freshness Skill: AI Agent Instructions

## Purpose
This skill identifies which Wagtail User Guide pages require updates to text or screenshots after a new release. It performs a **semantic comparison** between release notes and the guide's content to produce a maintenance checklist.

## ⚠️ Critical Constraint
**DO NOT suggest changes to pages within the `/releases/` directory.** Release notes are historical records of a specific version and should not be modified. Focus exclusively on updating the "How-to," "Tutorials," and "Reference" sections of the guide.

## Data Sources
- **Release Notes**: `prompts/content/en-latest/releases/new-in-wagtail-X.Y.md`
- **Guide Context**: `prompts/content/en-latest/llms-full.txt`

## Instructions for the AI Agent

### 1. Analysis Filter
Extract changes from the Release Notes that affect **Content Editors, Moderators, or Administrators**.
- **Include**: UI changes, new features, modified workflows, new settings.
- **Exclude**: Developer-only changes (APIs, CLI, dependencies) and existing Release Note pages.

### 2. Semantic Matching & Prioritization
Compare features against `llms-full.txt`. Do not use generic keyword matching; map the *intent* of the feature to the relevant guide page.
- **HIGH**: UI has visually changed (Screenshots are definitely outdated).
- **MEDIUM**: A new feature/setting exists that the page doesn't mention yet.
- **LOW**: Minor tweaks or bug fixes with minimal visual impact.
- **NEW PAGE NEEDED**: Feature is entirely undocumented in the current guide.

### 3. Required Output Format
Provide results EXACTLY in this format:

[PRIORITY] Page Title
URL: https://guide.wagtail.org/en-latest/...
Reason: [Specific change from release notes]
Suggested Note: [Content for a VersionNoteBlock]
Screenshots: [Yes / No / Maybe]

### 4. Summary
End with a tally of total pages to review, categorized by priority, and an estimated update time (assume 30m per LOW, 1h per MEDIUM, 2h per HIGH).