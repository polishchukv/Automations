# Findings Outreach Console — design notes

Companion to `campaign-console-v4.html` (open in any browser, no server needed).

## The flow

Pull → Team pool → Configure → Campaigns. Four stages, shown in the topbar.

1. **Pull** — an API query returns teams matching severity/exposure criteria. Every pull is an immutable snapshot with an ID and timestamp. Historical pulls are selectable and behave identically to the latest.
2. **Team pool** — one row per team from the selected pull: severity spine, exposure split, and current campaign status inline. Campaign state is layered onto the pool so you never leave the list to check who is already in flight.
3. **Configure** — staged teams get a per-team card. Scope is inherited from the pull and editable per team before locking.
4. **Campaigns** — the running ledger for each team.

## The campaign object

One campaign per team. It starts with a baseline notice and stays open across many follow-up cycles until manually marked complete, then archives. A team can only have one running campaign at a time; archiving frees it to start another.

- **Scope is fixed for the life of the campaign.** Changing it means completing and restarting. Otherwise "14 of 30 closed" stops meaning anything.
- **Follow-ups live inside the campaign** and absorb new findings that fall in scope.
- Each cycle stores its own reconciliation counts, so the history of what changed when is preserved.

## Finding statuses

Status lives on the finding within a campaign, not on the email:

| Status | Meaning |
|---|---|
| New in scope | Appeared since last cycle, matches campaign scope |
| Still active | Present in both cycles, unresolved |
| Confirmed remediated | Verified closed |
| Assumed remediated | Gone from scan results, not verified |
| Out of scope | No longer matches scope (re-scored, reassigned) |

Remediated and out-of-scope rows stay in the attachment so teams can see what has been credited to them. This kills most of the reply-thread arguing.

## Generated vs sent

Locking runs the detailed pull and generates one email + one attachment per team. **Nothing sends automatically.** Artifacts sit in a "Ready to send" state until manually marked sent. The topbar carries a ready-to-send counter so generated-but-unsent work cannot hide.

Both artifacts are openable from the UI — the email with headers and send status, the attachment as the actual finding rows with a status filter.

## Storage

Findings stay in CSV — that is scanner output, re-pulled and overwritten. Campaign state goes in SQLite, because it is ours and has to survive.

    pulls              id, run_at, criteria
    campaigns          id, team, source_pull, scope, started_at, status, archived_at
    outreach           id, campaign_id, cycle, kind, generated_at, sent_at, artifact_paths
    campaign_findings  campaign_id, finding_id, status, first_cycle, resolved_cycle

`campaign_findings` is the whole system. `sent_at` staying nullable is what makes manual sending work — one query against it returns everything generated but not out the door.

## Open dependency: finding identity

Reconciliation depends on recognizing that a finding in today's CSV is the same one emailed three weeks ago. Composite IDs are already generated from finding metadata upstream.

Worth validating: any field in the hash that can change while the finding stays the same produces a false remediate + false new-in-scope pair in one cycle. Severity is the usual culprit — it belongs in the scope filter, not in identity. Diagnostic: on two consecutive historical pulls, count IDs that disappear while a new ID appears on the same asset with the same vuln title. Should be near zero. Worth keeping as a permanent health metric.

## Not yet decided

- Whether follow-up cadence is per-campaign or global
- Whether assumed-remediated auto-promotes to confirmed after N clean cycles
- Escalation path when a campaign passes SLA repeatedly (currently just a status)
