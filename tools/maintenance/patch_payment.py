import re
import os

base_dir = r"c:\Users\pruth\OneDrive\Desktop\AI-Powered Image Stylization and Cartoonization Platform\frontend\templates"

# Read index.html to extract modals
with open(os.path.join(base_dir, 'index.html'), 'r', encoding='utf-8') as f:
    index_content = f.read()

# Extract payment modal
payment_match = re.search(r'(<div id="paymentModal".*?</div>\s*</div>\s*</div>)', index_content, re.DOTALL)
pay_success_match = re.search(r'(<div id="paySuccessModal".*?</div>\s*</div>\s*</div>)', index_content, re.DOTALL)

if not payment_match or not pay_success_match:
    print("Modals not found in index.html!")
    exit(1)

modals_html = f"\n\n    {payment_match.group(1)}\n\n    <!-- Payment Success Modal -->\n    {pay_success_match.group(1)}\n\n"

razorpay_script = '<script src="https://checkout.razorpay.com/v1/checkout.js"></script>'

for file in ['gallery.html', 'dashboard.html']:
    file_path = os.path.join(base_dir, file)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add modals if not present
    if 'id="paymentModal"' not in content:
        content = content.replace('</body>', f"{modals_html}</body>")
        print(f"Added modals to {file}")

    # Add razorpay script if not present
    if 'checkout.razorpay.com' not in content:
        content = re.sub(r'(<script src="/static/js/app.js)', f'{razorpay_script}\n    \\1', content)
        print(f"Added Razorpay script to {file}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Patching complete!")
