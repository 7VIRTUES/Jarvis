import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_finance_budget_agent import LocalFinanceBudgetAgentService, LocalFinanceBudgetRequest


def test_local_finance_budget_endpoint_returns_structured_plan():
    payload = app_module.LocalFinanceBudgetInput(
        profileName="Local Finance Plan",
        financialGoal="Prepare a manual budget for Boston move costs, student loans, and savings.",
        incomeNotes="Monthly income estimate from user-provided notes only.",
        expenseNotes="Recurring food, transit, phone, utilities, and school-related costs.",
        debtNotes="Student loan and small revolving balance notes for manual review.",
        loanNotes="Student loan repayment options need official servicer confirmation.",
        rentHousingNotes="Compare rent affordability for shared Boston housing.",
        moveCostNotes="Estimate deposit, first month, moving supplies, and transit setup.",
        savingsNotes="Build a small emergency cushion before optional spending.",
        spendingNotes="Review dining out, subscriptions, and hobby spending manually.",
        constraints=["Manual planning only"],
        priorities=["Avoid missed payments", "Protect move-in cash cushion"],
        desiredOutputType="finance_brief",
    )

    result = app_module.create_local_finance_budget_plan(payload)

    assert result["agentId"] == "local_finance_budget_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_finance_budget_planning"
    assert result["profileName"] == "Local Finance Plan"
    assert result["financialGoal"] == "Prepare a manual budget for Boston move costs, student loans, and savings."
    assert result["desiredOutputType"] == "finance_brief"
    assert result["financeFocus"]
    assert result["incomeSummary"]
    assert result["expenseSummary"]
    assert result["budgetPlan"]
    assert result["loanReview"]
    assert result["debtPayoffPlan"]
    assert result["moveBudget"]
    assert result["cashflowReview"]
    assert result["savingsPlan"]
    assert result["spendingReview"]
    assert result["decisionChecklist"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided finance notes" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("finance_brief", "finance_brief"),
        ("budget_plan", "budget_plan"),
        ("loan_review", "loan_review"),
        ("debt_payoff_plan", "debt_payoff_plan"),
        ("move_budget", "move_budget"),
        ("cashflow_review", "cashflow_review"),
        ("savings_plan", "savings_plan"),
        ("spending_review", "spending_review"),
        (" LOAN_REVIEW ", "loan_review"),
    ],
)
def test_local_finance_budget_supported_output_types_normalize(requested, expected):
    service = LocalFinanceBudgetAgentService()

    result = service.create_plan(
        LocalFinanceBudgetRequest(
            financial_goal="Prepare a manual student-loan and budget plan.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_finance_budget_unsupported_output_type_falls_back_safely():
    service = LocalFinanceBudgetAgentService()

    result = service.create_plan(
        LocalFinanceBudgetRequest(
            financial_goal="Prepare a budget.",
            desired_output_type="auto_pay_trade_and_apply",
        )
    )

    assert result["desiredOutputType"] == "finance_brief"
    assert result["safety"]["paymentActions"] is False
    assert result["safety"]["tradingActions"] is False
    assert result["safety"]["loanServicerAccess"] is False


def test_local_finance_budget_thin_input_reports_warnings_and_questions():
    service = LocalFinanceBudgetAgentService()

    result = service.create_plan(LocalFinanceBudgetRequest(financial_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_finance_budget_output_includes_budget_loan_debt_move_cashflow_savings_and_spending_sections():
    service = LocalFinanceBudgetAgentService()

    result = service.create_plan(
        LocalFinanceBudgetRequest(
            financial_goal="Balance rent, loans, savings, and spending.",
            income_notes="Monthly income estimate.",
            expense_notes="Recurring living costs.",
            debt_notes="Credit balance and student debt.",
            loan_notes="Federal student loan notes.",
            rent_housing_notes="Boston rent range.",
            move_cost_notes="Deposit and moving supplies.",
            savings_notes="Emergency cushion.",
            spending_notes="Subscriptions and dining.",
            desired_output_type="budget_plan",
        )
    )

    assert result["budgetPlan"]
    assert result["loanReview"]
    assert result["debtPayoffPlan"]
    assert result["moveBudget"]
    assert result["cashflowReview"]
    assert result["savingsPlan"]
    assert result["spendingReview"]


def test_local_finance_budget_output_does_not_claim_account_actions_payments_trades_or_validation():
    service = LocalFinanceBudgetAgentService()

    result = service.create_plan(
        LocalFinanceBudgetRequest(
            financial_goal="Pay debt, trade, transfer, submit FAFSA, and verify live balances.",
            desired_output_type="loan_review",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "account accessed",
        "payment completed",
        "transfer completed",
        "trade placed",
        "loan application submitted",
        "form submitted",
        "live balance verified",
        "loan approved",
        "repayment guaranteed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no banks" in output_text
    assert "no payments" in output_text
    assert "no financial-advisor" in output_text
    assert "no financial" in output_text


def test_local_finance_budget_high_stakes_inputs_include_professional_confirmation_limitations():
    service = LocalFinanceBudgetAgentService()

    result = service.create_plan(
        LocalFinanceBudgetRequest(
            financial_goal="Review taxes, legal agreements, credit, investments, private loan, FAFSA, and student loan choices.",
            desired_output_type="finance_brief",
        )
    )

    assert any("qualified professional confirmation" in warning for warning in result["warnings"])
    assert any("qualified professionals" in limitation for limitation in result["limitations"])
    assert any("qualified professional sources" in action for action in result["nextActions"])


def test_local_finance_budget_safety_flags_disable_connectors_accounts_payments_trading_persistence_mutation_and_certification():
    service = LocalFinanceBudgetAgentService()

    result = service.create_plan(LocalFinanceBudgetRequest(financial_goal="Prepare a budget."))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["connectors"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["webBrowsing"] is False
    assert safety["paidApis"] is False
    assert safety["bankAccess"] is False
    assert safety["creditCardAccess"] is False
    assert safety["loanServicerAccess"] is False
    assert safety["brokerageAccess"] is False
    assert safety["paymentActions"] is False
    assert safety["purchases"] is False
    assert safety["tradingActions"] is False
    assert safety["creditReportAccess"] is False
    assert safety["taxPortalAccess"] is False
    assert safety["financialAidAccess"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["financialAdviceValidation"] is False
    assert safety["taxValidation"] is False
    assert safety["legalValidation"] is False
    assert safety["investmentAdviceValidation"] is False
    assert safety["accountingValidation"] is False
    assert safety["certificationClaims"] is False


def test_local_finance_budget_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_finance_budget_agent").local_finance_budget_agent).lower()
    forbidden = [
        "requests",
        "httpx",
        "urllib.request",
        "socket",
        "subprocess",
        "open(",
        "read_text",
        "read_bytes",
        "write_text",
        ".write(",
        "sqlite",
        "taskqueue",
        "gmail.",
        "google_calendar",
        "smtp.",
        "imap.",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source for token in forbidden)


def test_local_finance_budget_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalFinanceBudgetInput.model_validate(
            {
                "financialGoal": "Prepare a budget.",
                "bankPassword": "not allowed",
            }
        )


def test_local_finance_budget_requires_financial_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalFinanceBudgetInput.model_validate({"profileName": "Missing goal"})


def test_local_finance_budget_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/finance-budget/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
