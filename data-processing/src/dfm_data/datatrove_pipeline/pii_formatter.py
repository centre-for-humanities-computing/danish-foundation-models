from functools import partial
from typing import Optional

from datatrove.pipeline.formatters.base import BaseFormatter
from datatrove.pipeline.formatters.pii import PIIReplacer, public_ip_validator

class PIIFormatter(BaseFormatter):
    """
    Replaces email addresses and ip addresses in the document text.
    Args:
        remove_emails: Replace email addresses
        remove_ips: Replace IP addresses
        only_remove_public_ips: by default we only replace public (and thus PII) IPs
        email_replacement: tuple of strings to use as replacement. They will be used in a circular way
        ip_replacement same as email_replacement but for IP addresses
    """

    name = "📞 PII"

    def __init__(
        self,
        remove_emails: bool = True,
        remove_ips: bool = True,
        only_remove_public_ips: bool = True,
        remove_danish_cpr: bool = True,
        email_replacement: Optional[tuple[str, ...] | str] = None,
        ip_replacement: Optional[tuple[str, ...] | str] = None,
        danish_cpr_replacement: Optional[tuple[str, ...] | str] = None,
    ):
        super().__init__()
        self.remove_emails = remove_emails
        self.remove_ips = remove_ips
        self.remove_danish_cpr = remove_danish_cpr

        if not email_replacement:
            # example.com/org are actually maintained as an example
            email_replacement = ("email@example.com", "firstname.lastname@example.org")

        if not ip_replacement:
            # randomly generated list of ips. they did not respond to ping requests at the time the list was created
            ip_replacement = (
                "22.214.171.124",
                "126.96.36.199",
                "188.8.131.52",
                "184.108.40.206",
                "220.127.116.11",
                "18.104.22.168",
            )

        if not danish_cpr_replacement:
            danish_cpr_replacement = (
                "000000-0000",
                "111111-1111",
                "222222-2222",
                "333333-3333",
                "444444-4444",
                "555555-5555",
                "666666-6666",
                "777777-7777",
                "888888-8888",
                "999999-9999",
            )


        self.emails_replacer = PIIReplacer(
            r"\b[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:(?:[A-Za-z0-9](?:["
            r"A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|["
            r"01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[A-Za-z0-9-]*[A-Za-z0-9]:)])",
            email_replacement,
        )

        self.ip_replacer = PIIReplacer(
            r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
            validator=partial(public_ip_validator, public_only=only_remove_public_ips),
            replacements=ip_replacement,
        )

        self.danish_cpr_replacer = PIIReplacer(
            r"\b(0[1-9]|[12]\d|3[01])(0[1-9]|1[0-2])\d{2}[-]?\d{4}\b",
            danish_cpr_replacement,
        )

    def format(self, text: str) -> str:
        if self.remove_emails:
            text = self.emails_replacer.replace(text)
        if self.remove_ips:
            text = self.ip_replacer.replace(text)
        if self.remove_danish_cpr:
            text = self.danish_cpr_replacer.replace(text)
        return text
