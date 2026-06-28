from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_finance_budget_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_finance_budget_planning"
SUPPORTED_OUTPUT_TYPES = (
    "finance_brief",
    "budget_plan",
    "loan_review",
    "debt_payoff_plan",
    "move_budget",
    "cashflow_review",
    "savings_plan",
    "spending_review",
)


@dataclass(frozen=True)
class LocalFinanceBudgetRequest:
    financial_goal: str
    profile_name: str = ""
    income_notes: str = ""
    expense_notes: str = ""
    debt_notes: str = ""
    loan_notes: str = ""
    rent_housing_notes: str = ""
    move_cost_notes: str = ""
    savings_notes: str = ""
    spending_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    desired_output_type: str = "finance_brief"


class LocalFinanceBudgetAgentService:
    def create_plan(self, request: LocalFinanceBudgetRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local finance profile"
        financial_goal = _clean_text(request.financial_goal)
        income_notes = _clean_text(request.income_notes)
        expense_notes = _clean_text(request.expense_notes)
        debt_notes = _clean_text(request.debt_notes)
        loan_notes = _clean_text(request.loan_notes)
        rent_housing_notes = _clean_text(request.rent_housing_notes)
        move_cost_notes = _clean_text(request.move_cost_notes)
        savings_notes = _clean_text(request.savings_notes)
        spending_notes = _clean_text(request.spending_notes)
        constraints = _clean_list(request.constraints)
        priorities = _clean_list(request.priorities)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            financial_goal,
            income_notes,
            expense_notes,
            debt_notes,
            loan_notes,
            rent_housing_notes,
            move_cost_notes,
            savings_notes,
            spending_notes,
            constraints,
            priorities,
        )
        high_stakes_context = _high_stakes_context(financial_goal, debt_notes, loan_notes, constraints, priorities)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "financialGoal": financial_goal,
            "desiredOutputType": desired_output_type,
            "financeFocus": _finance_focus(financial_goal, desired_output_type, thin_input),
            "incomeSummary": _income_summary(income_notes, priorities, thin_input),
            "expenseSummary": _expense_summary(expense_notes, rent_housing_notes, move_cost_notes, constraints),
            "budgetPlan": _budget_plan(financial_goal, income_notes, expense_notes, priorities, constraints),
            "loanReview": _loan_review(loan_notes, financial_goal, priorities, constraints),
            "debtPayoffPlan": _debt_payoff_plan(debt_notes, loan_notes, income_notes, priorities, constraints),
            "moveBudget": _move_budget(rent_housing_notes, move_cost_notes, income_notes, expense_notes, constraints),
            "cashflowReview": _cashflow_review(income_notes, expense_notes, debt_notes, savings_notes, constraints),
            "savingsPlan": _savings_plan(financial_goal, savings_notes, income_notes, expense_notes, priorities, constraints),
            "spendingReview": _spending_review(spending_notes, expense_notes, priorities, constraints),
            "decisionChecklist": _decision_checklist(financial_goal, debt_notes, loan_notes, priorities, high_stakes_context),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes_context),
            "openQuestions": _open_questions(
                financial_goal,
                income_notes,
                expense_notes,
                debt_notes,
                loan_notes,
                rent_housing_notes,
                move_cost_notes,
                savings_notes,
                spending_notes,
                constraints,
                priorities,
            ),
            "warnings": _warnings(thin_input, high_stakes_context),
            "limitations": _limitations(thin_input, high_stakes_context),
            "safety": local_finance_budget_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_finance_budget_dashboard_summary()


def local_finance_budget_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Finance / Loans / Budget Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/finance-budget/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "bankAccess": False,
        "creditCardAccess": False,
        "loanServicerAccess": False,
        "brokerageAccess": False,
        "paymentActions": False,
        "purchases": False,
        "tradingActions": False,
        "creditReportAccess": False,
        "taxPortalAccess": False,
        "financialAidAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "financialAdviceValidation": False,
        "taxValidation": False,
        "legalValidation": False,
        "investmentAdviceValidation": False,
        "accountingValidation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided finance, loan, debt, budget, savings, and spending inputs"],
    }


def local_finance_budget_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "bankAccess": False,
        "creditCardAccess": False,
        "loanServicerAccess": False,
        "brokerageAccess": False,
        "paymentActions": False,
        "purchases": False,
        "tradingActions": False,
        "creditReportAccess": False,
        "taxPortalAccess": False,
        "financialAidAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "financialAdviceValidation": False,
        "taxValidation": False,
        "legalValidation": False,
        "investmentAdviceValidation": False,
        "accountingValidation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "finance_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "finance_brief"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 10) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _thin_input(
    financial_goal: str,
    income_notes: str,
    expense_notes: str,
    debt_notes: str,
    loan_notes: str,
    rent_housing_notes: str,
    move_cost_notes: str,
    savings_notes: str,
    spending_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> bool:
    return not any(
        [
            financial_goal,
            income_notes,
            expense_notes,
            debt_notes,
            loan_notes,
            rent_housing_notes,
            move_cost_notes,
            savings_notes,
            spending_notes,
            constraints,
            priorities,
        ]
    )


def _high_stakes_context(
    financial_goal: str,
    debt_notes: str,
    loan_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> bool:
    text = " ".join([financial_goal, debt_notes, loan_notes, " ".join(constraints), " ".join(priorities)]).lower()
    terms = (
        "tax",
        "legal",
        "lawsuit",
        "contract",
        "credit",
        "bankruptcy",
        "collections",
        "private loan",
        "student loan",
        "fafsa",
        "investment",
        "brokerage",
        "mortgage",
        "refinance",
    )
    return any(term in text for term in terms)


def _finance_focus(financial_goal: str, desired_output_type: str, thin_input: bool) -> str:
    if thin_input:
        return "Clarify the financial goal, income, expenses, debts, loans, savings, spending notes, priorities, and constraints before relying on this plan."
    focus_by_type = {
        "budget_plan": "Shape a manual budget plan from supplied income, expense, priority, and constraint notes.",
        "loan_review": "Review user-provided loan notes without accessing servicers or validating repayment terms.",
        "debt_payoff_plan": "Draft a manual debt-payoff planning view without making payments or guaranteeing payoff outcomes.",
        "move_budget": "Organize rent, housing, and move-cost notes into a manual move budget.",
        "cashflow_review": "Review supplied cash-flow notes without reading bank, card, or statement data.",
        "savings_plan": "Turn supplied savings notes into a manual savings planning scaffold.",
        "spending_review": "Summarize user-provided spending notes without account access or statement reads.",
    }
    return focus_by_type.get(desired_output_type, f"Prepare a local finance, loans, and budget brief for: {financial_goal}.")


def _income_summary(income_notes: str, priorities: list[str], thin_input: bool) -> list[str]:
    summary = [f"Income notes supplied by user: {income_notes}." if income_notes else "Income notes are not specified."]
    if priorities:
        summary.append(f"Priority to keep visible: {priorities[0]}.")
    if thin_input:
        summary.append("Input is thin; add income, expenses, debts, loans, housing, move costs, savings, spending notes, priorities, and constraints.")
    summary.append("No bank, payroll, tax, file, or account data was accessed.")
    return summary


def _expense_summary(expense_notes: str, rent_housing_notes: str, move_cost_notes: str, constraints: list[str]) -> list[str]:
    summary = [f"Expense notes supplied by user: {expense_notes}." if expense_notes else "Expense notes are not specified."]
    if rent_housing_notes:
        summary.append(f"Rent/housing note: {rent_housing_notes}.")
    if move_cost_notes:
        summary.append(f"Move-cost note: {move_cost_notes}.")
    if constraints:
        summary.append(f"Constraint: {constraints[0]}.")
    summary.append("No card, bank, merchant, payment app, statement, or external-service data was accessed.")
    return summary


def _budget_plan(financial_goal: str, income_notes: str, expense_notes: str, priorities: list[str], constraints: list[str]) -> list[str]:
    plan = [
        f"Anchor the budget to the financial goal: {financial_goal}." if financial_goal else "Define the financial goal before relying on a budget plan.",
        f"Review income manually from supplied note: {income_notes}." if income_notes else "Add income notes before estimating available cash.",
        f"Review expenses manually from supplied note: {expense_notes}." if expense_notes else "Add expense notes before making tradeoff decisions.",
    ]
    if priorities:
        plan.append(f"Protect priority: {priorities[0]}.")
    if constraints:
        plan.append(f"Respect constraint: {constraints[0]}.")
    plan.append("No accounts, payments, transfers, purchases, records, files, or tasks were created.")
    return plan


def _loan_review(loan_notes: str, financial_goal: str, priorities: list[str], constraints: list[str]) -> list[str]:
    review = [f"Loan note supplied by user: {loan_notes}." if loan_notes else "Loan notes are not specified."]
    if financial_goal:
        review.append(f"Review loan tradeoffs against: {financial_goal}.")
    if priorities:
        review.append(f"Priority to preserve manually: {priorities[0]}.")
    if constraints:
        review.append(f"Constraint: {constraints[0]}.")
    review.append("No loan servicer, FAFSA, school financial-aid system, credit report, tax portal, or bank account was accessed.")
    review.append("No repayment certainty, approval, forgiveness, refinance, tax, legal, credit, or accounting validation is claimed.")
    return review


def _debt_payoff_plan(debt_notes: str, loan_notes: str, income_notes: str, priorities: list[str], constraints: list[str]) -> list[str]:
    plan = [
        f"Debt note supplied by user: {debt_notes}." if debt_notes else "Debt notes are not specified.",
        f"Loan context supplied by user: {loan_notes}." if loan_notes else "Loan context is not specified.",
        f"Income context to check manually: {income_notes}." if income_notes else "Add income notes before ranking payoff options.",
    ]
    if priorities:
        plan.append(f"Prioritize: {priorities[0]}.")
    if constraints:
        plan.append(f"Constraint: {constraints[0]}.")
    plan.append("No payment, transfer, autopay, servicer action, account connection, or credit action was performed.")
    return plan


def _move_budget(rent_housing_notes: str, move_cost_notes: str, income_notes: str, expense_notes: str, constraints: list[str]) -> list[str]:
    budget = [
        f"Rent/housing note: {rent_housing_notes}." if rent_housing_notes else "Rent or housing notes are not specified.",
        f"Move-cost note: {move_cost_notes}." if move_cost_notes else "Move-cost notes are not specified.",
    ]
    if income_notes:
        budget.append(f"Income context to compare manually: {income_notes}.")
    if expense_notes:
        budget.append(f"Existing expenses to preserve manually: {expense_notes}.")
    if constraints:
        budget.append(f"Constraint: {constraints[0]}.")
    budget.append("No apartment, bank, payment, map, credit, application, or external service was accessed.")
    return budget


def _cashflow_review(income_notes: str, expense_notes: str, debt_notes: str, savings_notes: str, constraints: list[str]) -> list[str]:
    review = [
        f"Income: {income_notes}." if income_notes else "Income is unknown from the request.",
        f"Expenses: {expense_notes}." if expense_notes else "Expenses are unknown from the request.",
        f"Debt: {debt_notes}." if debt_notes else "Debt is unknown from the request.",
        f"Savings: {savings_notes}." if savings_notes else "Savings are unknown from the request.",
    ]
    if constraints:
        review.append(f"Constraint: {constraints[0]}.")
    review.append("This is a manual cash-flow review only; no statements, accounts, files, or live balances were read.")
    return review


def _savings_plan(financial_goal: str, savings_notes: str, income_notes: str, expense_notes: str, priorities: list[str], constraints: list[str]) -> list[str]:
    plan = [
        f"Savings goal context: {financial_goal}." if financial_goal else "Define the savings goal before using this plan.",
        f"Savings note supplied by user: {savings_notes}." if savings_notes else "Savings notes are not specified.",
    ]
    if income_notes:
        plan.append(f"Income context: {income_notes}.")
    if expense_notes:
        plan.append(f"Expense context: {expense_notes}.")
    if priorities:
        plan.append(f"Priority: {priorities[0]}.")
    if constraints:
        plan.append(f"Constraint: {constraints[0]}.")
    plan.append("No account, transfer, purchase, investment, or automatic savings action was created.")
    return plan


def _spending_review(spending_notes: str, expense_notes: str, priorities: list[str], constraints: list[str]) -> list[dict[str, str]]:
    categories = [spending_notes] if spending_notes else ["Spending notes not supplied"]
    if expense_notes:
        categories.append(expense_notes)
    review = []
    for index, category in enumerate(categories[:3], start=1):
        note_parts = ["Manual review only; no card, bank, merchant, receipt, statement, or file data was read."]
        if priorities:
            note_parts.append(f"Compare against priority: {priorities[0]}.")
        if constraints:
            note_parts.append(f"Constraint: {constraints[0]}.")
        review.append({"item": f"spending_review_{index}", "sourceNote": category, "reviewNote": " ".join(note_parts)})
    return review


def _decision_checklist(
    financial_goal: str,
    debt_notes: str,
    loan_notes: str,
    priorities: list[str],
    high_stakes_context: bool,
) -> list[str]:
    checklist = [
        f"Restate the financial goal: {financial_goal}." if financial_goal else "Write the financial goal in one sentence.",
        "Separate known request-provided numbers from assumptions.",
        "Identify which decision requires official or professional confirmation.",
    ]
    if debt_notes:
        checklist.append("Review debt assumptions manually before acting.")
    if loan_notes:
        checklist.append("Confirm loan terms with official servicer or school sources before acting.")
    if priorities:
        checklist.append(f"Check impact on priority: {priorities[0]}.")
    if high_stakes_context:
        checklist.append("Pause for official/professional confirmation before debt, tax, legal, credit, investment, private-loan, FAFSA, or other high-stakes decisions.")
    checklist.append("Do not treat this checklist as a payment, transfer, trade, application, submission, or account action.")
    return checklist


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes_context: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add financial goal detail, income, expenses, debt, loans, rent/housing, move costs, savings, spending notes, priorities, and constraints.")
    type_actions = {
        "budget_plan": "Manually compare income, expenses, priorities, and constraints before changing spending.",
        "loan_review": "Confirm loan details with official servicer, school, FAFSA, or qualified professional sources before acting.",
        "debt_payoff_plan": "Choose a payoff scenario to review manually; do not treat this as payment execution.",
        "move_budget": "Manually compare rent, move costs, income, and recurring expenses before committing elsewhere.",
        "cashflow_review": "Fill unknown income, expense, debt, and savings details from official records outside this agent.",
        "savings_plan": "Choose one manual savings target and review affordability before acting.",
        "spending_review": "Pick one spending category to review manually without connecting accounts.",
    }
    actions.append(type_actions.get(desired_output_type, "Use this as local finance planning and decision-checklist support only."))
    if high_stakes_context:
        actions.append("Confirm debt, tax, legal, credit, investment, private-loan, FAFSA, or high-stakes financial decisions with official or qualified professional sources.")
    actions.append("Do not treat this response as financial, tax, legal, accounting, investment, credit, loan-approval, repayment, or live account validation.")
    return actions[:5]


def _open_questions(
    financial_goal: str,
    income_notes: str,
    expense_notes: str,
    debt_notes: str,
    loan_notes: str,
    rent_housing_notes: str,
    move_cost_notes: str,
    savings_notes: str,
    spending_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> list[str]:
    questions = []
    if not financial_goal:
        questions.append("What financial goal should anchor the plan?")
    if not income_notes:
        questions.append("What income notes should be used?")
    if not expense_notes:
        questions.append("What recurring expense notes should be included?")
    if not debt_notes:
        questions.append("What debt notes should be reviewed?")
    if not loan_notes:
        questions.append("What loan notes or student-loan context should be included?")
    if not rent_housing_notes:
        questions.append("What rent or housing affordability notes matter?")
    if not move_cost_notes:
        questions.append("What move-cost notes should be included?")
    if not savings_notes:
        questions.append("What savings target or cushion should be considered?")
    if not spending_notes:
        questions.append("What spending notes or categories should be reviewed?")
    if not constraints:
        questions.append("What constraints, deadlines, obligations, or risk limits matter?")
    if not priorities:
        questions.append("What financial priorities should be protected?")
    return questions


def _warnings(thin_input: bool, high_stakes_context: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Finance input is thin; output is a provisional local planning scaffold.")
    if high_stakes_context:
        warnings.append("Debt, tax, legal, credit, investment, private-loan, FAFSA, or high-stakes financial decisions need official or qualified professional confirmation.")
    warnings.append("This response uses only request-provided data and does not verify live balances, account records, credit reports, taxes, loan terms, aid status, payments, trades, or market conditions.")
    return warnings


def _limitations(thin_input: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided finance notes for budgets, loans, debt payoff, rent affordability, move costs, cash flow, savings, spending, priorities, and constraints.",
        "No banks, credit cards, loan servicers, Webull, brokerages, credit reports, tax portals, FAFSA, school financial-aid systems, payment apps, files, external services, paid APIs, accounts, or connectors were accessed.",
        "No payments, transfers, purchases, trades, loan applications, form submissions, account connections, statement reads, task creation, record persistence, file access, database write, shell execution, mutation, financial advice validation, tax validation, legal validation, investment advice validation, accounting validation, or certification was performed.",
        "No financial-advisor, tax, legal, credit, accounting, investment, loan-approval, repayment-certainty, debt-payoff, affordability, savings, market, or outcome validation is claimed.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add income, expenses, debts, loans, housing, move costs, savings, spending notes, priorities, and constraints.")
    if high_stakes_context:
        limitations.append("For debt, taxes, legal agreements, credit, investments, private loans, FAFSA, or high-stakes financial decisions, confirm with official sources or qualified professionals.")
    return limitations
