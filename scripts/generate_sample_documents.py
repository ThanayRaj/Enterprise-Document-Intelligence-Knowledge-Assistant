"""Generate original synthetic Northline sample documents (PDF, DOCX, TXT)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import fitz
from docx import Document
from docx.shared import Pt

from src.config import SAMPLE_DOCUMENTS_DIR

EMPLOYEE_HANDBOOK = """NORTHLINE SYSTEMS
Employee Handbook
Effective date: 1 March 2026
Document owner: People Operations
Classification: Internal

1. Purpose
This handbook describes employment expectations at Northline Systems, a fictional company created for software demonstration. It does not describe any real employer.

2. Working hours
Standard office hours are 09:00 to 18:00, Monday through Friday, with a one-hour unpaid lunch break. Core collaboration hours are 10:00 to 16:00 in the employee's primary time zone. Teams may agree a flexible start between 08:00 and 10:00 if coverage is maintained.

3. Probation
New employees complete a 90-day probation period. During probation, either party may end employment with seven calendar days' written notice. A probation review meeting is held between day 70 and day 85.

4. Compensation and pay cycle
Salaries are paid monthly on the last working day of each month. Overtime for eligible non-exempt roles requires written pre-approval from the line manager. Unapproved overtime is not compensated.

5. Annual leave
Full-time employees are entitled to 18 days of paid annual leave per calendar year, accrued monthly. Unused annual leave may be carried over to a maximum of 5 days, which must be used by 31 March of the following year.

6. Public holidays
Northline observes 10 public holidays each year. The holiday calendar is published by People Operations in December for the following year.

7. Conduct
Employees must treat colleagues, contractors, and customers with respect. Harassment, discrimination, and retaliation are prohibited. Suspected misconduct should be reported to People Operations or through the confidential ethics mailbox ethics@northline.example.

8. Equipment
Northline provides a laptop, account credentials, and required software. Company equipment remains Northline property and must be returned on the last working day. Personal software may not be installed on company laptops without IT approval.

9. Performance
Formal performance reviews occur twice each year, in June and December. Goals are documented in the People Portal. A rating of "Needs improvement" triggers a 60-day development plan.

10. Leaving Northline
Resigning employees should give 30 calendar days' written notice after probation. Exit interviews are optional. Access to systems is revoked at end of the last working day unless People Operations approves a shorter period for cause.
"""

LEAVE_POLICY = """NORTHLINE SYSTEMS
Leave Policy
Effective date: 1 March 2026
Document owner: People Operations
Classification: Internal

1. Scope
This policy covers annual leave, sick leave, parental leave, and unpaid leave for full-time Northline Systems employees. Contractors follow their contract terms instead of this policy.

2. Annual leave entitlement
Full-time employees receive 18 days of paid annual leave each calendar year. Part-time employees receive a pro-rated entitlement based on contracted hours. Annual leave requests of 1 to 5 consecutive working days are approved by the line manager in the People Portal.

3. Extended annual leave
Any request for more than 5 consecutive working days of annual leave requires line manager approval and a coverage plan. Requests longer than 10 consecutive working days also require director approval. Employees should submit extended leave at least 21 calendar days in advance unless an emergency applies.

4. Sick leave
Employees receive 12 days of paid sick leave per calendar year. Absences of more than 3 consecutive working days require a medical certificate uploaded to the People Portal. Unused sick leave does not carry over.

5. Parental leave
Primary caregivers receive 16 weeks of paid parental leave. Secondary caregivers receive 4 weeks of paid parental leave. Parental leave may begin up to 2 weeks before the expected arrival date. Employees must notify People Operations at least 8 weeks in advance when the date is known.

6. Bereavement leave
Employees may take up to 5 paid days of bereavement leave for an immediate family member.

7. Unpaid leave
Unpaid leave of up to 30 calendar days may be granted at director discretion when paid leave balances are exhausted. Unpaid leave does not accrue annual leave.

8. Recording leave
All leave must be recorded in the People Portal before the first day of absence except sudden illness, which must be recorded within 24 hours. Managers must respond to leave requests within 3 working days.
"""

TRAVEL_POLICY = """NORTHLINE SYSTEMS
Travel Policy
Effective date: 15 January 2026
Document owner: Finance
Classification: Internal

1. Purpose
This policy explains when Northline Systems employees may travel, how travel is approved, and which expenses are reimbursable.

2. Approval
Domestic travel requires line manager approval in the Travel Desk before tickets are booked. International travel requires director approval and a completed risk checklist. Travel booked without the required approval is not reimbursed.

3. Booking
Air travel inside the same continent should be economy class. Business class is allowed only for flights longer than 8 hours and only with director approval. Rail travel should use standard class. Employees must book refundable or changeable fares when meetings are not confirmed.

4. Lodging
Hotel rates should not exceed 180 USD per night in domestic cities or 250 USD per night internationally unless a cheaper safe option is unavailable. Airbnb and unlicensed lodging are not permitted for business travel.

5. Per diem
The domestic per diem for meals and incidentals is 75 USD per full travel day. The international per diem is 120 USD per full travel day. Per diem is halved for travel days under 6 hours. Alcohol is not reimbursable.

6. Ground transport
Airport transfers should use licensed taxis or the company-approved ride account. Rental cars require manager approval and are limited to compact or midsize vehicles. Traffic fines are the employee's responsibility.

7. Combining personal travel
Personal leisure days may be added to a business trip if there is no increase in airfare paid by Northline. Personal hotel nights and meals are not reimbursable.

8. Expense submission
Expense reports are due within 10 working days after return. Receipts are required for any item over 15 USD. Late reports may delay reimbursement to the next monthly cycle.

9. Safety
Employees must share their itinerary with their manager. For international trips, employees enroll in the travel advisory mailing list at least 5 days before departure.
"""

IT_SECURITY_POLICY = """NORTHLINE SYSTEMS
IT Security Policy
Effective date: 1 February 2026
Document owner: Information Security
Classification: Internal

1. Purpose
This policy sets minimum security requirements for Northline Systems systems, accounts, and devices.

2. Accounts and authentication
Every employee receives a unique directory account. Sharing passwords is prohibited. Passwords must be at least 12 characters and must not reuse the last 8 passwords. Multi-factor authentication (MFA) is required for email, VPN, cloud consoles, and the People Portal.

3. Devices
Company laptops must keep disk encryption enabled. Operating system and browser updates must be installed within 7 days of release for critical patches. Personal devices may access mail only through the approved mobile management profile.

4. Removable media
USB storage and other removable media are prohibited unless Information Security issues a written exception for a named project. Exceptions expire after 90 days.

5. Data classification
Public, Internal, Confidential, and Restricted labels apply. Confidential and Restricted data must not be stored in personal cloud accounts. Restricted data, including customer production credentials, may only be stored in the approved secrets manager.

6. Remote access
VPN is required when accessing internal services from outside Northline offices. Split-tunnel VPN is disabled. Unattended sessions must lock after 10 minutes.

7. Incident reporting
Suspected phishing, malware, or lost devices must be reported to security@northline.example within 1 hour of discovery. Employees must not pay ransomware demands.

8. Software
Only software from the approved catalogue may be installed. Open-source tools need a lightweight review by IT if they are not already listed. Browser extensions that read page content are not allowed.

9. Access reviews
Managers review application access quarterly. Access that is unused for 60 days is removed automatically for non-critical systems.
"""

REMOTE_WORK = """NORTHLINE SYSTEMS
Remote Work Policy
Effective date: 1 April 2026
Document owner: People Operations

1. Eligibility
Employees who have completed probation may request a hybrid or fully remote arrangement. Fully remote work is available only for roles listed as location-flexible in the job architecture.

2. Hybrid pattern
The default hybrid pattern is 3 office days and 2 remote days each week. Teams choose office anchor days. Tuesday and Thursday are the company-wide collaboration days unless a regional office publishes a different pair.

3. Home office
Remote employees must have a private workspace, a locked screen, and a reliable internet connection of at least 50 Mbps download. Northline provides a one-time 300 USD home-office stipend after probation. Recurring home internet bills are not reimbursed.

4. Availability
Remote employees follow the same core hours of 10:00 to 16:00. Calendar status must reflect meetings and focus time. Video is expected for interviews and customer calls.

5. Office visits
Fully remote employees travel to a Northline office at least twice per year for planning weeks. Those trips follow the Travel Policy, including manager approval for domestic travel.
"""

OFFICE_LOCATIONS = """NORTHLINE SYSTEMS
Office Locations Directory
Effective date: 1 January 2026
Owner: Workplace Services

Austin Hub
Address: 4400 Barton Skyway, Suite 800, Austin, TX 78746
Capacity: 120 seats
Hours: 08:00-19:00 local time on weekdays
Badge desk: Floor 8 reception

Manchester Studio
Address: 12 Quay Street, Manchester, M3 3JE, United Kingdom
Capacity: 40 seats
Hours: 08:30-18:30 local time on weekdays
Note: Visitor Wi-Fi is disabled. Guests receive a time-limited wired guest port after sign-in.

Bengaluru Delivery Center
Address: Manyata Tech Park, Block C3, Level 4, Bengaluru 560045, India
Capacity: 200 seats
Hours: 08:00-20:00 local time on weekdays
Secure print: Follow-me printing with badge release only

There is no Northline office in Antarctica. Do not invent additional sites.
"""


def _write_wrapped_pdf(path: Path, text: str) -> None:
    """Write a PDF by flowing the full text with a simple line wrapper."""
    doc = fitz.open()
    width, height = 595, 842
    margin = 72
    max_width = width - 2 * margin
    fontsize = 11
    line_height = 14
    font = fitz.Font(fontname="helv")

    lines: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            lines.append("")
            continue
        words = raw_line.split(" ")
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if font.text_length(trial, fontsize=fontsize) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

    y = None
    page = None

    def new_page() -> None:
        nonlocal page, y
        page = doc.new_page(width=width, height=height)
        y = margin

    new_page()
    for line in lines:
        if y > height - margin:
            new_page()
        page.insert_text((margin, y), line, fontsize=fontsize, fontname="helv")
        y += line_height
    doc.save(path)
    doc.close()


def _write_docx(path: Path, title: str, body: str) -> None:
    document = Document()
    heading = document.add_heading(title, level=0)
    for run in heading.runs:
        run.font.size = Pt(18)
    for para in body.strip().split("\n\n"):
        p = document.add_paragraph(para.strip())
        p.paragraph_format.space_after = Pt(8)
    document.save(path)


def generate_all(output_dir: Path | None = None) -> list[Path]:
    output_dir = output_dir or SAMPLE_DOCUMENTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    pdfs = {
        "Employee_Handbook.pdf": EMPLOYEE_HANDBOOK,
        "Leave_Policy.pdf": LEAVE_POLICY,
        "Travel_Policy.pdf": TRAVEL_POLICY,
        "IT_Security_Policy.pdf": IT_SECURITY_POLICY,
    }
    for name, text in pdfs.items():
        path = output_dir / name
        _write_wrapped_pdf(path, text)
        written.append(path)

    docx_path = output_dir / "Remote_Work_Policy.docx"
    _write_docx(docx_path, "Northline Remote Work Policy", REMOTE_WORK)
    written.append(docx_path)

    txt_path = output_dir / "Office_Locations.txt"
    txt_path.write_text(OFFICE_LOCATIONS, encoding="utf-8")
    written.append(txt_path)
    return written


if __name__ == "__main__":
    paths = generate_all()
    print(f"Wrote {len(paths)} sample documents to {SAMPLE_DOCUMENTS_DIR}")
    for p in paths:
        print(f" - {p.name}")
