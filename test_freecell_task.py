import unittest
import asyncio
from internbootcamp.bootcamps.freecell.freecell_reward_manager import FreecellRewardManager
from internbootcamp.bootcamps.freecell.freecell_interaction import FreecellInteraction

class TestFreecellTask(unittest.TestCase):
    def test_reward_extraction(self):
        # Test extraction logic
        self.assertEqual(FreecellRewardManager.extract_output("The answer is 1"), 1)
        self.assertEqual(FreecellRewardManager.extract_output("Option 3 is correct"), 3)
        self.assertEqual(FreecellRewardManager.extract_output("I choose 7"), 7)
        self.assertEqual(FreecellRewardManager.extract_output("The answer is option 2."), 2)
        self.assertEqual(FreecellRewardManager.extract_output("Some reasoning... therefore 5"), 5)
        self.assertIsNone(FreecellRewardManager.extract_output("No answer here"))

    def test_reward_scoring(self):
        # Test scoring logic (0.1 format + 0.9 answer)
        identity = {"answer": 1}
        
        # Correct answer
        score = FreecellRewardManager.verify_score("The answer is 1", identity, format_score=0.1)
        self.assertAlmostEqual(score, 1.0)
        
        # Incorrect answer but valid format (extracted something)
        score = FreecellRewardManager.verify_score("The answer is 2", identity, format_score=0.1)
        self.assertAlmostEqual(score, 0.1)
        
        # No answer extracted
        score = FreecellRewardManager.verify_score("No answer", identity, format_score=0.1)
        self.assertAlmostEqual(score, 0.0)

    def test_interaction(self):
        # Test interaction flow
        config = {}
        interaction = FreecellInteraction(config)
        
        async def run_interaction():
            instance_id = await interaction.start_interaction(identity={"answer": 3})
            
            # Correct response
            messages = [{"role": "assistant", "content": "The answer is 3"}]
            should_terminate, response, reward, _ = await interaction.generate_response(instance_id, messages)
            self.assertTrue(should_terminate)
            self.assertAlmostEqual(reward, 1.0)
            
            # Incorrect response
            instance_id = await interaction.start_interaction(identity={"answer": 3})
            messages = [{"role": "assistant", "content": "The answer is 4"}]
            should_terminate, response, reward, _ = await interaction.generate_response(instance_id, messages)
            self.assertTrue(should_terminate)
            self.assertAlmostEqual(reward, 0.1)

        asyncio.run(run_interaction())

if __name__ == '__main__':
    unittest.main()
