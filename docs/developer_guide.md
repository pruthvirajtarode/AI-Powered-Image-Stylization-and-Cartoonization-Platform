# 🛠️ Toonify Developer Guide

This guide provides technical documentation for developers working with or deploying the Toonify platform.

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────┐
│              Streamlit Frontend                 │
│  (User Interface, Session Management)           │
└────────────┬────────────────────────────────────┘
             │
             ├─────────────────────────────────────┐
             │                                     │
┌────────────▼────────┐              ┌────────────▼─────────┐
│  Authentication      │              │   Image Processing   │
│     Module           │              │       Module         │
│  - User login        │              │  - OpenCV filters    │
│  - Registration      │              │  - Style effects     │
│  - Password hashing  │              │  - Format conversion │
└────────────┬────────┘              └────────────┬─────────┘
             │                                     │
             │                                     │
┌────────────▼──────────────────────────────────┐ │
│            Database Module                      │ │
│  - SQLite storage                               │ │
│  - User data, transactions, history             │ │
└────────────┬──────────────────────────────────┘ │
             │                                     │
             │        ┌────────────────────────────▼─┐
             │        │    Payment Module             │
             └────────►  - Stripe integration         │
                      │  - Transaction processing     │
                      └───────────────────────────────┘
```

### Technology Stack

- **Frontend Framework**: Streamlit 1.31.0
- **Image Processing**: OpenCV 4.9.0, NumPy, Pillow
- **Database**: SQLite3 (can be migrated to PostgreSQL)
- **Authentication**: bcrypt for password hashing
- **Payment Gateway**: Stripe API
- **Python Version**: 3.8+

## 📂 Project Structure Details

```
AI-Powered Image Stylization and Cartoonization Platform/
│
├── app.py                      # Main Streamlit application entry point
│
├── config/                     # Configuration management
│   ├── __init__.py
│   └── settings.py            # Environment variables, constants
│
├── modules/                   # Core business logic
│   ├── __init__.py
│   ├── authentication.py      # User auth, validation
│   ├── database.py           # Database operations
│   ├── image_processing.py   # OpenCV image processing
│   └── payment.py            # Payment integration
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── validators.py         # Input validation
│   └── helpers.py            # Helper functions
│
├── scripts/                   # Utility scripts
│   ├── init_db.py            # Database initialization
│   └── test_processing.py    # Image processing tests
│
├── tests/                     # Unit tests
│   ├── test_auth.py
│   ├── test_processing.py
│   └── test_payment.py
│
├── data/                      # Data storage
│   ├── users.db              # SQLite database
│   └── processed_images/     # Temporary image storage
│
├── assets/                    # Static assets
│   ├── css/
│   ├── images/
│   └── samples/
│
└── docs/                      # Documentation
    ├── user_guide.md
    ├── developer_guide.md
    └── api_reference.md
```

## 🔧 Setup for Development

### 1. Environment Setup

```bash
# Clone repository
cd "AI-Powered Image Stylization and Cartoonization Platform"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Configure environment variables:

```env
# Application
SECRET_KEY=generate_a_random_secret_key_here
DEBUG=True

# Database
DATABASE_PATH=./data/users.db

# Payment (for production)
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLIC_KEY=pk_test_your_key
PAYMENT_AMOUNT=299  # in cents

# Image Processing
MAX_IMAGE_SIZE=10485760
PROCESSED_IMAGE_QUALITY=95
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Run Application

```bash
streamlit run app.py
```

Access at: `http://localhost:8501`

## 🔬 Module Details

### Authentication Module (`modules/authentication.py`)

**Key Functions:**

```python
# Password hashing
hash_password(password: str) -> str

# Password verification
verify_password(password: str, hashed: str) -> bool

# User registration
register_user(username, email, password, full_name) -> (bool, str)

# User login
login_user(username, password) -> (bool, dict, str)

# Validation
validate_email(email: str) -> bool
validate_password(password: str) -> (bool, str)
validate_username(username: str) -> (bool, str)
```

**Security Features:**
- bcrypt password hashing (10 rounds)
- Strong password requirements
- Email format validation
- Session management with Streamlit

### Image Processing Module (`modules/image_processing.py`)

**Key Functions:**

```python
# Main processing
process_image(image: np.ndarray, style: str) -> (np.ndarray, float)

# Individual effects
apply_classic_cartoon(image) -> np.ndarray
apply_sketch_effect(image) -> np.ndarray
apply_pencil_color(image) -> np.ndarray
apply_oil_painting(image) -> np.ndarray

# Utilities
resize_image(image, max_width, max_height) -> np.ndarray
create_comparison(original, processed) -> np.ndarray
get_image_bytes(image, format, quality) -> bytes
```

**Image Processing Pipeline:**

1. **Classic Cartoon**:
   - Bilateral filter (edge-preserving smoothing)
   - Grayscale conversion
   - Median blur (noise reduction)
   - Adaptive threshold (edge detection)
   - K-means color quantization
   - Edge overlay

2. **Sketch Effect**:
   - Grayscale conversion
   - Inversion
   - Gaussian blur
   - Dodge blend

3. **Pencil Color**:
   - OpenCV pencilSketch()
   - Sigma tuning for artistic effect

4. **Oil Painting**:
   - Stylization filter
   - HSV color enhancement

### Database Module (`modules/database.py`)

**Schema:**

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN
);

-- Transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    transaction_id TEXT UNIQUE,
    amount REAL,
    currency TEXT,
    status TEXT,
    payment_method TEXT,
    image_filename TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Processing history
CREATE TABLE processing_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    original_filename TEXT,
    processed_filename TEXT,
    style TEXT,
    processing_time REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Key Operations:**

```python
# User operations
create_user(username, email, password_hash, full_name)
get_user_by_username(username)
get_user_by_email(email)
update_user_profile(user_id, **kwargs)

# Transaction operations
create_transaction(user_id, transaction_id, amount, ...)
update_transaction_status(transaction_id, status)
get_user_transactions(user_id)

# History operations
add_processing_history(user_id, original, processed, style, time)
get_user_history(user_id, limit)
get_user_stats(user_id)
```

### Payment Module (`modules/payment.py`)

**Integration:**

```python
# Create payment intent
create_payment_intent(user_id, image_filename) -> (bool, str, str)

# Process demo payment
process_demo_payment(user_id, image_filename) -> (bool, str, str)

# Verify payment
verify_payment(transaction_id) -> bool

# Get purchase history
get_user_purchase_history(user_id) -> list
```

**Stripe Integration (Production):**

```python
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create payment intent
intent = stripe.PaymentIntent.create(
    amount=PAYMENT_AMOUNT,
    currency='usd',
    metadata={'user_id': user_id}
)
```

## 🧪 Testing

### Run All Tests

```bash
# Using pytest
pytest tests/

# With coverage
pytest --cov=modules tests/
```

### Run Individual Test Modules

```bash
# Authentication tests
python tests/test_auth.py

# Image processing tests
python tests/test_processing.py

# Payment tests
python tests/test_payment.py
```

### Manual Testing Script

```bash
# Test image processing
python scripts/test_processing.py
```

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Configure secrets in Streamlit dashboard
4. Deploy

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

Build and run:

```bash
docker build -t toonify .
docker run -p 8501:8501 toonify
```

### Environment Variables (Production)

```env
DEBUG=False
SECRET_KEY=<strong-random-key>
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
DATABASE_PATH=/app/data/users.db
```

## 🔐 Security Considerations

### Password Security
- bcrypt hashing with salt
- Minimum 8 characters
- Complexity requirements enforced
- No password stored in plain text

### Database Security
- Prepared statements (SQL injection prevention)
- Input validation on all user inputs
- Session-based authentication

### File Upload Security
- File size limits enforced
- File type validation
- Filename sanitization
- Temporary file cleanup

### Payment Security
- PCI-DSS compliant (via Stripe)
- No credit card data stored locally
- Transaction verification

## 📈 Performance Optimization

### Image Processing
- Automatic image resizing for large files
- Efficient OpenCV algorithms
- Numpy vectorization

### Database
- Indexed columns (username, email)
- Connection pooling for high load
- Query optimization

### Caching
- Streamlit's built-in caching
- Session state for user data

## 🐛 Debugging

### Enable Debug Mode

```python
# In .env
DEBUG=True
```

### Streamlit Debug Info

```bash
# Run with verbose logging
streamlit run app.py --logger.level=debug
```

### Common Issues

1. **OpenCV installation fails**:
   ```bash
   pip install opencv-python-headless
   ```

2. **Database locked**: 
   - Check file permissions
   - Ensure single connection per operation

3. **Memory issues with large images**:
   - Reduce MAX_IMAGE_SIZE
   - Implement image chunking

## 📝 Code Style

Follow PEP 8 guidelines:

```bash
# Install linting tools
pip install flake8 black

# Format code
black .

# Lint code
flake8 modules/ utils/ app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

## 📞 Developer Support

For technical questions:
- **Email**: dev@toonify.com
- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues

---

**Happy coding! 🚀**

*Version 1.0.0 - Developer Guide*
