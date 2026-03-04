# PlasticTracker-
PlasticTrack+ is a Python-based desktop application designed to help users monitor, analyze, and reduce their plastic usage. The project focuses on promoting environmental awareness by allowing users to track daily plastic consumption and understand their usage patterns through visual insights and reports.

The application is developed using Tkinter for the graphical user interface along with ttkbootstrap to provide a modern and visually appealing design. User data is stored locally using SQLite, ensuring lightweight and efficient data management without requiring an external database server.

PlasticTrack+ allows users to log plastic usage by specifying the date, plastic type, quantity, unit, recyclability status, and additional notes. The logged data can be reviewed through a recent entries view, making it easy to keep track of daily activities. The statistics section analyzes stored data over different time periods and presents the results using graphical visualizations created with Matplotlib, including pie charts and bar charts for better understanding.

The application also includes a goal-setting feature where users can define plastic reduction targets within a specific time frame. This encourages sustainable behavior by helping users stay aware of their progress. In addition, PlasticTrack+ features a built-in reusable product store that showcases eco-friendly alternatives to single-use plastics. Users can browse products by category, add items to a cart, and simulate a checkout process.

To support reporting and documentation, PlasticTrack+ can generate monthly PDF reports using ReportLab. These reports summarize plastic usage data and provide simple recommendations based on consumption patterns. Product data is managed through a JSON-based catalog, making it easy to extend or modify in the future.

Overall, PlasticTrack+ serves as an educational and practical desktop application that combines data tracking, visualization, and sustainability awareness in a single platform.
