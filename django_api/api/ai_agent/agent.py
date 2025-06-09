from ai_agent.tools.monotransations import get_monthly_jar_transactions_tool
from langchain.agents import AgentType, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI


def get_jar_monthly_report(date: str) -> dict[str, str]:
    """
    Get monthly report for Jar transactions
    :param date: date in YYYY-MM-DD format
    :return: monthly report
    """
    inputs = """Check monojartransactions around the given {date}.
    Your task is to generate a report per each jar with transactions for this month.
    Date for report can be fetched from tool get_monthly_jar_transactions. Use results to build report
    Report should contain Jar name, budget, and spent amount.
    * Jar name can be fetched from each transaction. In case of multiple transactions, group them by jar name.
    * Budget is a relatively big positive transaction to the jar (usually at the start of the month).
    In case of multiple positive transactions, consider the biggest as the budget.
    * Spent amount is a sum of all transactions (positive and negative) for this month per jar name excluding the budget.
        If no results or errors, return JSON in the format:
    {{
    "error": "Error message"
    }}
    Wrap the report in JSON in the format:
    {{
    "jar_name": {{
            "budget": 1000,
            "spent": 500,
            "owner": "John Doe"
        }},
        ...
    }}

    """
    inputs = inputs.format(date=date)
    # 🧠 Model: Google Generative AI (Gemini/PaLM)
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",  # You can use other available models
        temperature=0,
    )
    agent = initialize_agent(
        tools=[get_monthly_jar_transactions_tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    return agent.invoke(inputs)
