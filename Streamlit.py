
import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt



# Configure the page layout
st.set_page_config(page_title="Expense Tracker", layout="wide")

# Sidebar for navigation
st.sidebar.title("Expense Tracker")
st.sidebar.write("Navigate through the app sections")

# Navigation menu
menu = ["Home", "Expense Tracker","Visualization","Insights & Recommendations"]
choice = st.sidebar.radio("Select a section:", menu)


# Function to establish a connection using PyMySQL
@st.cache_resource
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",  
        password="123456789",  
        database="expense_tracker",  
        cursorclass=pymysql.cursors.DictCursor  
    )

# Function to run a query and fetch results
def run_query(query):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch all rows
    return results


# Home section
if choice == "Home":
    st.title("Welcome to the Expense Tracker App")
    st.write("""
        This application helps you track and analyze your personal expenses.
        Navigate through the sections to explore visualizations and insights.
    """)
   

# Expense Tracker section
elif choice == "Expense Tracker":
    
    queries = {
    "Expense by Category": """
        SELECT Category , SUM(Amount) AS expense_by_category 
        FROM expense 
        GROUP BY Category 
        ORDER BY expense_by_category DESC
    """,
    "Expense by Payment Mode": """
        SELECT Payment_Mode , SUM(Amount) AS expense_by_paymode 
        FROM expense 
        GROUP BY Payment_Mode
        ORDER BY expense_by_paymode DESC
    """,
    "Expense by Month": """
        SELECT MONTHNAME(Date) AS Month_Name, SUM(Amount) AS monthly_expense 
        FROM expense 
        GROUP BY MONTH(Date) , MONTHNAME(Date)
        ORDER BY monthly_expense DESC
    """,
    "Top 3 Expenses in January": """
        SELECT MONTHNAME(Date) AS Month_name, Category , Amount,
        RANK() OVER(ORDER BY Amount DESC) AS rank_value
        FROM expense
        WHERE MONTH(Date) = 1 
        LIMIT 3
    """,
    "Cashback by Month": """
        SELECT  MONTHNAME(Date) AS Month_Name , AVG(Cashback) AS avg_cashback_monthly
        FROM expense
        GROUP BY Month_Name
    """,
    "Transaction Comparison (Online vs Cash)": """
        SELECT
          ROUND(
                (COUNT(CASE WHEN Payment_Mode IN ('Wallet', 'UPI', 'Credit card', 'Debit card') THEN 1 END) * 100.0 / COUNT(*)), 2
            ) AS Online_Transactions_Percentage,
            ROUND(
                (COUNT(CASE WHEN Payment_Mode = 'Cash' THEN 1 END) * 100.0 / COUNT(*)), 2
            ) AS Cash_Transactions_Percentage
        FROM expense
    """,
    "Subscription Description Query": """
        SELECT * FROM expense 
        WHERE Description LIKE '%Subscription%'
    """,
    "Months with Expenses Exceeding 31,000": """
        SELECT MONTHNAME(Date) AS Month_name , SUM(Amount) as tot_amount 
        FROM expense 
        GROUP BY Month_name
        HAVING tot_amount > 31000 
    """,
    "Top Expense Categories with Ranking": """
        SELECT Category , SUM(Amount)  AS tot_amount,
        RANK() OVER(ORDER BY SUM(Amount) DESC) AS rank_value
        FROM expense
        GROUP BY Category
        ORDER BY rank_value
    """,
    "Total Amount Spent on Groceries": """
        SELECT Category , SUM(Amount) AS tot_amount 
        FROM expense  
        WHERE Category = 'Groceries'
    """,
    "Minimum Cashback Transactions": """
        SELECT Date , Category , Cashback 
        FROM expense 
        WHERE Cashback < 6
    """,
    "Highest Spending Day": """
        SELECT Date, MAX(Amount) AS Highest_Amount
        FROM expense
        GROUP BY Date
        ORDER BY Highest_Amount DESC
        LIMIT 1
    """,
    "Number of Transactions by Payment Mode": """
        SELECT Payment_Mode , COUNT(*)
        FROM expense 
        GROUP BY Payment_Mode
    """,
    "Transactions by Month": """
        SELECT MONTHNAME(Date) AS Month_name , COUNT(Amount)
        FROM expense 
        GROUP BY MONTHNAME(Date)
    """,
    "Spending Analysis (Total, Average, Max)": """
        SELECT SUM(Amount) AS tot_amount, 
        AVG(Amount) AS avg_amount , 
        MAX(Amount) AS max_amount
        FROM expense
    """,
    "Least Spent Category": """
        SELECT Category , SUM(Amount) AS tot_amount
        FROM expense
        GROUP BY Category 
        ORDER BY tot_amount 
    """,
    "Transactions Per Day": """
        SELECT Date , COUNT(Amount)
        FROM expense
        GROUP BY Date
    """,
    "Lowest Spending Day": """
        SELECT Date, MIN(Amount) AS Least_Amount
        FROM expense
        GROUP BY Date
        ORDER BY Least_Amount 
    """
    }


    st.title("Expense Tracker - Query Results")

    # Dropdown to select a query
    selected_query = st.selectbox("Select a query to execute:", list(queries.keys()))

    # Run the selected query and display results
    if selected_query:
        query = queries[selected_query]
    try:
        results = run_query(query)
        df_results = pd.DataFrame(results)

        # Display the results
        st.write(f"Results for: {selected_query}")
        st.dataframe(df_results)

    except Exception as e:
        st.error(f"Error executing query: {e}")


#VISUALIZATION Section

elif choice == "Visualization" :    

    # Sidebar for navigation
    st.sidebar.title("Visualization Options")
    options = ["Monthly Expenditure & Growth", "Spending by Category", "Payment Mode Distribution"]
    selected_option = st.sidebar.radio("Select a visualization:", options)

    # Load the dataset 
    @st.cache_data
    def load_data():
        df = pd.read_csv('expenses_consolidated.csv')  # Update with your actual file path
        df['Date'] = pd.to_datetime(df['Date'])
        df['YearMonth'] = df['Date'].dt.to_period('M')  # Extract Year-Month for analysis
        return df

    df = load_data()

    # Visualization 1: Monthly Expenditure & Growth
    if selected_option == "Monthly Expenditure & Growth":
        st.title("Monthly Expenditure & Growth")
    
    # Calculate total expenditure per month
        monthly_expenses = df.groupby('YearMonth')['Amount'].sum()
        monthly_expenses_pct_change = monthly_expenses.pct_change() * 100

    # Plotting total expenditure
        st.subheader("Total Expenditure per Month")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(monthly_expenses.index.astype(str), monthly_expenses, marker='o', label='Total Expenditure')
        ax.set_title('Monthly Expenditure')
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Expenditure')
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(fig)

    # Plotting growth percentage
        st.subheader("Monthly Growth/Decline Percentage")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(monthly_expenses_pct_change.index.astype(str), monthly_expenses_pct_change, color='skyblue', label='Growth (%)')
        ax.axhline(0, color='red', linestyle='--', linewidth=1)  # Line at 0 for comparison
        ax.set_title('Monthly Expenditure Growth/Decline')
        ax.set_xlabel('Month')
        ax.set_ylabel('Growth (%)')
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(fig)

# Visualization 2: Spending by Category
    elif selected_option == "Spending by Category":
        st.title("Spending by Category")

    # Group by category and sum the spending
        spending_by_category = df.groupby('Category')['Amount'].sum()

    # Plotting the spending by category
        fig, ax = plt.subplots(figsize=(8, 6))
        spending_by_category.plot(kind='bar', ax=ax, title='Spending by Category', color='skyblue')
        ax.set_xlabel('Category')
        ax.set_ylabel('Total Amount Paid')
        plt.xticks(rotation=45)
        st.pyplot(fig)

# Visualization 3: Payment Mode Distribution
    elif selected_option == "Payment Mode Distribution":
        st.title("Payment Mode Distribution")

    # Count the number of transactions per payment mode
        payment_mode_distribution = df['Payment_Mode'].value_counts()

    # Display the distribution as a bar chart
        st.subheader("Bar Chart: Payment Mode Distribution")
        fig, ax = plt.subplots(figsize=(10, 6))
        payment_mode_distribution.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Payment Mode Distribution')
        ax.set_xlabel('Payment Mode')
        ax.set_ylabel('Number of Transactions')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Display the distribution as a pie chart
        st.subheader("Pie Chart: Payment Mode Distribution")
        fig, ax = plt.subplots(figsize=(8, 8))
        payment_mode_distribution.plot(
            kind='pie', 
            autopct='%1.1f%%', 
            colors=['#ff9999','#FF0000','#66b3ff','#99ff99','#ffcc99'], 
            startangle=90, 
            ax=ax
        )
        ax.set_ylabel('')
        ax.set_title('Payment Mode Distribution (Pie Chart)')
        st.pyplot(fig)


elif choice == "Insights & Recommendations":
    st.title("Enhanced Insights & Recommendations")

    # Load and preprocess the dataset
    @st.cache_data
    def load_data():
        df = pd.read_csv('expenses_consolidated.csv')  # Replace with your actual file path
        df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is in datetime format
        df['YearMonth'] = df['Date'].dt.to_period('M')  # Extract Year-Month for analysis
        return df

    # Load the data
    df = load_data()

    # Calculate key insights
    st.subheader("Key Insights")

    # 1. Average monthly spending
    avg_monthly_spending = df.groupby(df['YearMonth'])['Amount'].sum().mean()
    st.write(f"**Average Monthly Spending**: ₹{avg_monthly_spending:.2f}")

    # 2. Highest spending category
    spending_by_category = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    highest_spending_category = spending_by_category.idxmax()
    st.write(f"**Highest Spending Category**: {highest_spending_category} (₹{spending_by_category.max():.2f})")

    # 3. Lowest spending category
    lowest_spending_category = spending_by_category.idxmin()
    st.write(f"**Lowest Spending Category**: {lowest_spending_category} (₹{spending_by_category.min():.2f})")

    # 4. Day with the highest spending
    highest_spending_day = df.loc[df['Amount'].idxmax()]
    st.write(f"**Day with the Highest Spending**: {highest_spending_day['Date']} (₹{highest_spending_day['Amount']:.2f})")

    # 5. Monthly spending trend (growth or decline)
    monthly_expenses = df.groupby('YearMonth')['Amount'].sum()
    monthly_growth = monthly_expenses.pct_change().mean() * 100
    spending_trend = "Growth" if monthly_growth > 0 else "Decline"
    st.write(f"**Monthly Spending Trend**: {spending_trend} ({monthly_growth:.2f}% change on average)")

    # 6. Cashback insights
    avg_cashback = df['Cashback'].mean()
    st.write(f"**Average Cashback per Transaction**: ₹{avg_cashback:.2f}")

    # Recommendations Section
    st.subheader("Actionable Recommendations")

    # 1. Reduce spending in the highest spending category
    st.write(f"- Focus on reducing expenses in the **{highest_spending_category}** category, as it accounts for the majority of your spending.")

    # 2. Increase savings on low-expense days
    lowest_spending_days = df.groupby(df['Date'].dt.day_name())['Amount'].sum().idxmin()
    st.write(f"- You spend the least on **{lowest_spending_days}**. Plan larger purchases or savings strategies for those days.")

    # 3. Optimize payment modes
    payment_mode_analysis = df['Payment_Mode'].value_counts(normalize=True) * 100
    most_used_payment_mode = payment_mode_analysis.idxmax()
    st.write(f"- Most transactions are made using **{most_used_payment_mode}**. Consider optimizing rewards or cashback for this mode.")

    # 4. Plan for high-spending months
    highest_spending_month = monthly_expenses.idxmax()
    st.write(f"- Spending was highest in **{highest_spending_month}**. Budget carefully for similar months in the future.")

    # 5. Improve cashback strategies
    st.write(f"- Your average cashback is **₹{avg_cashback:.2f}**. Increase usage of payment methods offering higher cashback.")



