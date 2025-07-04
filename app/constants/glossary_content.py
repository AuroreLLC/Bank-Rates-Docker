financial_rates = {
            "FOMC Rate (Federal Funds Rate)": {
                "category": "Monetary Policy",
                "description": "The target interest rate set by the Federal Open Market Committee (FOMC) at which depository institutions lend reserve balances to other institutions overnight. This is the primary tool of U.S. monetary policy and serves as the benchmark for all other interest rates in the economy.",
                "typical_range": "0% - 6%",
                "controlled_by": "Federal Reserve FOMC",
                "frequency": "8 meetings per year",
                "impact": "Influences all other rates, economic growth, inflation, and employment",
                "current_use": "Primary monetary policy tool"
            },
            "SOFR (Secured Overnight Financing Rate)": {
                "category": "Reference Rate",
                "description": "A broad measure of the cost of borrowing cash overnight collateralized by U.S. Treasury securities. SOFR is based on actual transactions in the repo market and has largely replaced LIBOR as the preferred reference rate for financial contracts.",
                "typical_range": "0% - 5%",
                "controlled_by": "Market-determined (calculated by NY Fed)",
                "frequency": "Published daily",
                "impact": "Benchmark for derivatives, loans, mortgages, and bonds",
                "current_use": "Primary LIBOR replacement"
            },
            "SOFR 30-Day Average": {
                "category": "Reference Rate",
                "description": "The arithmetic average of daily SOFR rates over a 30-day period. This smoothed version reduces daily volatility and provides a more stable reference rate for longer-term financial products and contracts.",
                "typical_range": "0% - 5%",
                "controlled_by": "Calculated from daily SOFR",
                "frequency": "Published daily",
                "impact": "Used for medium-term loans and financial products",
                "current_use": "Reduces volatility in pricing"
            },
            "SOFR 90-Day Average": {
                "category": "Reference Rate",
                "description": "The arithmetic average of daily SOFR rates over a 90-day period. This provides an even more stable reference rate for quarterly or longer-term financial contracts, further smoothing out short-term market fluctuations.",
                "typical_range": "0% - 5%",
                "controlled_by": "Calculated from daily SOFR",
                "frequency": "Published daily",
                "impact": "Used for longer-term loans and financial products",
                "current_use": "Quarterly contract benchmark"
            },
            "SOFR Adjusted": {
                "category": "Reference Rate",
                "description": "A version of SOFR that includes a spread adjustment to make it more comparable to USD LIBOR. This adjustment helps ensure continuity in financial contracts transitioning from LIBOR to SOFR.",
                "typical_range": "0.1% - 5.1%",
                "controlled_by": "SOFR plus fixed spread adjustment",
                "frequency": "Published daily",
                "impact": "Facilitates LIBOR transition",
                "current_use": "LIBOR replacement with adjustment"
            },
            "LIBOR (London Interbank Offered Rate)": {
                "category": "Legacy Reference Rate",
                "description": "The benchmark interest rate at which major global banks lend to one another in the international interbank market. LIBOR has been largely phased out due to manipulation scandals and lack of underlying transactions.",
                "typical_range": "0% - 6% (historical)",
                "controlled_by": "Previously by panel banks (now discontinued)",
                "frequency": "Was published daily (now legacy)",
                "impact": "Historical benchmark (being replaced by SOFR)",
                "current_use": "Legacy contracts only"
            },
            "OIS (Overnight Index Swap)": {
                "category": "Derivative Rate",
                "description": "Interest rate swaps where the floating leg is tied to a published overnight rate index. In the U.S., this is typically based on the effective federal funds rate. OIS rates reflect market expectations of future Fed policy.",
                "typical_range": "0% - 6%",
                "controlled_by": "Market-determined through trading",
                "frequency": "Continuous trading",
                "impact": "Reflects Fed policy expectations",
                "current_use": "Policy expectation gauge"
            },
            "Fannie Mae Rates": {
                "category": "Mortgage Finance",
                "description": "Interest rates associated with the Federal National Mortgage Association (Fannie Mae), a government-sponsored enterprise that buys mortgages from lenders. These rates influence conventional mortgage pricing across the United States.",
                "typical_range": "2% - 8%",
                "controlled_by": "Market-determined with GSE influence",
                "frequency": "Daily updates",
                "impact": "Affects conventional mortgage rates nationwide",
                "current_use": "Mortgage market benchmark"
            },
            "Prime Rate": {
                "category": "Commercial Banking",
                "description": "The interest rate that commercial banks charge their most creditworthy customers, typically large corporations with excellent credit ratings. The prime rate is usually set at approximately 3 percentage points above the federal funds rate.",
                "typical_range": "3% - 9%",
                "controlled_by": "Individual banks (market convention)",
                "frequency": "Changes with Fed funds rate",
                "impact": "Affects business loans, credit cards, and consumer loans",
                "current_use": "Commercial lending benchmark"
            },
            "Discount Rate": {
                "category": "Monetary Policy",
                "description": "The interest rate charged by Federal Reserve Banks to commercial banks and other depository institutions on short-term loans through the Fed's discount window. It's typically set above the federal funds rate to encourage interbank lending first.",
                "typical_range": "0.25% - 6.25%",
                "controlled_by": "Federal Reserve Banks",
                "frequency": "As needed by Fed",
                "impact": "Emergency liquidity for banks",
                "current_use": "Banking system safety net"
            },
            "10-Year Treasury Yield": {
                "category": "Government Securities",
                "description": "The return on investment for 10-year U.S. Treasury notes, considered the benchmark for long-term interest rates. It reflects investor expectations about economic growth, inflation, and overall market risk over the next decade.",
                "typical_range": "1% - 8%",
                "controlled_by": "Market forces (auctions and trading)",
                "frequency": "Continuous trading",
                "impact": "Influences mortgage rates, bond yields, and equity valuations",
                "current_use": "Long-term rate benchmark"
            },
            "30-Year Fixed Mortgage Rate": {
                "category": "Consumer Finance",
                "description": "The interest rate charged on a conventional 30-year fixed-rate mortgage loan. This rate is influenced by the 10-year Treasury yield, MBS spreads, and lender profit margins, and represents the most common home financing option in the U.S.",
                "typical_range": "3% - 8%",
                "controlled_by": "Market forces and lender pricing",
                "frequency": "Daily rate updates",
                "impact": "Affects home affordability and real estate markets",
                "current_use": "Primary home financing rate"
            },
            "FHLB (Federal Home Loan Bank)": {
                "category": "Government Sponsored Enterprise",
                "description": "A system of regional banks that provide liquidity to financial institutions for mortgage lending and community development. FHLB rates influence the cost of funds for member banks and affect mortgage market pricing.",
                "typical_range": "Varies by term and market conditions",
                "controlled_by": "FHLB System Board",
                "frequency": "Regular updates based on market conditions",
                "impact": "Affects mortgage lending costs for member institutions",
                "current_use": "Wholesale funding for banks"
            },
            "COFI (Cost of Funds Index)": {
                "category": "Regional Index",
                "description": "A weighted average of interest rates paid by savings institutions on savings and checking accounts, NOW accounts, and certificates of deposit. Used primarily for adjustable-rate mortgages in certain regions.",
                "typical_range": "1% - 5%",
                "controlled_by": "Calculated by Federal Home Loan Bank",
                "frequency": "Monthly calculation",
                "impact": "Determines rate adjustments for ARM mortgages",
                "current_use": "ARM benchmark in specific regions"
            },
            "FRED (Federal Reserve Economic Data)": {
                "category": "Data Source",
                "description": "A comprehensive database maintained by the Federal Reserve Bank of St. Louis containing hundreds of thousands of economic time series from various sources. FRED is the primary source for accessing historical and current economic data.",
                "typical_range": "N/A (data source)",
                "controlled_by": "Federal Reserve Bank of St. Louis",
                "frequency": "Continuous updates",
                "impact": "Provides data for economic analysis and policy decisions",
                "current_use": "Primary economic data repository"
            }
        }
quick_terms = {
    "SOFR": "Secured Overnight Financing Rate - Replaces LIBOR",
    "FRED": "Federal Reserve Economic Data - Economic data repository",
    "FHLB": "Federal Home Loan Bank - Federal loan bank",
    "COFI": "Cost of Funds Index - Funding cost index",
    "Treasury": "U.S. Treasury Bonds - Government securities",
    "Prime Rate": "Prime rate offered to top clients"
}


sections_terms = {
    "SOFR": "Secured Overnight Financing Rate - Replaces LIBOR",
    "FRED": "Federal Reserve Economic Data - Economic data repository",
    "FHLB": "Federal Home Loan Bank - Federal loan bank",
    "COFI": "Cost of Funds Index - Funding cost index",
    "Treasury": "U.S. Treasury Bonds - Government securities",
    "Prime Rate": "Prime rate offered to top clients"
}


style = """
        <style>
            .glossary-header {
                text-align: center;
                color: #1f77b4;
                font-size: 2.5rem;
                margin-bottom: 2rem;
                font-weight: bold;
            }
            .rate-card {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-left: 5px solid #1f77b4;
                padding: 1.5rem;
                margin: 1.5rem 0;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .rate-title {
                color: #1f77b4;
                font-size: 1.4rem;
                font-weight: bold;
                margin-bottom: 0.8rem;
            }
            .rate-description {
                line-height: 1.7;
                color: #333;
                margin-bottom: 1rem;
            }
            .rate-details {
                background-color: white;
                padding: 1rem;
                border-radius: 8px;
                margin-top: 1rem;
            }
            .detail-item {
                margin: 0.5rem 0;
                padding: 0.3rem 0;
                border-bottom: 1px solid #eee;
            }
            .detail-label {
                font-weight: bold;
                color: #495057;
            }
            .category-badge {
                background-color: #1f77b4;
                color: white;
                padding: 0.3rem 0.8rem;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: bold;
                margin-bottom: 1rem;
                display: inline-block;
            }
            .quick-term {
                background-color: #f8f9fa;
                border-left: 3px solid #1f77b4;
                padding: 0.5rem;
                margin: 0.5rem 0;
                border-radius: 5px;
                font-size: 0.9rem;
            }
            .term-tooltip {
                text-decoration: underline dotted;
                cursor: help;
                color: #1f77b4;
            }
            .sidebar-section {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
        </style>
        """

introduction = """
<div style="background-color: #e3f2fd; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
    <h3 style="color: #1976d2; margin-bottom: 1rem;">🏦 Understanding U.S. Financial Rates</h3>
    <p style="color: #333; line-height: 1.6; margin-bottom: 0;">
        This comprehensive glossary covers key interest rates and financial benchmarks that drive the U.S. economy.
        From Federal Reserve policy rates to market-determined indexes, these rates influence everything 
        from your mortgage payments to corporate loan costs and investment returns.
    </p>
</div>
"""


def generate_rate_card(rate_name, rate_info):
    card = f"""
        <div class="rate-card">
            <div class="category-badge">{rate_info['category']}</div>
            <div class="rate-title">{rate_name}</div>
            <div class="rate-description">{rate_info['description']}</div>
            <div class="rate-details">
                <div class="detail-item">
                    <span class="detail-label">Typical Range:</span> {rate_info['typical_range']}
                </div>
                <div class="detail-item">
                    <span class="detail-label">Controlled By:</span> {rate_info['controlled_by']}
                </div>
                <div class="detail-item">
                    <span class="detail-label">Update Frequency:</span> {rate_info['frequency']}
                </div>
                <div class="detail-item">
                    <span class="detail-label">Economic Impact:</span> {rate_info['impact']}
                </div>
                <div class="detail-item">
                    <span class="detail-label">Current Use:</span> {rate_info['current_use']}
                </div>
            </div>
        </div>
    """
    return card
