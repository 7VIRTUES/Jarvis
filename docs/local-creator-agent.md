# Local Creator Agent

The Local Creator Agent turns user-provided creator, channel, video, audience, platform, production, and content idea notes into structured local planning and drafting suggestions.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize creator and content ideas using only the request body.
- Return manual planning and drafting aids for channel plans, content calendars, video outlines, scripts, hooks, titles, thumbnails, production checklists, and repurposing plans.
- Keep all output non-persistent and non-executing.

## Scope

- Does not access YouTube, TikTok, Instagram, X/Twitter, Twitch, analytics, comments, DMs, accounts, websites, files, connectors, browser, paid API, database, shell, or cloud data.
- Does not upload, post, schedule, scrape, browse, verify trends, read analytics, send messages, create accounts, persist content, create files, or mutate external services.
- Does not claim follower growth, monetization success, trend validation, copyright clearance, brand deal validation, platform compliance, algorithm certainty, certification, or readiness.

## Endpoint

`POST /agents/creator/local-plan`

## Request Body Example

```json
{
  "creatorName": "Local Workshop Channel",
  "platforms": ["Video channel", "Short-form clips"],
  "niche": "Local-first software workflows",
  "audience": "Builders who want practical local tools",
  "contentIdea": "Explain how a local-only planning assistant stays review-friendly.",
  "goals": ["Clarify the idea", "Draft an outline", "Plan repurposing options"],
  "tone": "Practical and clear",
  "formatNotes": "Short explainer with a simple three-part structure.",
  "productionResources": ["Screen notes", "Demo outline"],
  "constraints": ["No platform claims", "No live trend verification"],
  "existingContentNotes": "Previous notes focus on local-only boundaries and manual review.",
  "desiredOutputType": "creator_brief"
}
```

## Supported Output Types

- `creator_brief`
- `channel_plan`
- `content_calendar`
- `video_outline`
- `script_draft`
- `title_thumbnail_ideas`
- `production_checklist`
- `repurposing_plan`

## Safety Boundaries

- Manual-input only.
- Local-only.
- Response-only.
- Drafting and planning only.
- No YouTube/social/account connectors.
- No upload, posting, scheduling, scraping, analytics, messaging, live trend verification, account creation, browser, paid API, file, database, shell, persistence, mutation, or external-service behavior.
- No copyright clearance, platform compliance validation, monetization guarantee, follower-growth claim, trend validation, algorithm certainty, certification, or readiness claim.
- Output is based only on user-provided input.

## Limitations

- Suggestions and drafts are review aids only.
- Copyright, reputation, legal, sponsorship, brand-deal, or sensitive content concerns require appropriate human or professional review.
- The agent does not prove upload readiness, platform compliance, copyright clearance, monetization potential, trend fit, algorithm performance, validation, certification, or readiness.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
