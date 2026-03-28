"""
Tests for the RTR module.
"""

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.rtr import RTRModule
from tests.modules.utils.test_modules import TestModules


class TestRTRModule(TestModules):
    """Test cases for the RTR module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(RTRModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_rtr_sessions",
            "falcon_get_rtr_session_details",
            "falcon_init_rtr_session",
            "falcon_pulse_rtr_session",
            "falcon_execute_rtr_read_only_command",
            "falcon_check_rtr_command_status",
            "falcon_list_rtr_session_files",
            "falcon_delete_rtr_session",
        ]
        self.assert_tools_registered(expected_tools)

    def test_tool_annotations(self):
        """Test tool annotations are correctly set."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_rtr_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_rtr_session_details", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_init_rtr_session",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_execute_rtr_read_only_command",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations("falcon_check_rtr_command_status", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_list_rtr_session_files", READ_ONLY_ANNOTATIONS)

    def test_search_sessions_returns_full_details(self):
        """Test searching RTR sessions fetches details after IDs are returned."""
        search_response = {
            "status_code": 200,
            "body": {"resources": ["session-1", "session-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "session-1", "aid": "aid-1"},
                    {"id": "session-2", "aid": "aid-2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [search_response, details_response]

        result = self.module.search_sessions(
            filter="hostname:'BRR-WB-LIB-22'",
            limit=25,
            offset=0,
            sort="created_at.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListAllSessions")
        self.assertEqual(first_call[1]["parameters"]["filter"], "hostname:'BRR-WB-LIB-22'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 25)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "created_at.desc")

        self.assertEqual(second_call[0][0], "RTR_ListSessions")
        self.assertEqual(second_call[1]["body"]["ids"], ["session-1", "session-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "session-1")

    def test_get_session_details_empty_ids(self):
        """Test get_session_details returns early for empty input."""
        result = self.module.get_session_details(ids=[])

        self.assertEqual(result, [])
        self.mock_client.command.assert_not_called()

    def test_init_session(self):
        """Test RTR session initialization."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-1"}]},
        }

        result = self.module.init_session(
            device_id="aid-123",
            origin="falcon-mcp",
            queue_offline=True,
            timeout=30,
            timeout_duration="30s",
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_InitSession",
            body={
                "device_id": "aid-123",
                "origin": "falcon-mcp",
                "queue_offline": True,
                "timeout": 30,
                "timeout_duration": "30s",
            },
        )
        self.assertEqual(result[0]["session_id"], "session-1")

    def test_execute_read_only_command(self):
        """Test RTR read-only command execution."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-123"}]},
        }

        result = self.module.execute_read_only_command(
            session_id="session-1",
            base_command="cat",
            command_string=r"cat C:\Windows\win.ini",
            persist=False,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_ExecuteCommand",
            body={
                "session_id": "session-1",
                "base_command": "cat",
                "command_string": r"cat C:\Windows\win.ini",
                "persist": False,
            },
        )
        self.assertEqual(result[0]["cloud_request_id"], "req-123")

    def test_check_command_status(self):
        """Test retrieving RTR command status."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"complete": True, "stdout": "ok"}]},
        }

        result = self.module.check_command_status(
            cloud_request_id="req-123",
            sequence_id=1,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_CheckCommandStatus",
            parameters={"cloud_request_id": "req-123", "sequence_id": 1},
        )
        self.assertTrue(result[0]["complete"])

    def test_list_session_files(self):
        """Test listing RTR session files."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "abc"}]},
        }

        result = self.module.list_session_files(session_id="session-1")

        self.mock_client.command.assert_called_once_with(
            "RTR_ListFilesV2",
            parameters={"session_id": "session-1"},
        )
        self.assertEqual(result[0]["sha256"], "abc")

    def test_delete_session(self):
        """Test deleting an RTR session."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-1", "deleted": True}]},
        }

        result = self.module.delete_session(session_id="session-1")

        self.mock_client.command.assert_called_once_with(
            "RTR_DeleteSession",
            parameters={"session_id": "session-1"},
        )
        self.assertTrue(result[0]["deleted"])
