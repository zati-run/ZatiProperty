# Protected draft creation: browser save

Environment and Loom/action-form versions match receipt 022.
A scoped manager navigated Portfolio -> synthetic property 4 -> unit 4 and
created a separate synthetic draft through the generated protected form.

The sole submission used request 74222cae-c207-4dc7-84e4-7129e3056bf4.
HTTP 200 returned verified, tenancy 6, code ZP-UI-DRAFT-20261010-R1,
property 4, lifecycle draft, version 0, dates 2042-01-01 through the
exclusive end 2043-01-01. The UI displayed Saved and checked.

The user entered USD 1500 rent and 3000 deposit. The actual submitted
proposal contained integer minor amounts 150000 and 300000, fixed USD
currency, complete matching term/party dates, and scoped tenant account 6.
The account chooser offered only the manager's permitted synthetic account.
No generic tenancy CRUD grant was introduced.

A private exclusive intent and response retain the exact command and prevent
blind replay. One earlier browser selector lookup timed out before the intent
or submit; correcting the label then produced the sole business submission.

Fresh reload, role isolation and domain audit acceptance remain separately
tracked. The surrounding tenancy table did not auto-refresh after save;
explicit success feedback asks for refresh. Duplicate optional labels and
raw enum punctuation remain visible usability work, not accepted polish.
