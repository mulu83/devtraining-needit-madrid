# IT Setup Guide — EFTA AI Use Case Registry

## Prerequisites checklist

Before starting, confirm the following with your Power Platform admin:

- [ ] Power Platform environment exists (e.g. `efta-prod`)
- [ ] Copilot Studio licences are assigned to the bot owner account
- [ ] Dataverse is enabled for the environment
- [ ] Power Pages is enabled for the environment
- [ ] The IT admin has **System Administrator** role in the environment

---

## Step 1 — Create the Dataverse table (30 min)

1. Go to [make.powerapps.com](https://make.powerapps.com) → select your environment
2. Left nav → **Tables** → **+ New table** → **Add columns and data**
3. Table settings:
   - Display name: `AI Use Case`
   - Plural name: `AI Use Cases`
   - Schema name: `efta_aiusecase`
4. Add each column from `dataverse/schema.json` in this repo
5. For **Choice** columns, create the option sets before adding the column
6. Save the table

**Verify:** The table appears in Tables list and you can create a test row manually.

---

## Step 2 — Create the Power Automate flows (45 min)

### Flow 1: Submit Use Case

1. Go to [make.powerautomate.com](https://make.powerautomate.com)
2. **+ Create** → **Automated cloud flow**
3. Trigger: **When a Power Apps or Copilot Studio calls a flow**
4. Add steps following `power-automate/submit-use-case-flow.json`
5. In the Teams notification step, paste your approver channel ID:
   - Find it in Teams → right-click channel → Get link → extract the `channel=` value
6. Replace `{{APPROVER_TEAMS_CHANNEL_ID}}` and `{{ENV_ID}}` with real values
7. Save and **turn on** the flow
8. Copy the flow's HTTP trigger URL — you'll need it in Step 3

### Flow 2: Approval notification

1. **+ Create** → **Automated cloud flow**
2. Trigger: **When a row is added, modified, or deleted** → Microsoft Dataverse
   - Table: `AI Use Cases`
   - Change type: `Modified`
   - Filter columns: `efta_status`
3. Add steps following `power-automate/approval-flow.json`
4. Save and **turn on**

---

## Step 3 — Set up Copilot Studio (60 min)

1. Go to [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. **+ New copilot** → name it `EFTA AI Use Case Registry`
3. In **Topics** → **+ New topic** → switch to YAML editor
4. Paste contents of `copilot-studio/submission-topic.yaml`
5. In the **Submit to Dataverse** action node, connect it to Flow 1 from Step 2
6. Test in the built-in test chat panel — walk through a full submission
7. **Publish** the copilot

### Add to Microsoft Teams

1. In Copilot Studio → **Channels** → **Microsoft Teams**
2. Follow prompts to submit to your Teams app catalogue
3. Your Teams admin approves it — it then appears in the Teams app store for all staff

---

## Step 4 — Set up Power Pages (45 min)

1. Go to [make.powerpages.microsoft.com](https://make.powerpages.microsoft.com)
2. **+ New site** → blank template → name it `EFTA AI Registry`
3. In **Pages** → create a page called `Use Cases`
4. Use the **Code editor** to paste `power-pages/public-portal.html`
5. In **Data** → add a table permission:
   - Table: `AI Use Cases`
   - Access type: **Global** (read-only)
   - Privilege: **Read**
   - Filter: `efta_status eq 'Published' and efta_visibility eq 'Public'`
6. **Sync** and **Preview** — confirm cards render correctly
7. **Publish** the site

---

## Step 5 — Set up Power BI (30 min)

1. Open Power BI Desktop
2. **Get data** → **Dataverse** → connect to your environment
3. Select table `efta_aiusecases`
4. Apply filter: `efta_status = Published`
5. Build visuals per `power-bi/report-spec.md`
6. Add the DAX measures from the spec
7. **Publish** to Power BI service → your workspace
8. Share the Executive Summary page as a public embed link (Settings → Embed)

---

## Step 6 — Handover testing (with business owner)

Walk through these scenarios before go-live:

- [ ] Staff submits a case via Teams bot — record appears in Dataverse as Draft
- [ ] Approver receives Teams notification with link
- [ ] Approver opens model-driven app, changes Status to Approved + visibility Public
- [ ] Submitter receives approval notification in Teams
- [ ] Case appears on public Power Pages portal
- [ ] Power BI dashboard shows updated count

---

## Environment variables to configure

| Variable | Where to set | Example |
|---|---|---|
| `APPROVER_TEAMS_CHANNEL_ID` | Flow 1 step | `19:abc123@thread.tacv2` |
| `ENV_ID` | Flow 1 approval link | `12345678-1234-...` |
| Dataverse environment URL | Power Pages data connection | `https://efta.crm4.dynamics.com` |

---

## Ongoing maintenance

| Task | Frequency | Owner |
|---|---|---|
| Review and approve new cases | As submitted (target: 5 working days) | Nominated approver |
| Add new domain / tool choices | As needed | Power Platform admin |
| Refresh Power BI dataset | Automatic daily | Power BI service |
| Review public portal appearance | Quarterly | Communications team |
