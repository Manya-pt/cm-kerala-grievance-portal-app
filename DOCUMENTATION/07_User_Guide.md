# 07 – User Guide

> Prototype with fictional data. Test accounts (from `supabase/demo_accounts.sql`) use the password `Demo@1234`.

## Public visitors (no login)
- **Home:** introduction, live sample statistics, featured departments, and **Submit Grievance** / **Track Grievance** buttons.
- **About Us / How It Works / FAQ:** what the portal is for and how a grievance moves through the system.
- **Departments:** sample departments that handle grievances.
- **Contact Us:** send a general enquiry (name, email, subject, message).
- **Track:** enter the reference number shown after submission (format `CMK-<year>-<6 digits>`) to see the status, assigned department and public history.

## Citizens
1. **Register:** click *Login → Create an account*, enter name, email, 10-digit mobile (starting with 6–9) and a password (8+ characters, letters and numbers). Or use `citizen@demo.com`.
2. **Submit a grievance:** *Dashboard → + Submit new grievance*.
   - Choose district and category, write a subject and a detailed description.
   - Click **Analyse with AI**. The assistant suggests a category, department and priority, writes a summary, and warns if a similar complaint already exists. Click **Apply category & priority** only if you agree.
   - Optionally attach a photo or PDF (max 5 MB), then click **Submit grievance**.
   - Note the **reference number** shown on your dashboard.
3. **Dashboard:** total, pending, resolved and reopened counts, and the list of your grievances. Click any grievance to open it.
4. **Updates:** the grievance page shows remarks from the CMO and the department, plus the full status history.
5. **After resolution:** rate the resolution (1–5 stars) with an optional comment. If the problem isn't fixed, write the reason and click **Reopen grievance**.

## CMO administrator (`cmo@demo.com`)
1. **Dashboard:** cards for total, pending, resolved, overdue and reports to review (click a card to filter). Charts show status, district-wise and department-wise numbers, and the monthly trend. Below is a department summary table.
2. **Find grievances:** filter by district, category, priority, status or department, tick *Overdue only*, or search by subject/reference.
3. **Open a grievance:** read the complaint, open attachments, see citizen contact details and the **AI analysis** (summary, suggestions, duplicate warning). Click **Re-run AI** to refresh it.
4. **Review:** click **Mark as Under Review**.
5. **Forward:** choose the department (pre-selected from the AI suggestion) and officer, add instructions and click **Forward**.
6. **Priority/category:** change them, or click **Use AI suggestion**, then **Save**.
7. **Remarks:** add a remark. Keep *Internal* ticked for notes the citizen should not see.
8. **Escalate:** for delayed grievances, click **Escalate delayed grievance** (sets High priority and flags it).
9. **Review action-taken reports:** when an officer submits a report, a highlighted box appears. Write a remark and click **Accept & resolve** or **Return**.
10. **Resolve directly:** write a resolution remark and click **Mark resolved directly**.
11. **Contact enquiries:** dashboard → *Contact enquiries*.
12. **Officers:** dashboard → *Officers* to create a department officer account (department, name, email, mobile, initial password) and see existing officers.

## Department officers (test accounts `officer.<code>@demo.com`, e.g. `officer.kwa@demo.com`, or accounts created by the CMO)
1. **Dashboard:** grievances forwarded to your department only, with counts. Tabs: Active, Resolved, All.
2. **Open a grievance:** read the details and open attachments.
3. **Start investigation:** write remarks and click **Start (set In Progress)**. Further remarks are posted as progress updates and are visible to the CMO and citizen.
4. **Action-taken report:** describe the action, optionally attach a file, and click **Submit report to CMO**. The CMO then accepts or returns it. If it's returned, the CMO's remark is shown and you can submit a new report.
5. **Internal note:** send a note visible only to CMO staff.

## Status meanings
| Status | Meaning |
|---|---|
| Submitted | Received, waiting for CMO review |
| Under Review | CMO reviewing / forwarded to a department |
| In Progress | Department acting on it (report may be awaiting review) |
| Resolved | Action verified by the CMO |
| Reopened | Citizen says it isn't fixed; back with the CMO |

**Overdue** = not resolved within 3 (High), 7 (Medium) or 14 (Low) days.
