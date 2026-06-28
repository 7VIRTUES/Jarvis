# Local Online Presence Agent

The Local Online Presence Agent turns user-provided profile, platform, audience, tone, strength, project, content idea, constraint, and reputation concern notes into structured local planning and drafting suggestions.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize online presence notes using only the request body.
- Return manual drafting and planning suggestions for bios, profile reviews, content plans, portfolio positioning, personal brand plans, reputation reviews, and posting drafts.
- Keep all output non-persistent and non-executing.

## Scope

- Does not access LinkedIn, X/Twitter, Instagram, TikTok, YouTube, GitHub, websites, analytics, DMs, comments, email, contacts, external accounts, connectors, browser, paid API, file, database, shell, or cloud data.
- Does not scrape, browse, post, schedule, upload, create accounts, send messages, read analytics, verify live reputation, inspect public profiles, or mutate external services.
- Does not claim brand success, follower growth, hiring results, reputation verification, platform compliance review, public posting, validation, certification, or readiness.

## Endpoint

`POST /agents/online-presence/local-plan`

## Request Body Example

```json
{
  "profileName": "Local Portfolio Profile",
  "platforms": ["Portfolio site", "Professional profile"],
  "currentBio": "Builder of practical local-first tools and documentation.",
  "goals": ["Clarify positioning", "Draft profile copy", "Plan a few content ideas"],
  "targetAudience": "Collaborators and reviewers interested in local-first software",
  "tone": "Clear, grounded, and practical",
  "strengths": ["Local-first product thinking", "Careful documentation", "Review-friendly implementation"],
  "projects": ["Local assistant dashboard", "Manual evidence runbooks"],
  "contentIdeas": ["Explain a local-only design choice", "Share a short project lesson"],
  "constraints": ["No hype", "No live profile verification"],
  "reputationConcerns": ["Avoid unsupported claims"],
  "desiredOutputType": "presence_brief"
}
```

## Supported Output Types

- `presence_brief`
- `bio_draft`
- `profile_review`
- `content_plan`
- `portfolio_positioning`
- `personal_brand_plan`
- `reputation_review`
- `posting_drafts`

## Safety Boundaries

- Manual-input only.
- Local-only.
- Response-only.
- Drafting only.
- No social, platform, account, analytics, email, contact, connector, browser, paid API, file, database, shell, posting, scheduling, messaging, scraping, upload, account creation, or external-service behavior.
- No persistence.
- No execution.
- No live reputation, profile, platform, compliance, hiring, follower-growth, or brand-success validation.
- Output is based only on user-provided input.

## Limitations

- Suggestions and drafts are review aids only.
- Sensitive reputation, legal, employment, identity, or public-claims concerns require appropriate human or professional review.
- The agent does not prove posting, scheduling, account access, analytics review, public-profile verification, platform compliance, reputation status, validation, certification, or readiness.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
