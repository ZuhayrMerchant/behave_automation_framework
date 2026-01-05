# 🔧 Python Selenium + Behave Automation Framework

A lightweight and scalable test automation framework built using **Python**, **Selenium WebDriver**, and **Behave** (BDD). This setup is ideal for web-based UI testing using the Page Object Model (POM).

---

## 📁 Folder Structure (Auto-Created by `framework_setup.py`) <br>
├── config/ <br>
│    └── config.yaml <br>
├── features/ <br>
│    └── environment.py <br>
│    └── test.feature <br>
│    └── steps/ <br>
│          └── test_step.py <br>
├── pages/ <br>
│    └── basePage.py <br>
├── testData/ <br>
│    └── testdata.csv <br>
├── reports/ <br>
|    └── logs <br>
|          └── logfile.txt <br>
|    └── screenshots <br>
├── utils/ <br>
│    └── actions.py <br>
│    └── attachments.py <br>
│    └── config_reader.py <br>
│    └── csv_util.py <br>
│    └── log_util.py <br>
├── behave.ini <br>
├── requirements.txt <br>
├── setup_framework.py <br>

---

## 🚀 Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/ZuhayrMerchant/behave_automation_framework.git
```


## 💻 Setup Guide
🪟 Windows Instructions
```1. Install Python
Download Python 3.12+ from: https://www.python.org/downloads/windows/
✅ During install, check: “Add Python to PATH”
```
2. Install Required Python Packages
```bash
pip install requirements.txt
```
3. Generate Framework Files
```bash
cd behave_automation_framework
python framework_setup.py
```


🍎 macOS Instructions
1. Install Python
Use Homebrew (recommended):
```bash
brew install python 
```
3. Install Required Python Packages
```bash
pip install requirements.txt
```
4. Generate Framework Files
```bash
python framework_setup.py
```

## 🧪 Running Tests
From the root directory, run:
```bash
behave
```
Modify the base config in config/config.yaml:
```yaml
env:
  site_url: "https://google.com/"
  selenium_url: "http://selenium:4444/wd/hub"

driver:
  browser: "chrome"

data:
  test_data_csv: "testData/testdata.csv"
```
Modify the base config in utils/config_reader.py: (when your modification of config.yaml files is completed)
```python
# File Path
def _load_config():
    global config
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")

# Environment
SITE_URL = config["env"]["site_url"]
SELENIUM_URL = config["env"]["selenium_url"]

# Driver
BROWSER = config["driver"]["browser"]

# Data Files
TEST_DATA_CSV = config["data"]["testdata_csv"]
```

Supported browsers: chrome, firefox, edge (you must install the correct driver manually if not using Chrome).

## 🛠 Troubleshooting
| Issue                       | Solution                                                                  |
| --------------------------- | ------------------------------------------------------------------------- |
| `ModuleNotFoundError`       | Ensure you're in the project root folder and installed packages correctly |
| `behave: command not found` | Try using `python -m behave` or reinstall with `pip install behave`       |
| Browser doesn't open        | Check ChromeDriver or geckodriver path & version compatibility            |

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/ZuhayrMerchant/behave_automation_framework/blob/main/LICENSE) file for details.

## 👤 Author
Muhammad Zuhair <br>
📧 zuhair96merchant@gmail.com <br>
🔗 [GitHub
](https://github.com/ZuhayrMerchant)
