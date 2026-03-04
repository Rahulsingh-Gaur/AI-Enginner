# Jenkins Integration Guide for Allure Reports

## ✅ Prerequisites

### 1. Jenkins Plugins Required
Install these plugins in Jenkins:

| Plugin | Purpose |
|--------|---------|
| **Allure Jenkins Plugin** | Generate and display Allure reports |
| **HTML Publisher Plugin** | Publish HTML reports (alternative) |
| **JUnit Plugin** | Publish JUnit test results |
| **Git Plugin** | Checkout code from Git |
| **Pipeline Plugin** | Use Jenkins Pipeline |

### 2. Allure CLI on Jenkins Agent
Ensure Allure CLI is installed on your Jenkins agent/node:

```bash
# Linux/Mac
brew install allure
# OR
wget https://github.com/allure-framework/allure2/releases/download/2.34.0/allure-2.34.0.tgz
tar -xzf allure-2.34.0.tgz
export PATH=$PATH:/path/to/allure-2.34.0/bin
```

### 3. Python Requirements
The `requirements.txt` already includes:
```
allure-pytest==2.15.3
```

---

## 🚀 Jenkins Pipeline Setup

### Option 1: Using Jenkinsfile (Recommended)

1. The `Jenkinsfile` is already created in the project root
2. Create a new Pipeline job in Jenkins
3. Select "Pipeline script from SCM"
4. Configure your Git repository
5. Build!

### Option 2: Manual Pipeline Configuration

```groovy
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest tests/ --alluredir=reports/allure-results
                '''
            }
        }
        
        stage('Allure Report') {
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'reports/allure-results']]
                ])
            }
        }
    }
}
```

---

## 📊 What Gets Reported in Jenkins

### Allure Report Includes:
- ✅ Test execution status (Pass/Fail/Skip)
- ✅ Test duration and timeline
- ✅ 5-Stage E2E flow steps
- ✅ **Test Summary Attachments:**
  - 📱 Mobile Number
  - 📧 Email
  - 🆔 Profile ID
  - 👤 User Type
  - 📊 Customer Status
  - 🔗 Redirect URI
- ✅ Error details on failure
- ✅ Environment information
- ✅ Jenkins build info (Build #, Job Name)

---

## 🔧 Jenkins Job Configuration

### Freestyle Project Settings:

1. **Source Code Management:**
   - Git repository URL
   - Credentials
   - Branch specifier: `*/main`

2. **Build Environment:**
   - Delete workspace before build starts (optional)

3. **Build Steps:**
   ```bash
   #!/bin/bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pytest tests/ -v --alluredir=reports/allure-results
   ```

4. **Post-build Actions:**
   - **Allure Report:**
     - Path: `reports/allure-results`
   - **Archive Artifacts:**
     - Files to archive: `reports/**/*`
   - **Publish JUnit test result report:**
     - Test report XMLs: `reports/*.xml`

---

## 🐳 Docker Alternative (Recommended for Jenkins)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Install Allure
RUN apt-get update && apt-get install -y wget default-jre
RUN wget https://github.com/allure-framework/allure2/releases/download/2.34.0/allure_2.34.0-1_all.deb
RUN dpkg -i allure_2.34.0-1_all.deb || apt-get install -f -y

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["pytest", "tests/", "--alluredir=reports/allure-results"]
```

Jenkins Pipeline with Docker:
```groovy
pipeline {
    agent {
        docker {
            image 'your-docker-image-with-allure'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'pytest tests/ --alluredir=reports/allure-results'
            }
        }
        stage('Report') {
            steps {
                allure results: [[path: 'reports/allure-results']]
            }
        }
    }
}
```

---

## 📋 Verifying Jenkins Setup

### Test Your Setup:
1. Commit and push `Jenkinsfile`
2. Trigger Jenkins build
3. Check "Allure Report" link in build page
4. Verify test summary with mobile/email/profile_id is visible

### Expected Results:
```
Allure Report
├── Overview (Pass/Fail counts)
├── Categories (Defect types)
├── Suites (Test suites)
├── Graphs (Trends, durations)
└── Test Cases
    └── E2E 5-Stage Authentication Flow
        ├── Steps (Stage 1-5)
        └── Attachments
            ├── 📊 Test Summary (Text)
            └── Test Data (JSON)
```

---

## 🔗 Accessing Reports

### In Jenkins:
1. Go to Build page
2. Click "Allure Report" link
3. View interactive report

### Download Reports:
- Archived artifacts: `reports/allure-html/`
- Raw results: `reports/allure-results/`

---

## ⚠️ Troubleshooting

### Issue: "Allure command not found"
**Fix:** Install Allure CLI on Jenkins agent

### Issue: "No Allure results found"
**Fix:** Check `reports/allure-results` directory exists and contains `.json` files

### Issue: "Permission denied"
**Fix:** Ensure Jenkins user has write permissions to workspace

### Issue: Tests pass but report shows 404
**Fix:** Use `allure serve` or check Allure Jenkins Plugin configuration

---

## ✅ Jenkins Setup Checklist

- [ ] Allure Jenkins Plugin installed
- [ ] Allure CLI installed on agent
- [ ] Python 3.9+ installed on agent
- [ ] Jenkinsfile committed to repo
- [ ] Pipeline job created
- [ ] Git credentials configured
- [ ] Build triggers configured (optional)
- [ ] Email notifications configured (optional)

---

**Your setup is Jenkins-ready! 🎉**
