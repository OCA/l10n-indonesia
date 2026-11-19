Everything is set on the online bank statement provider of the bank journal
(*Accounting > Configuration > Banks > Online Bank Statement Providers*, or
the *Configuration* button of the journal), tab **SNAP** (Accounting Manager
only):

1. On the bank journal, set the bank account (its number is the `accountNo`
   sent to the bank) and *Bank Feeds* = *Online*; choose the bank service on
   the provider, preferably with *daily* statements.
2. Choose the environment (sandbox or production). The Base URL and Channel
   ID are filled in from the bank module; the production Base URL must be
   typed in when the bank does not publish it.
3. Fill in the Client ID, Client Secret and Partner ID (`X-PARTNER-ID`) given
   by the bank.
4. RSA keys:
   - if the bank gives you a key pair, paste or upload the **private key**
     (PEM, also accepted on one line); the public key is derived and shown;
   - otherwise click *Generate Key Pair* and send the public key (*Download
     Public Key*) to the bank.
5. Click *Test Token*, then *Test Connection* (balance inquiry).

**Several accounts, one bank application.** Each bank account has its own
journal and provider; the providers of one bank application hold the same
Client ID, Client Secret and private key. The bank keeps one secret and one
public key per application, so after regenerating the key pair or the secret,
update **every** provider using that Client ID. Odoo warns about the other
providers when you change the secret or the private key.

Secrets (Client Secret, private key, access token) are readable by
Accounting Managers only (the token by system administrators only) and are
never written to logs or messages.
