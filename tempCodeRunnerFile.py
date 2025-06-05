queries = [
#     "What is the name of the bank? Provide only the name no extra information.",

#     f"What is the total revenue reported for quarter {quarter} in year {year}?, Provide Exact values only and no other information. If no exact value found just give output as NULL dont give anything else.",
#     f"What is the net income reported for quarter {quarter} in year {year}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else.",
#     f"What is the date of publishment of conference of quarter {quarter} in year {year}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else.",

#     f"What is the total revenue reported for quarter {prev_q} in year {prev_y}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else.",
#     f"What is the net income reported for quarter {prev_q} in year {prev_y}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else.",
#     f"What is the date of publishment of conference of quarter {prev_q} in year {prev_y}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else.",

#     f"What is the total revenue reported for quarter {quarter} in year {last_y_same_q}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else.",
#     f"What is the net income reported for quarter {quarter} in year {last_y_same_q}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else.",
#     f"What is the date of publishment of conference of quarter {quarter} in year {last_y_same_q}?, Provide Exact values only and no other information.If no exact value found just give output as NULL dont give anything else."
# ]

# # Ask queries and collect answers
# answers = []
# for query in queries:
#     response = query_deepseek(query, context)
#     answer = response['choices'][0]['message']['content']
#     answers.append(answer)
#     print(f"Q: {query}\nA: {answer}\n")

# # Extract rows
# bank_name = answers[0]

# row1 = [bank_name, f"{quarter}Q{str(year)[-2:]}", answers[1], answers[2], answers[3]]
# row2 = [bank_name, f"{prev_q}Q{str(prev_y)[-2:]}", answers[4], answers[5], answers[6]]
# row3 = [bank_name, f"{quarter}Q{str(last_y_same_q)[-2:]}", answers[7], answers[8], answers[9]]

# # Insert into MySQL
# insert_three_rows([row1, row2, row3])
# print("✅ Data inserted into MySQL.")