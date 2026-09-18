import unittest
from pathlib import Path
from unittest.mock import patch

from generate_pi_config import generate_config, generate_settings, parse_models_ini


class PiConfigTests(unittest.TestCase):
    def test_current_presets_match_router_and_template(self):
        _, presets = parse_models_ini(Path(__file__).resolve().parents[1] / 'models/models.ini')
        config = generate_config(presets, 'http://localhost:8080/v1/', 'local-llama', '', 64000)
        provider = config['providers']['local-llama']
        self.assertEqual({m['id'] for m in provider['models']}, {'qwen3.8', 'qwen-uncensored'})
        self.assertTrue(provider['compat']['supportsUsageInStreaming'])
        for model in provider['models']:
            self.assertEqual(model['contextWindow'], 160000)
            self.assertEqual(model['input'], ['text'])
            self.assertEqual(model['samplingParams'], {'temperature': 1.0, 'top_k': 20, 'top_p': 0.95, 'min_p': 0.0})
            levels = model['thinkingLevelMap']
            self.assertEqual({v for v in levels.values() if v is not None}, {'low', 'medium', 'xhigh'})
            self.assertEqual(levels['high'], 'xhigh')
            kwargs = model['compat']['chatTemplateKwargs']
            self.assertEqual(kwargs['reasoning_effort'], {'$var': 'thinking.effort'})
            self.assertEqual(kwargs['enable_thinking'], {'$var': 'thinking.enabled'})
        settings = generate_settings(presets, 'local-llama', 64000)
        self.assertEqual(set(settings['modelThinkingLevels'].values()), {'xhigh'})
        for limits in settings['compaction']['modelOverrides'].values():
            self.assertEqual(limits['reserveTokens'], 68096)

    def test_inheritance_and_small_context_validation(self):
        text = 'version = 1\n[*]\nctx-size = 8192\ntemp = 0.7\n[alias]\nmodel = /models/Qwen3.8.gguf\nreasoning = off\n'
        with patch.object(Path, 'is_file', return_value=True), patch.object(Path, 'read_text', return_value=text):
            _, presets = parse_models_ini(Path('models.ini'))
        model = generate_config(presets, 'http://test/v1', 'test', 'pi', 2048)['providers']['test']['models'][0]
        self.assertEqual(model['contextWindow'], 8192)
        self.assertFalse(model['reasoning'])
        self.assertNotIn('thinkingLevelMap', model)
        self.assertEqual(model['samplingParams']['temperature'], 0.7)
        with self.assertRaises(ValueError):
            generate_settings(presets, 'test', 64000)


if __name__ == '__main__':
    unittest.main()
