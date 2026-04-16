"""Ghost Inspector API client."""

import httpx
from typing import Any, Optional


class GhostInspectorClient:
    """Client for interacting with the Ghost Inspector API."""

    BASE_URL = "https://api.ghostinspector.com/v1"

    def __init__(self, api_key: str):
        """Initialize the client with an API key."""
        self.api_key = api_key
        self._client = httpx.Client(timeout=60.0)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> Any:
        """Make a request to the Ghost Inspector API."""
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key

        response = self._client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("code") == "ERROR":
            raise Exception(result.get("message", "Unknown API error"))

        return result.get("data", result)

    # ==================== Tests ====================

    def list_tests(self) -> list[dict]:
        """List all tests in the account."""
        return self._request("GET", "tests")

    def get_test(self, test_id: str) -> dict:
        """Get a single test by ID."""
        return self._request("GET", f"tests/{test_id}")

    def execute_test(
        self,
        test_id: str,
        start_url: Optional[str] = None,
        browser: Optional[str] = None,
        region: Optional[str] = None,
        viewport: Optional[str] = None,
        immediate: bool = False,
        variables: Optional[dict] = None,
    ) -> dict:
        """Execute a test and return the result."""
        params = {}
        if start_url:
            params["startUrl"] = start_url
        if browser:
            params["browser"] = browser
        if region:
            params["region"] = region
        if viewport:
            params["viewport"] = viewport
        if immediate:
            params["immediate"] = "true"
        if variables:
            for key, value in variables.items():
                params[key] = value

        return self._request("POST", f"tests/{test_id}/execute", params=params)

    def list_test_results(
        self, test_id: str, count: int = 10, offset: int = 0
    ) -> list[dict]:
        """List results for a specific test."""
        return self._request(
            "GET",
            f"tests/{test_id}/results",
            params={"count": count, "offset": offset},
        )

    def get_test_result(self, result_id: str) -> dict:
        """Get a specific test result."""
        return self._request("GET", f"results/{result_id}")

    def cancel_test_result(self, result_id: str) -> dict:
        """Cancel a running test result."""
        return self._request("POST", f"results/{result_id}/cancel")

    def duplicate_test(self, test_id: str, suite_id: Optional[str] = None) -> dict:
        """Duplicate an existing test, optionally into a different suite."""
        data = {}
        if suite_id:
            data["suiteId"] = suite_id
        return self._request("POST", f"tests/{test_id}/duplicate", json_data=data if data else None)

    def update_test(self, test_id: str, **kwargs) -> dict:
        """Update a test's properties."""
        return self._request("POST", f"tests/{test_id}", json_data=kwargs)

    def execute_on_demand_test(
        self,
        org_id: str,
        test_definition: dict,
        start_url: Optional[str] = None,
        browser: Optional[str] = None,
        region: Optional[str] = None,
        viewport: Optional[str] = None,
        immediate: bool = False,
    ) -> dict:
        """Execute an on-demand test from a JSON definition.

        The test is executed but not permanently saved to the account.
        """
        params = {"organizationId": org_id}
        if start_url:
            params["startUrl"] = start_url
        if browser:
            params["browser"] = browser
        if region:
            params["region"] = region
        if viewport:
            params["viewport"] = viewport
        if immediate:
            params["immediate"] = "true"

        return self._request(
            "POST", "tests/on-demand/execute", params=params, json_data=test_definition
        )

    # ==================== Suites ====================

    def list_suites(self) -> list[dict]:
        """List all suites in the account."""
        return self._request("GET", "suites")

    def get_suite(self, suite_id: str) -> dict:
        """Get a single suite by ID."""
        return self._request("GET", f"suites/{suite_id}")

    def execute_suite(
        self,
        suite_id: str,
        start_url: Optional[str] = None,
        browser: Optional[str] = None,
        region: Optional[str] = None,
        viewport: Optional[str] = None,
        immediate: bool = False,
        variables: Optional[dict] = None,
    ) -> list[dict]:
        """Execute all tests in a suite and return the results."""
        params = {}
        if start_url:
            params["startUrl"] = start_url
        if browser:
            params["browser"] = browser
        if region:
            params["region"] = region
        if viewport:
            params["viewport"] = viewport
        if immediate:
            params["immediate"] = "true"
        if variables:
            for key, value in variables.items():
                params[key] = value

        return self._request("POST", f"suites/{suite_id}/execute", params=params)

    def list_suite_tests(self, suite_id: str) -> list[dict]:
        """List all tests in a suite."""
        return self._request("GET", f"suites/{suite_id}/tests")

    def list_suite_results(
        self, suite_id: str, count: int = 10, offset: int = 0
    ) -> list[dict]:
        """List results for a specific suite."""
        return self._request(
            "GET",
            f"suites/{suite_id}/results",
            params={"count": count, "offset": offset},
        )

    def get_suite_result(self, result_id: str) -> dict:
        """Get a specific suite result."""
        return self._request("GET", f"suite-results/{result_id}")

    def cancel_suite_result(self, result_id: str) -> dict:
        """Cancel a running suite result."""
        return self._request("POST", f"suite-results/{result_id}/cancel")

    def list_suite_result_tests(self, result_id: str) -> list[dict]:
        """List test results within a suite result."""
        return self._request("GET", f"suite-results/{result_id}/results")

    def create_suite(
        self,
        name: str,
        organization_id: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> dict:
        """Create a new test suite."""
        data = {"name": name}
        if organization_id:
            data["organization"] = organization_id
        if folder_id:
            data["folder"] = folder_id
        return self._request("POST", "suites", json_data=data)

    def update_suite(self, suite_id: str, **kwargs) -> dict:
        """Update a suite's properties (e.g. name, folder)."""
        return self._request("POST", f"suites/{suite_id}", json_data=kwargs)

    def delete_suite(self, suite_id: str) -> dict:
        """Delete a suite."""
        return self._request("DELETE", f"suites/{suite_id}")

    def import_test(self, suite_id: str, test_definition: dict) -> dict:
        """Import a test into a suite from a JSON definition.

        The test is permanently saved to the specified suite.
        """
        return self._request(
            "POST", f"suites/{suite_id}/import-test/json", json_data=test_definition
        )

    # ==================== Folders ====================

    def list_folders(self) -> list[dict]:
        """List all folders in the account."""
        return self._request("GET", "folders")

    def get_folder(self, folder_id: str) -> dict:
        """Get a single folder by ID."""
        return self._request("GET", f"folders/{folder_id}")

    def list_folder_suites(self, folder_id: str) -> list[dict]:
        """List all suites in a folder."""
        return self._request("GET", f"folders/{folder_id}/suites")

    def create_folder(
        self, name: str, organization_id: Optional[str] = None
    ) -> dict:
        """Create a new folder."""
        data = {"name": name}
        if organization_id:
            data["organization"] = organization_id
        return self._request("POST", "folders", json_data=data)

    def update_folder(self, folder_id: str, name: str) -> dict:
        """Update a folder's properties."""
        return self._request(
            "POST", f"folders/{folder_id}", json_data={"name": name}
        )

    def delete_folder(self, folder_id: str) -> dict:
        """Delete a folder."""
        return self._request("DELETE", f"folders/{folder_id}")

    # ==================== Organizations ====================

    def get_running(self, org_id: str) -> list[dict]:
        """Get currently running tests for an organization."""
        return self._request("GET", f"organizations/{org_id}/running")

    def close(self):
        """Close the HTTP client."""
        self._client.close()
