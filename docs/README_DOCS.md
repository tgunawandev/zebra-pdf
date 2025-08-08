# 📚 Documentation Index

This directory contains all project documentation except the main README.

## 📋 **Available Documentation**

### **Architecture & Development**
- [`ARCHITECTURE_UPGRADE.md`](ARCHITECTURE_UPGRADE.md) - Complete architecture transformation guide
- [`DOMAIN_INPUT_GUIDE.md`](DOMAIN_INPUT_GUIDE.md) - Custom domain input feature documentation

### **Deployment & Operations**
- [`DOCKER_DEPLOYMENT.md`](DOCKER_DEPLOYMENT.md) - Complete Docker deployment guide

## 🗂️ **Project Structure**

```
zebra-pdf/
├── 📄 README.md                    # Main project documentation
├── 📁 docs/                        # All documentation (this folder)
│   ├── ARCHITECTURE_UPGRADE.md     # Architecture documentation
│   ├── DOCKER_DEPLOYMENT.md        # Docker deployment guide  
│   ├── DOMAIN_INPUT_GUIDE.md       # Domain input feature guide
│   └── README_DOCS.md               # This index file
├── 📁 tests/                       # All test files
│   ├── conftest.py                 # PyTest configuration
│   ├── test_database.py            # Database functionality tests
│   ├── test_domain_input.py        # Domain input tests
│   ├── test_label_service.py       # Label service tests
│   └── test_modular_system.py      # Integration tests
├── 📁 zebra_print/                 # Main application code
└── 🐳 docker-compose.yml           # Docker deployment configuration
```

## 🧪 **Running Tests**

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run tests with coverage
pytest --cov=zebra_print
```

## 🚀 **Quick Links**

- **Getting Started**: See main [`README.md`](../README.md)
- **Docker Deployment**: [`DOCKER_DEPLOYMENT.md`](DOCKER_DEPLOYMENT.md)
- **Domain Configuration**: [`DOMAIN_INPUT_GUIDE.md`](DOMAIN_INPUT_GUIDE.md)
- **Architecture Details**: [`ARCHITECTURE_UPGRADE.md`](ARCHITECTURE_UPGRADE.md)