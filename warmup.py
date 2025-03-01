import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import os

# Load the data
data = pd.read_csv('data.csv')

# Create a scatter plot
plt.scatter(data['x'], data['y'])
plt.xlabel('x')
plt.ylabel('y')
plt.title('Scatter plot of x and y')
plt.show()

# Calculate the correlation coefficient
correlation = np.corrcoef(data['x'], data['y'])[0, 1]
print('The correlation coefficient is:', correlation)

# Calculate the mean of x and y
mean_x = np.mean(data['x'])
mean_y = np.mean(data['y'])
print('The mean of x is:', mean_x)
print('The mean of y is:', mean_y)

# Calculate the standard deviation of x and y
std_x = np.std(data['x'])
std_y = np.std(data['y'])
print('The standard deviation of x is:', std_x)
print('The standard deviation of y is:', std_y)

# Calculate the slope and intercept of the regression line
slope = correlation * std_y / std_x
intercept = mean_y - slope * mean_x
print('The slope of the regression line is:', slope)
print('The intercept of the regression line is:', intercept)

# Plot the regression line
plt.scatter(data['x'], data['y'])
plt.plot(data['x'], slope * data['x'] + intercept, color='red')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Scatter plot of x and y with regression line')
plt.show()

# Load json data
json_data = pd.read_json('data.json')

# detect json data with multiple lines
json_data = pd.read_json('data.json', lines=True)

# Load json data with orient='records'
json_data = pd.read_json('data.json', orient='records')

# Load json data with orient='split'
json_data = pd.read_json('data.json', orient='split')

# Load json data with orient='index'
json_data = pd.read_json('data.json', orient='index')

# Load json data with orient='columns'
json_data = pd.read_json('data.json', orient='columns')

# Load json data with orient='values'
json_data = pd.read_json('data.json', orient='values')


def main():
    parser = argparse.ArgumentParser(description='Load data from a file')
    parser.add_argument('filename', type=str,
                        help='The name of the file to load')
    parser.add_argument('--format', type=str,
                        help='The format of the file to load')
    args = parser.parse_args()
    if args.format == 'csv':
        data = pd.read_csv(args.filename)
    elif args.format == 'json':
        data = pd.read_json(args.filename)
    else:
        raise ValueError('Unsupported file format')
    print(data)


# on launch
if __name__ == "__main__":
    main()
