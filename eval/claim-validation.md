# F004 — Representative Claim Validation Review

## Method

- Ran five factual queries from `eval/eval.jsonl` (records 7, 9, 11, 14 and 19) through the existing persisted index in hybrid mode with 20 candidates/top 5; no ingestion or index rebuild occurred.
- Generated each answer and its separate GPT-4.1-mini claim check using only retrieved passages. Manually compared the claims below with the cited page in the indexed source PDF.
- Claim status is an automated aid, not a correctness guarantee. This small review is not an exhaustive entailment evaluation.

## Claim checks

| Query / claim | Automated status | Cited source and page evidence manually reviewed | Manual result |
|---|---|---|---|
| Gayatri Projects restart date: “Trading in the equity shares of Gayatri Projects Limited will resume with effect from April 09, 2026.” | **Supported** | `0001fd562caa1c25`, p. 1, *Revocation of Trading Suspension in Equity Shares of Gayatri Projects Limited*: “suspension ... will be revoked w.e.f. April 09, 2026”; the circular also says it is effective from April 09, 2026. | Correct status; the cited page directly confirms the date. |
| Whitebox provider: “M/s. Stockwiz Technologies LLP was empanelled provisionally for whitebox and blackbox algo solutions” (validator also included the March 2, 2026 circular date). | **Supported** | `075fa795bfc794af`, p. 1, *Algo Provider - Provisional Empanelment for Providing Algorithmic Trading Solutions*: names M/s Stockwiz Technologies LLP and lists “Whitebox and Blackbox”; page says the provider was empanelled on a provisional basis. | Correct status; name, provisional status and algo types appear on the cited page. |
| Hercules name change: “The effective date for the Hercules name change from Hercules Hoists Limited to Hercules Investments Limited is November 24, 2025.” | **Supported** | `00b388f1536c50c4`, p. 1, *Change in name of Hercules Hoists Limited to Hercules Investments Limited*: identifies both names and states the change is effective November 24, 2025. | Correct status; the cited page directly confirms the names and date. |
| Current Infraprojects transfer: “The effective date for Current Infraprojects Limited moving from trade-for-trade segment to the rolling segment is September 17, 2025.” | **Supported** | `0006ec6de19b9b41`, p. 1, *Trade for Trade - Current Infraprojects Limited (SME IPO)*: says the security will transfer from trade-for-trade to rolling segment effective September 17, 2025. | Correct status; the cited page directly confirms the segment change and date. |
| November 21, 2026 SLBM session: “Trades during the November 21, 2026 SLBM mock session do not create any fund pay-in or pay-out obligations.” | **Needs review** | The validator mapped this claim to `cbe480f0ca976c14`, p. 3, *Mock Trading Session in SLBM on Saturday, June 06, 2026 - No New Version Release*. That page says mock-session trades have no fund pay-in or pay-out, but it concerns the June 6 session, not November 21. | Correct conservative status. The cited passage is consistent with the claim but does not establish the named November session; no false positive observed. |

The same November query produced a second claim that other 2025/2026 SLBM mock-session notices consistently state there are no fund pay-in/pay-out obligations. The validator marked that **Supported** using the listed prior-session citations. This does not upgrade the first, date-specific November 21 claim: its only mapped evidence above is from a June session. The example shows why claim-level source mapping and a **Needs review** status matter.

## Observed errors

- No obvious false positive or false negative was found in the five manually reviewed factual claims. The November 21 example was appropriately left at **Needs review** because its mapped page did not identify that session.
- The answer may cite general language shared by multiple dated mock sessions. The CLI displays each available circular ID, title, publication date and actual page to expose that context; it does not infer that one notice supersedes another.
