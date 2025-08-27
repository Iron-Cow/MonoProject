# pyright: reportAttributeAccessIssue=false
# pyright: reportReturnType=false

import json
from typing import Any, Dict

from ai_agent.tools.monotransations import (
    get_daily_mono_transactions_tool,
    get_monthly_jar_transactions_tool,
)
from langchain.agents import AgentType, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI


def get_jar_monthly_report(date: str) -> Dict[str, Any]:
    """
    Agent 1: Analysis Agent - Processes raw data into structured analysis
    :param date: date in YYYY-MM-DD format
    :return: structured analysis data
    """
    inputs = """Analyze jar transactions for {date}.

    Your task is to process transaction data and generate a structured analysis.
    Always use tools to get data.

    Analysis rules:
    * Group transactions by jar name
    * Budget = largest positive transaction (usually at month start)
    * Spent = sum of all transactions (positive + negative) excluding budget
    * Remaining balance is balance of last (on time value) transaction in the jar
    * Count total transactions per jar
    * If you failed to finish calculation - try again.

    Return structured JSON:
    {{
        "jars": {{
            "jar_name": {{
                "budget": 1000,
                "spent": 500,
                "remaining": 500,
                "transaction_count": 15,
                "owner": "John Doe",
            }}
        }},
    }}

    If no data or errors, return:
    {{
        "error": "Error message",
        "jars": {{}},
    }}
    """

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0,
    )

    agent = initialize_agent(
        tools=[get_monthly_jar_transactions_tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    result = agent.invoke({"input": inputs.format(date=date)})

    # Extract the output content
    if hasattr(result, "output"):
        return (
            result.output  # pyright: ignore[reportAttributeAccessIssue, reportGeneralTypeIssues]
        )
    return result


def generate_html_report(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 2: Presentation Agent - Converts analysis to beautiful HTML
    :param analysis_data: Structured analysis from get_jar_monthly_report
    :return: HTML formatted report
    """
    inputs = """Convert this financial analysis data into a HTML format. It will be used in telegram bot.
    Make sure to use code tags for values of the fields.
Data: {data}

Please use format from example below:
----
Here is Jar report:

<<<JAR_REPORT goes here>>>
----

Available tags for report formatting:
----
<b>Bold text</b>
<i>Italic text</i>
<u>Underlined text</u>
<code>Monospace text</code>
<a href="https://example.com">Link</a>

<b>List Examples:</b>
• <i>Bullet point 1</i>
• <i>Bullet point 2</i>
• <i>Bullet point 3</i>

<b>Numbered List:</b>
1️⃣ <code>First item</code>
2️⃣ <code>Second item</code>
3️⃣ <code>Third item</code>

<b>Checklist:</b>
☑️ <i>Completed task</i>
☐ <i>Pending task</i>
☐ <i>Another pending task</i>
---

Data: {data}

Requirements:
- repare data in required format
- Return only the HTML content (no markdown formatting).


    """

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0.1,  # Slight creativity for better HTML
    )

    agent = initialize_agent(
        tools=[],  # No tools needed for HTML generation
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    result = agent.invoke(
        {"input": inputs.format(data=json.dumps(analysis_data, indent=2))}
    )

    # Extract the output content
    if hasattr(result, "output"):
        return (
            result.output  # pyright: ignore[reportAttributeAccessIssue, reportGeneralTypeIssues]
        )
    return result  # pyright: ignore[reportReturnType]


def get_jar_monthly_report_html(date: str) -> Dict[str, Any]:
    """
    Complete workflow: Data → Analysis → HTML Report
    :param date: date in YYYY-MM-DD format
    :return: HTML formatted report
    """
    # Step 1: Get structured analysis
    analysis_result = get_jar_monthly_report(date)

    # Step 2: Generate HTML report
    html_report = generate_html_report(analysis_result)

    return html_report


def get_daily_mono_transactions_report(
    date: str | None = None, tg_id: str | int | None = None
) -> str:
    """
    Generate a report of MONO transactions that were not covered by JAR transactions.
    :param date: date in YYYY-MM-DD format (defaults to today)
    :return: HTML formatted report of uncovered transactions
    """
    if date is None:
        from datetime import datetime

        date = datetime.now().strftime("%Y-%m-%d")

    inputs = """Analyze daily MONO card transactions for {date} and create a comprehensive spending coverage report.

Your task is to get MONO transactions and analyze which spending transactions are covered by positive (income) transactions.

Always use tools to get mono transactions data.
You MUST call the tool with parameters day="{date}", tg_id="{tg_id}", include_family=False to ensure data is filtered by the specified user.

Analysis rules:
* Get ALL MONO transactions for the day (both positive and negative)
* Focus on negative amounts as spending transactions
* Focus on positive amounts as income/compensation transactions
* Try to match spending transactions with positive transactions to determine coverage
* Transactions may not be exact matches - they can be:
  - Broken down into multiple smaller transactions
  - Different by a few percent (up to 5% variance)
  - Have slightly different descriptions or timing
  - One positive transaction can cover multiple smaller spending transactions
  - Compensation can be received before the spending transaction
* It not should be a situation, when you have uncovered spending and leftover positive transaction with same amount.
* Use multiple iterations if needed to find the best matching combinations
* Try to find the best matching combinations of spending transactions and positive transactions.
* Mark each spending transaction as either "✅ COVERED" or "❌ NOT COVERED"
* Show ALL spending transactions in the report, regardless of coverage status
* Show leftover positive transactions that were not used for coverage of spending transactions
* Make additional round of comparion on uncovered spending transactions and positive leftover transactions
to make sure that you have covered all spending transactions.

Return HTML formatted report using ONLY these supported Telegram HTML tags:
<b>Bold text</b>
<i>Italic text</i>
<u>Underlined text</u>
<code>Monospace text</code>
<a href="https://example.com">Link</a>

IMPORTANT: Do NOT use any other HTML tags like <br>, <div>, <p>, etc. Use line breaks (newlines) instead.

Report format:
<b>Daily MONO Transactions Report for {date}</b>

<b>💳 All MONO Spending Transactions:</b>
[For each spending transaction, show:]
• ✅ COVERED | <code>[amount] UAH</code> | <i>[description]</i> | [time] | [category]
• ❌ NOT COVERED | <code>[amount] UAH</code> | <i>[description]</i> | [time] | [category]

<b>💰 Leftover Income Transactions:</b>
[For each unused positive transaction, show:]
• <code>[amount] UAH</code> | <i>[description]</i> | [time] | [category]

<b>📊 Summary:</b>
• Total spending: <code>[total_spending] UAH</code>
• Total positive: <code>[total_positive] UAH</code>
• Covered spending: <code>[covered_count]</code> transactions (<code>[covered_amount] UAH</code>)
• Not covered spending: <code>[not_covered_count]</code> transactions (<code>[not_covered_amount] UAH</code>)
• Leftover positive: <code>[leftover_count]</code> transactions (<code>[leftover_amount] UAH</code>)

<b>💡 Notes: This report for info only. Please take actions if needed.</b>

Remember: Amounts in MONO transactions are in kopiykas (divide by 100 for UAH).
    """.format(
        date=date,
        tg_id=str(tg_id) if tg_id is not None else "",
    )

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0,
    )

    agent = initialize_agent(
        tools=[get_daily_mono_transactions_tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    result = agent.invoke({"input": inputs})

    # Extract the output content
    if result.get("output"):
        output = result.get(
            "output"
        )  # pyright: ignore[reportAttributeAccessIssue, reportGeneralTypeIssues]
    else:
        output = str(result)

    return output
