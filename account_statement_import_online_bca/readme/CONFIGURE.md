1. Register an application on the BCA developer portal
   (<https://developer.bca.co.id>). BCA gives a Client ID, Client Secret, an
   RSA key pair and an API Key / API Secret. The **API Key / API Secret belong
   to the older non-SNAP API and are not used** by this module.
2. On the BCA bank journal, set the bank account (sandbox: `1234567890`)
   and create the online provider with service *BCA (SNAP BI)* and *daily*
   statements. In its **SNAP** tab:
   - paste the private key given by BCA;
   - Partner ID (`X-PARTNER-ID`) is the **KlikBCA Bisnis Corporate ID**: the
     first part of the KlikBCA Bisnis username (*CorporateID* + *UserID*). In
     the sandbox use `KBBABCINDO` (the documentation examples show
     `KBCABCINDO`, which the sandbox rejects with *Unknown client*);
   - Channel ID is `95051` (KlikBCA Bisnis WSID);
   - for production, fill in the Base URL given by BCA.
3. Click *Test Token*, then *Test Connection*. In the sandbox the
   `partnerReferenceNo` is BCA's sample value automatically.
