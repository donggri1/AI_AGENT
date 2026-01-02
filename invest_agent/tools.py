from typing import Type
from crewai.tools import BaseTool
from firecrawl import Firecrawl
from pydantic import BaseModel, Field
from env import FIRECRAWL_API_KEY
import yfinance as yf

def _yahoo_finance(ticker:str,period:str = "1y"):

    try:
            stock = yf.Ticker(ticker)
            history = stock.history(period=period)
            info = stock.info

            if history.empty:
                return f"No historical data found for ticker: {ticker}"

            current_price = history["Close"].iloc[-1] if not history.empty else None
            year_high = history["High"].max()
            year_low = history["Low"].min()

            revenue_growth = "N/A"
            try:
                financials = stock.financials
                if not financials.empty and "Total Revenue" in financials.index:
                    revenues = financials.loc["Total Revenue"].dropna()
                    if len(revenues) >= 2:
                        latest_revenue = revenues.iloc[0]
                        prev_revenue = revenues.iloc[1]
                        revenue_growth = (
                            f"{((latest_revenue - prev_revenue) / prev_revenue * 100):.2f}%"
                        )
            except Exception:
                pass

            company_data = {
                "ticker": ticker,
                "company_name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "current_price": float(current_price) if current_price else None,
                "52_week_high": float(year_high),
                "52_week_low": float(year_low),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "forward_pe": info.get("forwardPE", "N/A"),
                "price_to_book": info.get("priceToBook", "N/A"),
                "revenue_growth": revenue_growth,
                "profit_margin": info.get("profitMargins", "N/A"),
                "operating_margin": info.get("operatingMargins", "N/A"),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "return_on_equity": info.get("returnOnEquity", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "business_summary": (
                    info.get("longBusinessSummary", "N/A")[:500] + "..."
                    if info.get("longBusinessSummary")
                    and len(info.get("longBusinessSummary", "")) > 500
                    else info.get("longBusinessSummary", "N/A")
                ),
            }

            return company_data

    except Exception as e:
        return f"Error retrieving data for {ticker}: {e}"


def _web_search(query: str):
    firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)

    response = firecrawl.search(query, limit=5)

    if not response:
        return f"No search results found for query: {query}"

    search_results = []

    if response.web:
        for result in response.web:
            title = getattr(result, "title", "No Title")
            url = getattr(result, "url", "")
            description = getattr(result, "description", "")

            search_results.append(
                {
                    "title": title,
                    "url": url,
                    "content": description,
                }
            )
        search_result = {
            "query": query,
            "results_count": len(search_results),
            "results": search_results,
        }
        return search_result



class YahooFinanceInput(BaseModel):
    """Input schema for YahooFinanceTool."""
    ticker: str = Field(
                ...,
                description="분석할 기업의 주식 티커 심볼 (예: 'AAPL', 'TSLA', 'MSFT')."
            )
    period: str = Field(
        default="1y",
        description="과거 데이터를 조회할 기간. '1d', '1mo', '1y', '5y', 'max' 등의 형식을 사용함. 기본값은 '1y'이며, 52주 신고가/신저가 계산에 영향을 줌."
    )

class YahooFinanceTool(BaseTool):
    name: str = "yahoo_finance_tool"
    description: str = (
        "특정 기업의 재무 제표, 가치 평가 지표(P/E, P/B), 수익성(ROE, 이익률), "
        "주가 통계 및 사업 개요를 포함한 종합적인 기업 정보를 가져옵니다. "
        "단순 현재가 조회를 넘어 기업의 펀더멘털 분석이나 투자 타당성을 검토할 때 이 도구를 사용해야 합니다."
    )
    args_schema: Type[BaseModel] = YahooFinanceInput

    def _run(self, ticker: str, period = "1y"):
        return _yahoo_finance(ticker, period)



class WebSearchToolInput(BaseModel):
    """Input schema for WebSearchTool."""

    query: str = Field(..., description="The search query to look for.")


class WebSearchTool(BaseTool):
    name: str = "web_search_tool"
    description: str = (
        "Searches the web for information based on a query and returns relevant results with titles, URLs, and content snippets."
    )
    args_schema: Type[BaseModel] = WebSearchToolInput

    def _run(self, query: str):
        return _web_search(query)


web_search_tool = WebSearchTool()
yahoo_finance_tool = YahooFinanceTool()

if __name__ == "__main__":
    test_tickers = ["NVDA","GOOGL","TSLA"]
    for ticker in test_tickers:
        print(f"Fetching data for {ticker}...  ")

        result = _yahoo_finance(ticker)
        print(result)
        print("\n")
