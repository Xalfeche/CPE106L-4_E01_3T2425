import pandas as pd
import matplotlib.pyplot as plt
import os

# Print the current working directory
print("Current working directory:", os.getcwd())

# Load the data from the CSV file
data = pd.read_csv('breadprice.csv')

# Clean the data by handling missing values (if any)
# In this dataset, missing values are represented as empty strings, so we replace them with NaN
data = data.replace('', pd.NA)

# Calculate the average price for each year by averaging the monthly prices
data['Average Price'] = data.iloc[:, 1:13].mean(axis=1)

# Display basic information about the dataset
print("Bread Price Data Summary:")
print("=" * 40)
print(f"Years covered: {data['Year'].min()} - {data['Year'].max()}")
print(f"Number of years: {len(data)}")
print("\nAverage prices by year:")
for _, row in data.iterrows():
    if pd.notna(row['Average Price']):
        print(f"{int(row['Year'])}: ${row['Average Price']:.3f}")

# Plot the average price for each year
plt.figure(figsize=(10, 6))
plt.plot(data['Year'], data['Average Price'], marker='o', linestyle='-', color='b')

# Add title and labels
plt.title('Average Price of Bread per Year')
plt.xlabel('Year')
plt.ylabel('Average Price')
plt.grid(True)

# Save the plot to a file
plt.savefig('bread_price_plot.png')

# Show the plot
plt.show()

# Print confirmation message
print("\nPlot saved as 'bread_price_plot.png'")