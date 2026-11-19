BCA only serves the last 31 days of transactions. A scheduled pull that
reaches further back skips the older days, posts a message with the skipped
range on the provider and continues; a manual pull of such a period is
refused. Import older periods from a statement file.

The 36-character BCA remark (2 x 18 characters) is shown as
`remark 1 / remark 2`; the raw bank data stays on the statement line.
Reconcile the imported lines as usual, for example with
`account_reconcile_oca`.
