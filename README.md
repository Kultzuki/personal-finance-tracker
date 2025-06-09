# Personal Finance Tracker 💰

A modern, full-stack web application built with Flask for managing personal finances. Track your income, expenses, and financial goals with an intuitive dashboard and beautiful visualizations.

## 🌟 Features

### 💳 Transaction Management
- **Income & Expense Tracking**: Categorize and manage all your financial transactions
- **Smart Categories**: Predefined categories for income (Salary, Freelance, Investment) and expenses (Food, Transportation, Entertainment, etc.)
- **Date-based Filtering**: View transactions by specific time periods
- **Transaction History**: Complete audit trail of all financial activities

### 🎯 Goal Setting & Tracking
- **Financial Goals**: Set and track progress toward savings and financial objectives
- **Progress Visualization**: Monitor goal completion with intuitive progress bars
- **Deadline Management**: Set target dates and track urgency
- **Goal Status Tracking**: Active, paused, and completed goal states

### 📊 Analytics & Insights
- **Interactive Dashboard**: Real-time overview of financial health
- **Visual Charts**: Spending by category and income vs expenses visualization
- **Monthly Summaries**: Track financial trends over time
- **Financial Metrics**: Net balance, total income, expenses, and goal progress

### 🔐 Security & User Management
- **Secure Authentication**: User registration and login with password hashing
- **Session Management**: Secure user sessions with Flask-Login
- **Data Isolation**: Users can only access their own financial data
- **Password Security**: Secure password hashing with Werkzeug

## 🛠️ Technical Stack

### Backend
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: Flask-Login with secure password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Architecture**: Blueprint-based modular design

### Frontend
- **UI Framework**: Bootstrap 5 for responsive design
- **Charts**: Chart.js for interactive data visualization
- **Icons**: Bootstrap Icons
- **Responsive Design**: Mobile-first approach

### Development & Testing
- **Testing**: Pytest with comprehensive test suite
- **Code Quality**: Pre-commit hooks and linting
- **Environment**: Virtual environment management
- **Database Migrations**: SQLAlchemy-based schema management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/personal-finance-tracker.git
   cd personal-finance-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   # The database will be created automatically on first run
   # Configuration is handled in instance/config.py
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📱 Usage

### Getting Started
1. **Register**: Create a new account with username and password
2. **Login**: Access your personal dashboard
3. **Add Transactions**: Record income and expenses with categories
4. **Set Goals**: Define financial objectives and track progress
5. **Monitor Progress**: Use the dashboard to view your financial health

### Demo Account
For testing purposes, you can use the demo account:
- **Username**: demo
- **Password**: demo123

## 🏗️ Project Structure

```
personal-finance-tracker/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── forms/               # WTF forms for user input
│   ├── models/              # SQLAlchemy database models
│   ├── routes/              # Blueprint route handlers
│   ├── static/              # CSS, JS, and images
│   ├── templates/           # Jinja2 HTML templates
│   └── utils/               # Utility functions
├── instance/
│   └── config.py            # Application configuration
├── tests/                   # Comprehensive test suite
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md               # Project documentation
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/test_models.py    # Model tests
pytest tests/test_routes.py    # Route tests
pytest tests/test_forms.py     # Form validation tests
```

## 🌟 Key Features Showcase

### Modern UI Design
- Clean, professional interface with Bootstrap 5
- Responsive design that works on all devices
- Intuitive navigation and user experience
- Interactive charts and visualizations

### Robust Backend
- SQLAlchemy ORM for database management
- Flask blueprints for modular architecture
- Comprehensive form validation
- Secure authentication system

### Best Practices
- CSRF protection on all forms
- SQL injection prevention through ORM
- Secure password hashing
- Session management
- Error handling and validation

## 🔧 Configuration

The application uses environment-based configuration:

- **Development**: Debug mode enabled, local SQLite database
- **Production**: Environment variables for sensitive data
- **Database**: Configurable database URI
- **Security**: Secret key for session management

## 📈 Future Enhancements

- **Export Functionality**: PDF and CSV export of financial data
- **Budget Planning**: Monthly budget creation and tracking
- **Investment Tracking**: Portfolio management features
- **Mobile App**: React Native mobile application
- **API Integration**: Bank account synchronization
- **Advanced Analytics**: Machine learning insights

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Developer

**Your Name**
- GitHub: [@yourusername](https://github.com/Kultzuki)
- LinkedIn: [Your LinkedIn](https://www.linkedin.com/in/prashant-krishan-bharti/)
- Portfolio: [yourwebsite.com](https://yourwebsite.com)

---

⭐ **Star this repository if you found it helpful!**

Built with ❤️ using Flask, Bootstrap, and modern web technologies.
