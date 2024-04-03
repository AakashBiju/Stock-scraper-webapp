# Stock Data Scraper

Stock Data Scraper is a web application built using Streamlit, Python, and data scraping techniques to fetch and display essential stock data including market information, financial ratios, growth rates, and more. 
This implements a growth-RoC DCF model with explicit fade period

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Retrieves stock data including company name, price, FY23 PE, and RoCE.
- Displays Compounded Sales Growth (CSG) and Compounded Profit Growth (CPG) charts over different time periods.
- Calculates and displays the intrinsic PE and degree of overvaluation based on user inputs.
- Interactive sliders for user input and real-time updating of calculations.

## Installation

To run the application locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/stock-data-scraper.git
   ```

2. Navigate to the project directory:

   ```bash
   cd stock-data-scraper
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   streamlit run main.py
   ```

## Usage

1. Enter the NSE/BSE symbol of the company in the input field.
2. Click the "Get Stock Data" button to fetch and display the stock data.
3. Adjust the sliders in the right pane to change user inputs for intrinsic PE and degree of overvaluation calculations.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/new-feature`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

You can modify and expand this template based on the specifics of your project, such as adding more detailed instructions, including screenshots, or providing additional information about the technology stack used.
