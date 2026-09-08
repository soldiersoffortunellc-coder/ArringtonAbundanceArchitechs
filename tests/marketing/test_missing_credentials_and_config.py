import json
import unittest
from pathlib import Path

from csuite.marketing.content_strategy import validate_ghl_marketing_config
from csuite.providers.base import ProviderLiveModeNotAuthorized
from csuite.providers.avatar_video_adapter import AvatarVideoAdapter
from csuite.providers.idecide_adapter import IDecideAdapter

CONFIG_ROOT = Path(__file__).resolve().parents[2] / "config" / "marketing"


class TestInvalidGhlConfiguration(unittest.TestCase):
    def test_shipped_ghl_marketing_config_template_is_all_placeholders(self):
        with open(CONFIG_ROOT / "ghl_marketing_config.template.json") as fh:
            config = json.load(fh)
        missing = validate_ghl_marketing_config(config)
        # the template must NOT ship with any real-looking ID — every field should still be a placeholder
        self.assertGreater(len(missing), 10)

    def test_shipped_idecide_field_map_template_is_all_placeholders(self):
        with open(CONFIG_ROOT / "idecide" / "field_map.template.json") as fh:
            config = json.load(fh)
        missing = validate_ghl_marketing_config(config)
        field_paths_missing = [p for p in missing if p.startswith("fields.")]
        self.assertEqual(len(field_paths_missing), len(config["fields"]))

    def test_pipeline_mapping_files_flag_placeholder_stage_ids(self):
        with open(CONFIG_ROOT / "pipelines" / "licensed_agent_recruiting.json") as fh:
            config = json.load(fh)
        missing = validate_ghl_marketing_config(config)
        self.assertTrue(any("ghl_stage_id" in path for path in missing))


class TestMissingCredentials(unittest.TestCase):
    def test_every_new_provider_adapter_refuses_live_mode_without_authorization(self):
        for adapter_cls in (AvatarVideoAdapter, IDecideAdapter):
            with self.assertRaises(ProviderLiveModeNotAuthorized):
                adapter_cls(dry_run=False)


if __name__ == "__main__":
    unittest.main()
