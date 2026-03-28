"""Integration tests for the RTR module."""

import pytest

from falcon_mcp.modules.rtr import RTRModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestRTRIntegration(BaseIntegrationTest):
    """Integration tests for the RTR module with real API calls.

    Validates:
    - Correct FalconPy operation names for RTR session search and details
    - Two-step search pattern returns full session details, not just IDs
    - POST body usage for session detail lookups
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the RTR module with a real client."""
        self.module = RTRModule(falcon_client)

    def test_search_rtr_sessions_returns_details(self):
        """Test that RTR session search returns full session details."""
        result = self.call_method(self.module.search_sessions, limit=5)

        self.assert_no_error(result, context="search_rtr_sessions")
        self.assert_valid_list_response(result, min_length=0, context="search_rtr_sessions")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "device_id", "hostname"],
                context="search_rtr_sessions",
            )

    def test_search_rtr_sessions_with_sort(self):
        """Test RTR session search with a supported sort expression."""
        result = self.call_method(
            self.module.search_sessions,
            sort="created_at.desc",
            limit=3,
        )

        self.assert_no_error(result, context="search_rtr_sessions with sort")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_rtr_sessions with sort",
        )

    def test_get_rtr_session_details_with_valid_id(self):
        """Test session detail lookup using a valid session ID."""
        search_result = self.call_method(self.module.search_sessions, limit=1)

        if not search_result or len(search_result) == 0:
            self.skip_with_warning(
                "No RTR sessions available to test get_rtr_session_details",
                context="test_get_rtr_session_details_with_valid_id",
            )

        session_id = self.get_first_id(search_result)
        if not session_id:
            self.skip_with_warning(
                "Could not extract session ID from RTR search results",
                context="test_get_rtr_session_details_with_valid_id",
            )

        result = self.call_method(self.module.get_session_details, ids=[session_id])

        self.assert_no_error(result, context="get_rtr_session_details")
        self.assert_valid_list_response(result, min_length=1, context="get_rtr_session_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "device_id", "hostname"],
            context="get_rtr_session_details",
        )

    def test_operation_names_are_correct(self):
        """Validate that the RTR FalconPy operation names are correct."""
        result = self.call_method(self.module.search_sessions, limit=1)
        self.assert_no_error(result, context="RTR operation name validation")
