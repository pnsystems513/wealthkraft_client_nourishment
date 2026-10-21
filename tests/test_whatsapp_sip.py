import asyncio
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from sqlalchemy import column

from app.jobs import scheduler
from app.models.cms_read_db import SipHistory
from app.services import whatsapp_sip


class FakeQuery:
    def __init__(self, rows, session):
        self.rows = rows
        self.session = session

    def label(self, *_args):
        return self

    def join(self, *_args):
        return self

    def filter(self, *_args):
        self.session.filters.extend(_args)
        return self

    def group_by(self, *_args):
        self.session.group_by_args = _args
        return self

    def subquery(self):
        return SimpleNamespace(
            c=SimpleNamespace(
                client_id=column("client_id"),
                oldest_sip_start_date=column("oldest_sip_start_date"),
            )
        )

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows):
        self.rows = rows
        self.closed = False
        self.query_count = 0
        self.query_entities = []
        self.group_by_args = ()
        self.filters = []

    def query(self, *_entities):
        self.query_count += 1
        self.query_entities.append(_entities)
        return FakeQuery(self.rows if self.query_count == 2 else [], self)

    def close(self):
        self.closed = True


class WhatsAppSipTests(unittest.IsolatedAsyncioTestCase):
    async def test_sip_template_request_uses_configured_credentials_and_payload(self):
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.post.return_value = SimpleNamespace(
            status_code=200, text="accepted"
        )

        with (
            patch.object(whatsapp_sip, "_API_KEY", "test-key"),
            patch.object(whatsapp_sip, "_API_URL", "https://example.test/send"),
            patch.object(whatsapp_sip, "_SIP_CAMPAIGN", "sip-anniversary"),
            patch.object(whatsapp_sip.httpx, "AsyncClient", return_value=client),
        ):
            result = await whatsapp_sip.send_sip_anniversary_whatsapp(
                "919876543210", "Test Client", "Test Agent"
            )

        self.assertTrue(result)
        request = client.post.await_args.kwargs
        self.assertEqual(request["json"]["apiKey"], "test-key")
        self.assertEqual(request["json"]["campaignName"], "sip-anniversary")
        self.assertEqual(request["json"]["destination"], "919876543210")
        self.assertEqual(request["json"]["templateParams"], ["Test Client"])
        self.assertEqual(request["json"]["media"]["filename"], "sip_image")

    async def test_non_successful_aisensy_response_returns_false(self):
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.post.return_value = SimpleNamespace(
            status_code=503, text="unavailable"
        )

        with (
            patch.object(whatsapp_sip, "_API_KEY", "test-key"),
            patch.object(whatsapp_sip, "_API_URL", "https://example.test/send"),
            patch.object(whatsapp_sip, "_SIP_CAMPAIGN", "sip-anniversary"),
            patch.object(whatsapp_sip.httpx, "AsyncClient", return_value=client),
        ):
            result = await whatsapp_sip.send_sip_anniversary_whatsapp(
                "919876543210", "Test Client"
            )

        self.assertFalse(result)


class SipAnniversaryJobTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2027, 1, 1)
        client = SimpleNamespace(
            id="client-1",
            full_name="Test Client",
            mobile_number="919876543210",
            agent_username="",
            owner_username="Test Agent",
        )
        self.oldest_start_date = date(2026, 1, 1)
        self.db = FakeSession([(client, self.oldest_start_date)])
        self.state = {}
        self.sender = AsyncMock(return_value=True)

    def run_job(self):
        with (
            patch.object(scheduler, "_today_in_scheduler_timezone", return_value=self.today),
            patch.object(scheduler, "_load_state", side_effect=lambda: self.state.copy()),
            patch.object(
                scheduler,
                "_save_state",
                side_effect=lambda update: (self.state.update(update) or True),
            ),
            patch.object(scheduler, "CMSSessionLocal", return_value=self.db),
            patch.object(scheduler, "send_sip_anniversary_whatsapp", self.sender),
            patch.object(scheduler, "_run_async", side_effect=asyncio.run),
        ):
            scheduler.sip_anniversary_job()

    def test_success_is_persisted_and_duplicate_job_run_is_skipped(self):
        self.run_job()
        self.run_job()

        self.sender.assert_awaited_once_with(
            "919876543210", "Test Client", "Test Agent"
        )
        self.assertEqual(self.state["sip_anniversary_sent_date"], "2027-01-01")
        self.assertEqual(
            self.state["sip_anniversary_sent_ids"], ["client-1:2027"]
        )
        self.assertIn("min(sip_histories.sip_start_date)", str(self.db.query_entities[0][1]))
        self.assertEqual(self.db.group_by_args, (SipHistory.client_id,))
        anniversary_filters = " ".join(
            str(criteria.compile(compile_kwargs={"literal_binds": True}))
            for criteria in self.db.filters
        )
        self.assertIn("EXTRACT(year FROM oldest_sip_start_date) = 2026", anniversary_filters)
        self.assertTrue(self.db.closed)

    def test_api_failure_is_not_marked_as_sent(self):
        self.sender.return_value = False

        self.run_job()

        self.sender.assert_awaited_once()
        self.assertNotIn("sip_anniversary_sent_ids", self.state)

    def test_created_at_is_not_used_as_the_sip_start_date(self):
        self.assertIn("sip_start_date", SipHistory.__table__.c)
        self.assertNotIn("sip_start_date", ("created_at", "updated_at"))


if __name__ == "__main__":
    unittest.main()
