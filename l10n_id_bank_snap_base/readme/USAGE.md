Statements are pulled by the scheduled action of *Online Bank Statements*
or with *Pull Online Bank Statement* on the provider. Pulling the same
period again never duplicates lines: SNAP has no transaction id, so each
line gets an import id built from account, date, type, amount and remark,
with a counter for identical transactions.

Common SNAP response codes (HTTP status + 2-digit service + 2-digit case):

- `401xx00` / `4017300` *Unauthorized (Unknown client / Signature)*: the
  Client ID does not belong to this environment, the private key is not the
  one registered for the application, or the Client Secret / Partner ID is
  wrong.
- `401xx01` *Invalid token*: the token is refreshed and the call retried
  once automatically.
- `403xx01` *Feature not allowed*: the service is not enabled for the
  application or corporate at the bank.
- `409xx00` *Conflict*: duplicate `X-EXTERNAL-ID`.
- `429xx00` *Too many requests / more than 20000 rows*: use daily statements.
- `5xxxx0x`: bank-side error, retry later.
