# Copyright 2026 PT Solusi Aglis Indonesia. (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import hashlib
import hmac
import json
import logging
import re
import secrets
import textwrap
import time
from collections import Counter
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pytz
import requests

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
except ImportError:  # pragma: no cover
    _logger.debug("cryptography is not installed")

SNAP_TZ = pytz.timezone("Asia/Jakarta")
SNAP_TIMEOUT = 60
TOKEN_MARGIN = timedelta(seconds=60)
# SNAP spells the direction out (CREDIT/DEBIT) or with ISO 20022 codes.
SNAP_DEBIT = {"DEBIT", "DBIT", "DB", "D"}
SNAP_CREDIT = {"CREDIT", "CRDT", "CR", "C"}


class OnlineBankStatementProvider(models.Model):
    """SNAP BI connection data, kept on the provider like other OCA services.

    Several accounts of one bank application mean several providers holding
    the same credentials (see readme).
    """

    _inherit = "online.bank.statement.provider"

    snap_is_snap = fields.Boolean(compute="_compute_snap_is_snap")
    snap_environment = fields.Selection(
        [("sandbox", "Sandbox"), ("production", "Production")],
        string="SNAP Environment",
        default="sandbox",
    )
    snap_base_url = fields.Char(
        string="SNAP Base URL",
        compute="_compute_snap_base_url",
        store=True,
        readonly=False,
        help="Scheme and host of the bank SNAP API, without trailing slash.",
    )
    snap_client_key = fields.Char(string="Client ID", copy=False)
    snap_client_secret = fields.Char(
        string="Client Secret", copy=False, groups="account.group_account_manager"
    )
    snap_partner_id = fields.Char(
        string="Partner ID",
        help="Value of the X-PARTNER-ID header (for BCA: KlikBCA Bisnis "
        "Corporate ID).",
    )
    snap_channel_id = fields.Char(string="Channel ID")
    snap_private_key = fields.Text(
        string="Private Key (PEM)", copy=False, groups="account.group_account_manager"
    )
    snap_private_key_file = fields.Binary(
        string="Upload Private Key",
        compute="_compute_snap_private_key_file",
        inverse="_inverse_snap_private_key_file",
        groups="account.group_account_manager",
    )
    snap_public_key = fields.Text(
        string="Public Key (PEM)",
        compute="_compute_snap_public_key",
        compute_sudo=True,
        store=True,
        copy=False,
    )
    snap_public_key_file = fields.Binary(
        string="Public Key File", compute="_compute_snap_public_key_file"
    )
    snap_access_token = fields.Char(copy=False, groups="base.group_system")
    snap_token_expiry = fields.Datetime(
        string="Token Valid Until", copy=False, groups="base.group_system"
    )

    @api.model
    def _snap_bank_config(self):
        """Per-bank constants, extended by bank modules.

        A bank module only has to add its entry here:

        - ``label``: service name shown on the provider (registers the service)
        - ``sandbox_url`` / ``production_url``: scheme and host (False: typed in)
        - ``channel_id``: default CHANNEL-ID header
        - ``token_path``, ``statement_path``, ``balance_path``: SNAP endpoints
        - ``history_days`` (optional): how far back the bank serves statements
        - ``remark_split`` (optional): fixed width of the bank's remark parts
        - ``sandbox_partner_reference_no`` (optional): value the sandbox requires

        :return: {service: {key: value}}
        """
        return {}

    @api.model
    def _get_available_services(self):
        services = super()._get_available_services()
        known = {code for code, _label in services}
        return services + [
            (code, config["label"])
            for code, config in self._snap_bank_config().items()
            if config.get("label") and code not in known
        ]

    def _obtain_statement_data(self, date_since, date_until):
        self.ensure_one()
        if not self._snap_config():
            return super()._obtain_statement_data(date_since, date_until)
        start = self._snap_apply_history_window(date_since, date_until)
        if start is None:
            return [], {}
        return self._snap_obtain_statement_data(start, date_until)

    def _snap_history_cutoff(self):
        """Oldest moment (naive UTC) the bank serves: Jakarta midnight - N days."""
        self.ensure_one()
        days = self._snap_config().get("history_days")
        if not days:
            return None
        today = datetime.now(SNAP_TZ).date()
        local = SNAP_TZ.localize(
            datetime.combine(today - timedelta(days=days), datetime.min.time())
        )
        return local.astimezone(pytz.utc).replace(tzinfo=None)

    def _snap_apply_history_window(self, date_since, date_until):
        """Clamp the period to the bank's history window.

        Never drops days silently: scheduled runs log the skipped range in the
        chatter and go on, manual pulls raise.
        """
        self.ensure_one()
        cutoff = self._snap_history_cutoff()
        if cutoff is None or date_since >= cutoff:
            return date_since
        skipped_until = min(cutoff, date_until)
        config = self._snap_config()
        message = self.env._(
            "Transactions from %(since)s to %(until)s are outside the %(days)s-day "
            "window of the %(bank)s statement API and were not pulled; import "
            "this period from a statement file.",
            since=self._utc_to_provider_tz(date_since).date(),
            until=self._utc_to_provider_tz(skipped_until - timedelta(seconds=1)).date(),
            days=config["history_days"],
            bank=config.get("label") or self.service,
        )
        if not self.env.context.get("scheduled"):
            raise UserError(message)
        self.message_post(body=message)
        if date_until <= cutoff:
            return None
        return cutoff

    def _snap_config(self):
        self.ensure_one()
        return self._snap_bank_config().get(self.service) or {}

    @api.depends("service")
    def _compute_snap_is_snap(self):
        config = self._snap_bank_config()
        for rec in self:
            rec.snap_is_snap = rec.service in config

    @api.depends("service", "snap_environment")
    def _compute_snap_base_url(self):
        for rec in self:
            config = rec._snap_config()
            if config:
                # Switching environment must never keep the other one's URL.
                rec.snap_base_url = config.get(f"{rec.snap_environment}_url") or False
            elif not rec.snap_base_url:
                rec.snap_base_url = False

    @api.onchange("service")
    def _onchange_snap_service(self):
        channel = self._snap_config().get("channel_id")
        if channel:
            self.snap_channel_id = channel

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("snap_private_key"):
                vals["snap_private_key"] = self._snap_normalize_pem(
                    vals["snap_private_key"]
                )
            if vals.get("service") and not vals.get("snap_channel_id"):
                config = self._snap_bank_config().get(vals["service"]) or {}
                if config.get("channel_id"):
                    vals["snap_channel_id"] = config["channel_id"]
        return super().create(vals_list)

    _snap_token_fields = (
        "snap_environment",
        "snap_base_url",
        "snap_client_key",
        "snap_client_secret",
        "snap_private_key",
        "snap_partner_id",
        "snap_channel_id",
        "service",
    )

    def write(self, vals):
        if vals.get("snap_private_key"):
            vals = dict(
                vals,
                snap_private_key=self._snap_normalize_pem(vals["snap_private_key"]),
            )
        if any(field in vals for field in self._snap_token_fields):
            vals = dict(vals, snap_access_token=False, snap_token_expiry=False)
        return super().write(vals)

    # Keys ---------------------------------------------------------------

    @api.model
    def _snap_normalize_pem(self, text):
        """Rebuild a PEM key pasted on one line or without its markers."""
        text = (text or "").strip()
        match = re.search(r"-----BEGIN ([A-Z ]+)-----", text)
        label = match.group(1) if match else "PRIVATE KEY"
        body = re.sub(r"-----(BEGIN|END) [A-Z ]+-----", "", text)
        body = re.sub(r"\s+", "", body)
        if not body or not re.fullmatch(r"[A-Za-z0-9+/=]+", body):
            return text
        lines = "\n".join(textwrap.wrap(body, 64))
        return f"-----BEGIN {label}-----\n{lines}\n-----END {label}-----\n"

    @api.model
    def _snap_parse_private_key(self, pem):
        pem = self._snap_normalize_pem(pem)
        try:
            key = serialization.load_pem_private_key(pem.encode(), password=None)
        except (ValueError, TypeError) as exc:
            raise ValidationError(
                self.env._("The private key is not a readable unencrypted PEM key.")
            ) from exc
        if not isinstance(key, rsa.RSAPrivateKey):
            raise ValidationError(self.env._("The private key must be an RSA key."))
        return key

    def _snap_load_private_key(self):
        self.ensure_one()
        if not self.snap_private_key:
            raise UserError(
                self.env._("Provider %(name)s has no SNAP private key.", name=self.name)
            )
        try:
            return self._snap_parse_private_key(self.snap_private_key)
        except ValidationError as exc:
            raise UserError(exc.args[0]) from exc

    @api.model
    def _snap_public_pem(self, private_key):
        return (
            private_key.public_key()
            .public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode()
        )

    @api.depends("snap_private_key")
    def _compute_snap_public_key(self):
        for rec in self:
            try:
                key = rec._snap_parse_private_key(rec.snap_private_key)
            except ValidationError:
                key = None
            rec.snap_public_key = (
                self._snap_public_pem(key) if rec.snap_private_key and key else False
            )

    @api.constrains("snap_private_key")
    def _check_snap_private_key(self):
        for rec in self.filtered("snap_private_key"):
            rec._snap_parse_private_key(rec.snap_private_key)

    def _compute_snap_private_key_file(self):
        self.snap_private_key_file = False

    def _inverse_snap_private_key_file(self):
        for rec in self.filtered("snap_private_key_file"):
            rec.snap_private_key = base64.b64decode(rec.snap_private_key_file).decode()

    @api.depends("snap_public_key")
    def _compute_snap_public_key_file(self):
        for rec in self:
            rec.snap_public_key_file = (
                base64.b64encode(rec.snap_public_key.encode())
                if rec.snap_public_key
                else False
            )

    def action_generate_key_pair(self):
        self.ensure_one()
        if self.snap_private_key and not self.env.context.get(
            "snap_confirm_regenerate"
        ):
            raise UserError(
                self.env._(
                    "This provider already has a key pair. Use 'Regenerate Key "
                    "Pair' to replace it; the bank must then receive the new "
                    "public key."
                )
            )
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.snap_private_key = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        self.message_post(body=self.env._("A new RSA key pair was generated."))
        return True

    def action_snap_test_token(self):
        """Request a fresh B2B token and report the result (never the token)."""
        self.ensure_one()
        cred = self.sudo()
        try:
            cred._snap_check_ready()
            cred._snap_get_token(force=True)
        except UserError as exc:
            return self._snap_notification(exc.args[0], "danger")
        message = self.env._(
            "Access token obtained (2007300), valid until %(expiry)s UTC.",
            expiry=cred.snap_token_expiry,
        )
        self.message_post(body=message)
        return self._snap_notification(message, "success")

    @api.model
    def _snap_notification(self, message, kind):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("SNAP connection"),
                "message": message,
                "type": kind,
                "sticky": kind == "danger",
            },
        }

    @api.onchange("snap_client_secret", "snap_private_key")
    def _onchange_snap_shared_credentials(self):
        """Warn when other providers use the same bank application."""
        if not self.snap_client_key:
            return {}
        others = (
            self.sudo()
            .search(
                [
                    ("snap_client_key", "=", self.snap_client_key),
                    ("id", "!=", self._origin.id),
                ]
            )
            .filtered("snap_is_snap")
        )
        if not others:
            return {}
        return {
            "warning": {
                "title": self.env._("Shared SNAP application"),
                "message": self.env._(
                    "These providers use the same Client ID: %(names)s. The "
                    "bank keeps one secret and one public key per application: "
                    "update them as well.",
                    names=", ".join(others.mapped("name")),
                ),
            }
        }

    def action_download_public_key(self):
        self.ensure_one()
        if not self.snap_public_key:
            raise UserError(self.env._("There is no public key yet."))
        filename = f"{(self.name or 'snap').replace(' ', '_')}_public.pem"
        return {
            "type": "ir.actions.act_url",
            "url": (
                f"/web/content?model={self._name}&id={self.id}"
                f"&field=snap_public_key_file&filename={filename}&download=true"
            ),
            "target": "self",
        }

    tz = fields.Selection(default="Asia/Jakarta")
    # Statement data ---------------------------------------------------------

    def _snap_check_ready(self):
        """Return the provider as sudo (it reads secrets) once configured."""
        self.ensure_one()
        if not self.snap_client_key:
            raise UserError(
                self.env._(
                    "Online bank statement provider %(name)s has no SNAP " "Client ID.",
                    name=self.name,
                )
            )
        if not self.account_number:
            raise UserError(
                self.env._(
                    "Online bank statement provider %(name)s has no account " "number.",
                    name=self.name,
                )
            )
        return self.sudo()

    @api.model
    def _snap_format_date(self, day):
        return f"{day.isoformat()}T00:00:00+07:00"

    def _snap_request_date_range(self, date_since, date_until):
        """Bank dates (Jakarta) covering the naive-UTC period [since, until).

        toDateTime is the next Jakarta midnight, so the window is never empty
        whether the bank reads it as a date or as an instant; extra rows are
        dropped by the framework and balanced out. It never lies in the future.
        """

        def jakarta_day(dt):
            return pytz.utc.localize(dt).astimezone(SNAP_TZ).date()

        first = jakarta_day(date_since)
        last = jakarta_day(date_until - timedelta(seconds=1)) + timedelta(days=1)
        last = max(first, min(last, datetime.now(SNAP_TZ).date()))
        return self._snap_format_date(first), self._snap_format_date(last)

    def _snap_clean_remark(self, remark):
        """One-line remark; fixed-width bank parts shown as "part 1 / part 2"."""
        part = self._snap_config().get("remark_split")
        if part and remark and len(remark) >= 2 * part:
            remark = (
                f"{remark[:part].strip()} / {remark[part : 2 * part].strip()} "
                f"{remark[2 * part :].strip()}"
            )
        return " ".join((remark or "").split())

    @api.model
    def _snap_parse_date(self, value):
        """Bank datetime; one without offset is Jakarta time."""
        date = datetime.fromisoformat(value)
        if date.tzinfo is None:
            date = SNAP_TZ.localize(date)
        return date

    def _snap_detail_to_line(self, item):
        kind = (item.get("type") or "").upper()
        if kind not in SNAP_DEBIT | SNAP_CREDIT:
            raise UserError(
                self.env._(
                    "Unknown SNAP transaction type %(type)s.", type=item.get("type")
                )
            )
        value = float((item.get("amount") or {}).get("value") or 0.0)
        return {
            "date": self._snap_parse_date(item["transactionDate"]),
            "amount": value if kind in SNAP_CREDIT else -value,
            "payment_ref": self._snap_clean_remark(item.get("remark")),
            "raw_data": json.dumps(item),
        }

    def _snap_assign_unique_ids(self, lines_with_items):
        """Stable import id per transaction; twins get -0, -1, ... suffixes.

        :param lines_with_items: [(line_vals, item)] in bank order (newest first)
        """
        self.ensure_one()
        ordered = sorted(
            enumerate(lines_with_items),
            key=lambda pair: (
                self._snap_parse_date(pair[1][1]["transactionDate"]),
                -pair[0],
            ),
        )
        seen = Counter()
        for _index, (line, item) in ordered:
            key = "|".join(
                [
                    self.account_number or "",
                    item.get("transactionDate") or "",
                    (item.get("type") or "").upper(),
                    (item.get("amount") or {}).get("value") or "",
                    item.get("remark") or "",
                ]
            )
            digest = hashlib.sha1(key.encode()).hexdigest()
            line["unique_import_id"] = f"{digest}-{seen[digest]}"
            seen[digest] += 1

    def _snap_obtain_statement_data(self, date_since, date_until):
        self.ensure_one()
        snap = self._snap_check_ready()
        from_dt, to_dt = self._snap_request_date_range(date_since, date_until)
        data = snap._snap_bank_statement(self.account_number, from_dt, to_dt)
        if data.get("hasMore") == "Y" and snap.snap_environment == "production":
            # Paging is not specified yet: never import a partial day silently.
            raise UserError(
                self.env._(
                    "The bank has more transactions for %(since)s - %(until)s "
                    "than one response holds (hasMore=Y, last record "
                    "%(last)s); paging is not supported yet. Nothing was "
                    "imported for this period.",
                    since=from_dt,
                    until=to_dt,
                    last=data.get("lastRecordDateTime") or "-",
                )
            )
        items = data.get("detailData") or []
        unknown = [
            item
            for item in items
            if (item.get("type") or "").upper() not in SNAP_DEBIT | SNAP_CREDIT
        ]
        if unknown:
            # Never block the following days on one odd row: report it.
            self.message_post(
                body=self.env._(
                    "%(count)s transaction(s) with an unknown type were not "
                    "imported for %(since)s - %(until)s, enter them manually: "
                    "%(rows)s",
                    count=len(unknown),
                    since=from_dt,
                    until=to_dt,
                    rows="; ".join(json.dumps(item) for item in unknown),
                )
            )
        pairs = [
            (self._snap_detail_to_line(item), item)
            for item in items
            if item not in unknown
        ]
        self._snap_assign_unique_ids(pairs)
        balances = {}
        balance = (data.get("balance") or [{}])[0]
        start = (balance.get("startingBalance") or {}).get("value")
        end = (balance.get("endingBalance") or {}).get("value")
        if start is not None and end is not None:
            balances = {"balance_start": float(start), "balance_end_real": float(end)}
        return [line for line, _item in pairs], balances

    # Test connection --------------------------------------------------------

    def action_snap_test_connection(self):
        self.ensure_one()
        try:
            snap = self._snap_check_ready()
            snap._snap_get_token(force=True)
            data = snap._snap_balance_inquiry(self.account_number)
        except UserError as exc:
            self.message_post(body=exc.args[0])
            return self._snap_notification(exc.args[0], "danger")
        info = data.get("accountInfos") or {}
        if isinstance(info, list):
            info = info[0] if info else {}
        available = (info.get("availableBalance") or {}).get("value", "-")
        message = self.env._(
            "Connection OK (%(code)s). Account %(account)s %(name)s, "
            "available balance %(balance)s.",
            code=data.get("responseCode"),
            account=self.account_number,
            name=data.get("name") or "",
            balance=available,
        )
        self.message_post(body=message)
        return self._snap_notification(message, "success")

    # Signatures -----------------------------------------------------------

    def _snap_timestamp(self, dt=None):
        """ISO-8601 timestamp in Asia/Jakarta, e.g. 2026-11-17T07:00:00+07:00.

        :param dt: naive UTC datetime, defaults to now
        """
        dt = dt or datetime.utcnow()
        local = pytz.utc.localize(dt.replace(microsecond=0)).astimezone(SNAP_TZ)
        return local.isoformat()

    def _snap_minify(self, payload):
        if payload is None:
            return b""
        return json.dumps(payload, separators=(",", ":")).encode()

    def _snap_sign_asymmetric(self, timestamp):
        """SHA256withRSA over "clientId|timestamp", base64 (token request)."""
        self.ensure_one()
        key = self.sudo()._snap_load_private_key()
        signature = key.sign(
            f"{self.snap_client_key}|{timestamp}".encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode()

    def _snap_symmetric_string_to_sign(
        self, method, relative_url, token, body, timestamp
    ):
        body_hash = hashlib.sha256(body or b"").hexdigest().lower()
        return f"{method.upper()}:{relative_url}:{token}:{body_hash}:{timestamp}"

    def _snap_sign_symmetric(self, method, relative_url, token, body, timestamp):
        """HMAC-SHA512 with the client secret, base64 (service requests)."""
        self.ensure_one()
        string_to_sign = self._snap_symmetric_string_to_sign(
            method, relative_url, token, body, timestamp
        )
        digest = hmac.new(
            (self.sudo().snap_client_secret or "").encode(),
            string_to_sign.encode(),
            hashlib.sha512,
        ).digest()
        return base64.b64encode(digest).decode()

    def _snap_external_id(self):
        """Numeric X-EXTERNAL-ID, unique within the day, max 32 digits."""
        return f"{time.time_ns()}{secrets.randbelow(10**12):012d}"[:32]

    # HTTP -----------------------------------------------------------------

    def _snap_url(self, path):
        self.ensure_one()
        if not self.snap_base_url:
            raise UserError(
                self.env._(
                    "Provider %(name)s has no SNAP Base URL. For production, "
                    "fill in the production Base URL given by the bank.",
                    name=self.name,
                )
            )
        return self.snap_base_url.rstrip("/") + path

    def _snap_path(self, key):
        self.ensure_one()
        path = self._snap_config().get(key)
        if not path:
            raise UserError(
                self.env._(
                    "Service %(service)s does not define the SNAP endpoint %(key)s.",
                    service=self.service,
                    key=key,
                )
            )
        return path

    def _snap_send(self, method, path, headers, body):
        """Send one HTTP request; return (http_status, json dict)."""
        url = self._snap_url(path)
        started = time.monotonic()
        try:
            response = requests.request(
                method, url, headers=headers, data=body, timeout=SNAP_TIMEOUT
            )
        except requests.RequestException as exc:
            raise UserError(
                self.env._(
                    "Could not reach the bank SNAP API at %(host)s (%(error)s).",
                    host=urlparse(url).netloc,
                    error=type(exc).__name__,
                )
            ) from None
        try:
            data = response.json()
        except ValueError:
            data = {}
        _logger.debug(
            "SNAP %s %s -> HTTP %s %s (%.2fs)",
            method,
            path,
            response.status_code,
            data.get("responseCode"),
            time.monotonic() - started,
        )
        return response.status_code, data

    def _snap_error_message(self, http_status, code, message):
        code = code or ""
        prefix = code[:3]
        if prefix == "401":
            hint = self.env._(
                "Unknown client / signature: check that the Client ID belongs to "
                "this environment (sandbox or production), that the private key "
                "belongs to this application, the Client Secret and the Partner ID."
            )
        elif prefix == "403":
            hint = self.env._(
                "The feature is not enabled for this application or corporate at "
                "the bank."
            )
        elif prefix == "409":
            hint = self.env._("The bank reports a duplicate X-EXTERNAL-ID.")
        elif prefix == "429":
            hint = self.env._(
                "Too many rows (more than 20000) or too many requests: use daily "
                "statements."
            )
        elif prefix.startswith("5"):
            hint = self.env._("Bank-side error, retry later.")
        elif prefix == "400":
            hint = self.env._("The bank rejected a request field.")
        else:
            hint = ""
        return self.env._(
            "Bank SNAP API error (HTTP %(status)s): %(code)s %(message)s\n%(hint)s",
            status=http_status,
            code=code or "-",
            message=message or "",
            hint=hint,
        ).strip()

    def _snap_check(self, http_status, data, success_prefix):
        code = data.get("responseCode") or ""
        if not code.startswith(success_prefix):
            raise UserError(
                self._snap_error_message(http_status, code, data.get("responseMessage"))
            )

    def _snap_get_token(self, force=False):
        """Return a valid B2B access token, from cache when possible."""
        self.ensure_one()
        cred = self.sudo()
        now = fields.Datetime.now()
        if (
            not force
            and cred.snap_access_token
            and cred.snap_token_expiry
            and cred.snap_token_expiry - now > TOKEN_MARGIN
        ):
            return cred.snap_access_token
        timestamp = self._snap_timestamp()
        headers = {
            "Content-Type": "application/json",
            "X-TIMESTAMP": timestamp,
            "X-CLIENT-KEY": self.snap_client_key or "",
            "X-SIGNATURE": self._snap_sign_asymmetric(timestamp),
        }
        body = self._snap_minify({"grantType": "client_credentials"})
        status, data = self._snap_send(
            "POST", self._snap_path("token_path"), headers, body
        )
        self._snap_check(status, data, "200")
        token = data.get("accessToken")
        if not token:
            raise UserError(self.env._("The bank returned no access token."))
        try:
            expires_in = int(data.get("expiresIn") or 900)
        except ValueError:
            expires_in = 900
        cred.write(
            {
                "snap_access_token": token,
                "snap_token_expiry": now + timedelta(seconds=expires_in),
            }
        )
        return token

    def _snap_service_headers(self, method, path, token, body):
        timestamp = self._snap_timestamp()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-TIMESTAMP": timestamp,
            "X-SIGNATURE": self._snap_sign_symmetric(
                method, path, token, body, timestamp
            ),
            "X-PARTNER-ID": self.snap_partner_id or "",
            "X-EXTERNAL-ID": self._snap_external_id(),
            "CHANNEL-ID": self.snap_channel_id or "",
        }

    def _snap_request(self, path, payload, method="POST"):
        """Signed SNAP service call; return the JSON response on success."""
        self.ensure_one()
        body = self._snap_minify(payload)
        token = self._snap_get_token()
        status, data = self._snap_send(
            method, path, self._snap_service_headers(method, path, token, body), body
        )
        code = data.get("responseCode") or ""
        if code[:3] == "401" and code[5:] == "01":
            token = self._snap_get_token(force=True)
            status, data = self._snap_send(
                method,
                path,
                self._snap_service_headers(method, path, token, body),
                body,
            )
        self._snap_check(status, data, "200")
        return data

    # SNAP services ------------------------------------------------------------

    def _snap_partner_reference_no(self):
        """partnerReferenceNo of a request.

        Sandboxes may only accept their sample value (bank config key
        ``sandbox_partner_reference_no``); otherwise 22 digits, unique.
        """
        self.ensure_one()
        sample = self._snap_config().get("sandbox_partner_reference_no")
        if self.snap_environment == "sandbox" and sample:
            return sample
        stamp = datetime.now(SNAP_TZ).strftime("%y%m%d%H%M%S")
        return f"{stamp}{secrets.randbelow(10**10):010d}"

    def _snap_bank_statement(self, account_no, from_dt, to_dt):
        return self._snap_request(
            self._snap_path("statement_path"),
            {
                "partnerReferenceNo": self._snap_partner_reference_no(),
                "accountNo": account_no,
                "fromDateTime": from_dt,
                "toDateTime": to_dt,
            },
        )

    def _snap_balance_inquiry(self, account_no):
        return self._snap_request(
            self._snap_path("balance_path"),
            {
                "partnerReferenceNo": self._snap_partner_reference_no(),
                "accountNo": account_no,
            },
        )
