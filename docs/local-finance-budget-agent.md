# Local Finance / Loans / Budget Agent

The Local Finance / Loans / Budget Agent turns user-provided finance notes about budgets, student loans, debt payoff, rent affordability, Boston move costs, cash-flow planning, savings, spending, and financial decision checklists into structured local planning suggestions.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize budget plans, loan reviews, debt-payoff planning, move budgets, cash-flow reviews, savings plans, spending reviews, and decision checklists using only the request body.
- Return manual planning and checklist aids without checking banks, credit cards, loan servicers, brokerages, payment apps, tax portals, FAFSA, school financial-aid systems, files, accounts, or external sources.
- Keep all output non-persistent and non-executing.

## Scope

- Does not access banks, credit cards, loan servicers, Webull, brokerages, credit reports, tax portals, FAFSA, school financial-aid systems, payment apps, files, connectors, browser, paid API, database, shell, or cloud data.
- Does not make payments, transfer money, place trades, make purchases, apply for loans, submit forms, connect accounts, read statements, create tasks, persist records, create files, or mutate external services.
- Does not claim financial-advisor, tax, legal, credit, accounting, investment, loan-approval, repayment-certainty, affordability, savings, market, validation, certification, or outcome certainty.

## Endpoint

`POST /agents/finance-budget/local-plan`

## Request Body Example

```json
{
  "profileName": "Local Finance Plan",
  "financialGoal": "Prepare a manual budget for Boston move costs, student loans, and savings.",
  "incomeNotes": "Monthly income estimate from user-provided notes only.",
  "expenseNotes": "Recurring food, transit, phone, utilities, and school-related costs.",
  "debtNotes": "Student loan and small revolving balance notes for manual review.",
  "loanNotes": "Student loan repayment options need official servicer confirmation.",
  "rentHousingNotes": "Compare rent affordability for shared Boston housing.",
  "moveCostNotes": "Estimate deposit, first month, moving supplies, and transit setup.",
  "savingsNotes": "Build a small emergency cushion before optional spending.",
  "spendingNotes": "Review dining out, subscriptions, and hobby spending manually.",
  "constraints": ["Manual planning only", "No account connections or live balance checks"],
  "priorities": ["Avoid missed payments", "Protect move-in cash cushion"],
  "desiredOutputType": "finance_brief"
}
```

## Supported Output Types

- `finance_brief`
- `budget_plan`
- `loan_review`
- `debt_payoff_plan`
- `move_budget`
- `cashflow_review`
- `savings_plan`
- `spending_review`

## Safety Boundaries

- Manual-input only.
- Local-only.
- Response-only.
- Planning and checklists only.
- No bank/credit-card/loan/brokerage/payment/tax/financial-aid/account connectors.
- No payments, trades, transfers, purchases, applications, submissions, account connections, statement reads, scraping, browsing, live verification, file access, paid API, database, shell, connector, persistence, mutation, or external-service behavior.
- No persistence.
- No financial, tax, legal, accounting, investment, credit, loan-approval, repayment-certainty, financial-advisor, affordability, savings, market, validation, certification, or outcome claim.
- Output is based only on user-provided input.

## Limitations

- Suggestions and checklists are review aids only.
- Debt, taxes, legal agreements, credit, investments, private loans, FAFSA, student loans, and other high-stakes financial decisions require official or qualified professional confirmation.
- The agent does not prove budget accuracy, repayment ability, loan eligibility, aid eligibility, credit impact, tax treatment, legal position, investment suitability, accounting treatment, validation, certification, or readiness.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
