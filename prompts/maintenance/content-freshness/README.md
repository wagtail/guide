# Content Freshness Skill

An AI-powered system for maintaining the [Wagtail User Guide](https://guide.wagtail.org) after each new release.

## Overview
This skill identifies documentation pages and screenshots that have become outdated due to new Wagtail features. It uses an AI agent to perform a semantic comparison between new release notes and the existing guide content.

## File Structure
- `content-freshness.md`: The "brain" of the skill. Contains the core logic, analysis filters, and output constraints for the AI Agent.

## Workflow
To use this skill, provide the AI agent with the contents of `content-freshness.md` along with the specific **Release Notes** and **Guide Context** (`llms-full.txt`) for the version you are auditing.

## Maintenance Rules
* **Do Not Edit Releases**: The AI is strictly instructed to never suggest changes to pages within the `/releases/` directory, as these are historical records.
* **Screenshot Priority**: Any change involving a UI update is automatically flagged as **HIGH** priority to ensure visuals remain accurate.
* **User-Facing Focus**: The analysis filters out developer-specific changes (APIs, CLI updates) to focus purely on the experience for Editors and Administrators.