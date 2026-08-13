import unittest

from ops.scripts.probe_codex_agent_runtime import probe


class RuntimeProbeTests(unittest.TestCase):
    def test_missing_host_runtime_is_explicitly_unassessed(self):
        result = probe("/definitely/missing/codex-runtime", live=False, timeout=1)
        self.assertEqual(result["config_parse"], "NOT_ASSESSED")
        self.assertEqual(result["runtime_evidence"]["configuration"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["runtime_evidence"]["dispatch"]["status"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
