# Power BI Report Specification — EFTA AI Use Case Registry

## Data source
Dataverse table: `efta_aiusecases`
Refresh: Daily at 06:00 CET

## Pages

### Page 1 — Executive Summary
Audience: Senior management

| Visual | Type | Fields | Notes |
|---|---|---|---|
| Total cases submitted | Card | COUNT(CaseId) | All statuses |
| Cases published | Card | COUNT where Status = Published | |
| Cases this quarter | Card | COUNT where SubmissionDate >= quarter start | |
| Cases by domain | Donut chart | Domain, COUNT | |
| Cases by tool | Bar chart | ToolUsed, COUNT | |
| Submissions over time | Line chart | SubmissionDate (month), COUNT | |
| Latest 5 published | Table | CaseId, Title, Domain, ToolUsed, Date | Linked to record |

### Page 2 — Case Detail Table
Audience: Management / internal reviewers

| Column | Field |
|---|---|
| Case ID | efta_caseid |
| Title | efta_title |
| Domain | efta_domain |
| Tool | efta_toolused |
| Status | efta_status |
| Submitted by | efta_submittedby |
| Date | efta_submissiondate |
| Visibility | efta_visibility |

Filters: Domain, Tool, Status, Date range, Submitted by

### Page 3 — Learning Digest
Audience: All staff, Member States

A text-heavy page showing key learnings grouped by domain.
Visual type: Table or multi-row card with wrapping text.

Fields shown: Domain · Tool · Key Learning · Outcome (brief)

---

## Sharing
- Executive Summary page: shared as a public embed (no login required)
- Case Detail page: shared only with authenticated M365 users
- Learning Digest page: shared as a public embed

## Row-level security
Not required — visibility filtering is enforced at Dataverse level before Power BI loads data.
Only `Status = Published` AND `Visibility IN (Management, Public)` records are included in the dataset for management view.
Only `Status = Published` AND `Visibility = Public` records are included in the public dataset.

## Measures (DAX)

```dax
Total Cases = COUNTROWS(efta_aiusecases)

Published Cases = CALCULATE(COUNTROWS(efta_aiusecases), efta_aiusecases[efta_status] = "Published")

Cases This Quarter = 
CALCULATE(
    COUNTROWS(efta_aiusecases),
    DATESQTD(efta_aiusecases[efta_submissiondate])
)

Approval Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(efta_aiusecases), efta_aiusecases[efta_status] IN {"Approved","Published"}),
    COUNTROWS(efta_aiusecases),
    0
) * 100
```
