# Contributing to GPU Stress Test Tool

Thank you for considering contributing to this project! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your system info (GPU model, OS, driver version)
- Relevant log output

### Suggesting Features

Feature requests are welcome! Please:
- Check existing issues first to avoid duplicates
- Clearly describe the feature and its benefits
- Explain your use case

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test thoroughly**
   ```bash
   python3 benchmark.py --duration 2 --non-interactive
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: automatic CPU stress testing"
   ```
6. **Push and create a Pull Request**

### Code Style Guidelines

- Use Python 3.7+ compatible syntax
- Follow PEP 8 style guide
- Use descriptive variable names
- Add docstrings for functions and classes
- Keep functions focused and modular

### Testing Checklist

Before submitting a PR, ensure:
- [ ] Code runs without errors
- [ ] Tested on at least one NVIDIA GPU
- [ ] Safety mechanisms still work
- [ ] Documentation updated
- [ ] No PII or sensitive data included
- [ ] New dependencies documented

### Areas for Contribution

We especially welcome contributions in:

- **AMD GPU Support** - Extend to AMD GPUs using rocm-smi
- **Windows Support** - Port to Windows platform
- **CPU Stress Testing** - Integrate CPU stress tools
- **Web Dashboard** - Real-time monitoring web interface
- **Statistical Analysis** - Better result analysis and visualization
- **Multi-GPU Support** - Test multiple GPUs simultaneously
- **Temperature Prediction** - ML-based thermal prediction
- **Automated Reporting** - Generate PDF/HTML reports

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/gpu-stress-test.git
cd gpu-stress-test

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt  # If we add this later

# Run tests
./run-benchmark.sh --duration 2
```

## Pull Request Process

1. Update README_PUBLIC.md with any new features
2. Add your changes to a CHANGELOG.md if one exists
3. Ensure all tests pass
4. Request review from maintainers
5. Address any feedback

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory comments
- Trolling or insulting remarks
- Publishing others' private information
- Other unprofessional conduct

## Questions?

Feel free to:
- Open a discussion on GitHub
- Comment on existing issues
- Reach out to maintainers

Thank you for making this project better! 🚀
