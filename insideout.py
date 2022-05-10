import pandas as pd
import streamlit as st


def by_employee_by_date(employee, date, data):
    by_date = data[data["Date"].dt.date == date]
    by_employee = (
        by_date[by_date["Employee"].map(lambda x: employee in x)]
        .assign(e=lambda x: x["Amount"] * 0.65, c=lambda x: x["Amount"] * 0.35)
        .rename(columns={"e": "To employee", "c": "To company"})
    )
    total = by_employee[["Amount", "To employee", "To company"]].sum().rename("Total")
    return by_employee[
        ["Customer", "Employee", "Date", "Amount", "To employee", "To company"]
    ].append(total)


"""
# InsideOut Reports
"""

uploaded_file = st.file_uploader(
    "Upload an CSV export from HouseCall Pro to start generating reports."
)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file).set_index("Invoice")

    # Date types
    data["Date"] = pd.to_datetime(data["Date"])
    data["Finished"] = pd.to_datetime(data["Finished"])

    # Number types
    def money_to_float(text):
        return float(text[1:])

    data[["Amount", "Labor", "Materials", "Subtotal"]] = data[
        ["Amount", "Labor", "Materials", "Subtotal"]
    ].applymap(money_to_float)

    # List types
    def split_tags(text):
        tags = text.split(sep=",")
        return list(map(str.strip, tags))

    data[["Customer Tags", "Job Tags", "Employee"]] = (
        data[["Customer Tags", "Job Tags", "Employee"]].fillna("").applymap(split_tags)
    )

    employees = sorted(data["Employee"].explode().unique())

    employee = st.selectbox("Employee:", employees)
    date = st.date_input("Date:")

    st.write(by_employee_by_date(employee, date, data))
