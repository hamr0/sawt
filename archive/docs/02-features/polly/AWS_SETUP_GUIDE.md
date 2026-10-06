# AWS Setup Guide for Amazon Polly Integration

This guide walks you through setting up AWS credentials for the Amazon Polly TTS integration.

**Estimated Time:** 15-20 minutes  
**Cost:** Free (AWS Free Tier includes 5 million characters/month for 12 months)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Create AWS Account](#step-1-create-aws-account)
3. [Step 2: Create IAM User](#step-2-create-iam-user)
4. [Step 3: Generate Access Keys](#step-3-generate-access-keys)
5. [Step 4: Configure Credentials](#step-4-configure-credentials)
6. [Step 5: Verify Setup](#step-5-verify-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Email address for AWS account
- Credit/debit card (required for AWS account, but won't be charged within free tier limits)
- Python 3.7+ installed
- boto3 package installed (`pip install boto3>=1.28.0`)

---

## Step 1: Create AWS Account

If you don't have an AWS account:

1. Go to [https://aws.amazon.com/](https://aws.amazon.com/)
2. Click **"Create an AWS Account"**
3. Follow the registration process:
   - Enter email address and account name
   - Provide contact information
   - Enter payment information (required but won't be charged within free tier)
   - Verify identity via phone
   - Select **"Basic Support - Free"** plan
4. Sign in to AWS Console at [https://console.aws.amazon.com/](https://console.aws.amazon.com/)

**Free Tier Benefits:**
- 5 million characters per month (Neural voices) for first 12 months
- Approximately 8-10 audiobooks per month at 100,000 words each

---

## Step 2: Create IAM User

**Why IAM User?** Using IAM users instead of root credentials is a security best practice.

### 2.1 Navigate to IAM

1. Sign in to AWS Console
2. In the search bar at top, type **"IAM"**
3. Click **"IAM"** (Identity and Access Management)

### 2.2 Create User

1. In left sidebar, click **"Users"**
2. Click **"Create user"** button
3. **User name:** Enter `polly-tts-user` (or your preferred name)
4. Click **"Next"**

### 2.3 Set Permissions

1. Select **"Attach policies directly"**
2. In the search box, type: **"Polly"**
3. Check the box next to **"AmazonPollyReadOnlyAccess"**
   
   **Note:** For this POC, read-only access is sufficient. The required permission is:
   - `polly:SynthesizeSpeech`

4. Click **"Next"**
5. Review and click **"Create user"**

### 2.4 Minimal IAM Policy (Alternative)

If you prefer minimal permissions, use this custom policy instead:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "polly:SynthesizeSpeech"
            ],
            "Resource": "*"
        }
    ]
}
```

**To apply custom policy:**
1. Instead of "Attach policies directly", select "Create inline policy"
2. Switch to JSON tab
3. Paste the policy above
4. Name it: `PollyTTSMinimal`
5. Create policy and attach to user

---

## Step 3: Generate Access Keys

### 3.1 Create Access Key

1. Click on the user you just created (`polly-tts-user`)
2. Click **"Security credentials"** tab
3. Scroll down to **"Access keys"** section
4. Click **"Create access key"**
5. Select use case: **"Command Line Interface (CLI)"**
6. Check the confirmation box: "I understand..."
7. Click **"Next"**
8. (Optional) Add description tag: "Polly TTS Integration"
9. Click **"Create access key"**

### 3.2 Save Credentials

**IMPORTANT:** This is the only time you can view the secret access key!

1. You'll see:
   - **Access key ID:** `your_access_key_id_here`
   - **Secret access key:** `your_secret_access_key_here`

2. **Download .csv file** OR copy both values to a secure location

3. Click **"Done"**

⚠️ **Security Warning:** Never commit these credentials to Git or share them publicly!

---

## Step 4: Configure Credentials

Choose ONE of the following methods:

### Method 1: Environment Variables (Recommended for Development)

**Linux/macOS:**

```bash
# Add to ~/.bashrc or ~/.zshrc for persistence
export AWS_ACCESS_KEY_ID="your_access_key_id_here"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key_here"
export AWS_DEFAULT_REGION="us-east-1"

# Apply changes
source ~/.bashrc  # or source ~/.zshrc
```

**Windows (PowerShell):**

```powershell
# Add to PowerShell profile for persistence
$env:AWS_ACCESS_KEY_ID="your_access_key_id_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key_here"
$env:AWS_DEFAULT_REGION="us-east-1"
```

**Windows (Command Prompt):**

```cmd
set AWS_ACCESS_KEY_ID=your_access_key_id_here
set AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
set AWS_DEFAULT_REGION=us-east-1
```

### Method 2: .env File (Recommended for Projects)

1. Copy the `.env.example` file in project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_id_here
   AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **IMPORTANT:** Add `.env` to `.gitignore`:
   ```bash
   echo ".env" >> .gitignore
   ```

4. Load in Python (if needed):
   ```python
   from pathlib import Path
   from dotenv import load_dotenv  # pip install python-dotenv
   
   load_dotenv(Path(__file__).parent / '.env')
   ```

### Method 3: AWS CLI Configuration (Recommended for Production)

1. Install AWS CLI:
   ```bash
   # Ubuntu/Debian
   sudo apt install awscli
   
   # macOS
   brew install awscli
   
   # Windows
   # Download from: https://aws.amazon.com/cli/
   ```

2. Configure credentials:
   ```bash
   aws configure
   ```

3. Enter when prompted:
   - **AWS Access Key ID:** `your_access_key_id`
   - **AWS Secret Access Key:** `your_secret_access_key`
   - **Default region name:** `us-east-1`
   - **Default output format:** `json`

4. Credentials are stored in `~/.aws/credentials` (Linux/macOS) or `%USERPROFILE%\.aws\credentials` (Windows)

### Method Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| Environment Variables | Simple, no files | Not persistent (unless in profile) | Quick testing |
| .env File | Project-specific, easy to manage | Need to load manually in code | Development |
| AWS CLI Config | Persistent, secure, standard | Requires AWS CLI installation | Production |

**Recommendation:** Use AWS CLI Config (Method 3) for production, .env file (Method 2) for development.

---

## Step 5: Verify Setup

### 5.1 Test boto3 Import

```bash
python3 -c "import boto3; print(f'boto3 version: {boto3.__version__}')"
```

**Expected output:**
```
boto3 version: 1.40.64
```

### 5.2 Test AWS Connection

Create a test script `test_aws_connection.py`:

```python
import boto3

try:
    # Initialize Polly client
    polly = boto3.client('polly', region_name='us-east-1')
    
    # List available voices
    response = polly.describe_voices(LanguageCode='ar')
    
    print("✅ AWS Polly connection successful!")
    print(f"\nAvailable Arabic voices:")
    for voice in response['Voices']:
        print(f"  - {voice['Name']} ({voice['Gender']}, {voice['LanguageCode']})")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Verify credentials are set correctly")
    print("2. Check IAM user has Polly permissions")
    print("3. Ensure AWS_DEFAULT_REGION is set to 'us-east-1'")
```

Run the test:
```bash
python3 test_aws_connection.py
```

**Expected output:**
```
✅ AWS Polly connection successful!

Available Arabic voices:
  - Zeina (Female, arb)
  - Hala (Female, ar-AE)
```

---

## Troubleshooting

### Error: "NoCredentialsError: Unable to locate credentials"

**Cause:** AWS credentials not configured

**Solutions:**
1. Verify environment variables are set:
   ```bash
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_SECRET_ACCESS_KEY
   ```
2. Check `~/.aws/credentials` file exists and contains valid credentials
3. Try Method 1 (Environment Variables) as a quick test

### Error: "An error occurred (UnrecognizedClientException)"

**Cause:** Invalid access key ID or secret access key

**Solutions:**
1. Verify you copied the credentials correctly (no extra spaces)
2. Generate new access keys in IAM Console
3. Ensure you're using the correct AWS account

### Error: "An error occurred (AccessDeniedException)"

**Cause:** IAM user lacks Polly permissions

**Solutions:**
1. Go to IAM Console → Users → your user
2. Click "Permissions" tab
3. Verify "AmazonPollyReadOnlyAccess" or custom policy is attached
4. If using custom policy, ensure it includes `polly:SynthesizeSpeech`

### Error: "EndpointConnectionError: Could not connect to the endpoint URL"

**Cause:** Network connectivity issues or wrong region

**Solutions:**
1. Check internet connection
2. Verify `AWS_DEFAULT_REGION=us-east-1`
3. Try different region (e.g., `us-west-2`)
4. Check firewall/proxy settings

### Error: "SignatureDoesNotMatch"

**Cause:** System clock is out of sync

**Solutions:**
1. Sync system clock:
   ```bash
   # Linux
   sudo ntpdate -s time.nist.gov
   
   # macOS
   sudo sntp -sS time.apple.com
   ```
2. Regenerate access keys if issue persists

---

## Security Best Practices

1. **Never commit credentials to Git**
   - Add `.env` to `.gitignore`
   - Use environment variables or AWS CLI config
   
2. **Use IAM users, not root credentials**
   - Create dedicated IAM user for this project
   - Apply principle of least privilege
   
3. **Rotate access keys regularly**
   - AWS recommends rotating every 90 days
   - Delete old keys after rotation
   
4. **Monitor usage**
   - Check AWS billing dashboard regularly
   - Set up billing alerts for unexpected charges
   
5. **Use MFA for AWS account**
   - Enable Multi-Factor Authentication on root account
   - Consider MFA for IAM users in production

---

## Cost Management

### Free Tier Limits

- **Neural voices:** 5 million characters/month (first 12 months)
- **Standard voices:** 5 million characters/month (always free)

### After Free Tier

- **Neural voices:** $16.00 per 1 million characters
- **Standard voices:** $4.00 per 1 million characters

### Cost Examples

| Usage | Characters | Cost (Neural) | Cost (Standard) |
|-------|-----------|---------------|-----------------|
| This POC (5 test sentences) | ~500 | $0.00 | $0.00 |
| 100k word audiobook | ~600,000 | $9.60 | $2.40 |
| 10 audiobooks/month | ~6,000,000 | $96.00 | $24.00 |

### Setting Up Billing Alerts

1. Go to AWS Console → Billing Dashboard
2. Click "Budgets" in left sidebar
3. Click "Create budget"
4. Select "Cost budget"
5. Set amount (e.g., $10/month)
6. Enter email for alerts
7. Create budget

---

## Next Steps

✅ AWS credentials configured successfully!

**Now you can:**

1. Run the Polly integration test script:
   ```bash
   python scripts/test_polly_integration.py
   ```

2. Read the [Polly Usage Guide](POLLY_USAGE_GUIDE.md) for code examples

3. Proceed with POC validation (Task 5.0 in task list)

---

## Additional Resources

- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [Amazon Polly Documentation](https://docs.aws.amazon.com/polly/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [boto3 Polly Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly.html)

---

**Questions or issues?** Check the [Troubleshooting](#troubleshooting) section or review the Polly Implementation Plan.
