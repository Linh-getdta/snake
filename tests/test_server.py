import unittest
from unittest.mock import call, patch

from backend.server import Room


def make_player(name, body, direction):
    return {
        "name": name,
        "body": body,
        "direction": direction,
        "pending": direction,
        "score": 0,
        "alive": True,
    }


class RoomTickTests(unittest.TestCase):
    def test_tick_moves_both_snakes(self):
        room = Room("TEST01")
        room.players = {
            "one": make_player("One", [[100, 100], [80, 100], [60, 100]], "RIGHT"),
            "two": make_player("Two", [[700, 500], [720, 500], [740, 500]], "LEFT"),
        }
        room.food = [400, 300]

        room.tick()

        self.assertEqual(room.players["one"]["body"][0], [120, 100])
        self.assertEqual(room.players["two"]["body"][0], [680, 500])
        self.assertFalse(room.finished)

    def test_eating_food_increases_score_and_respawns_food(self):
        room = Room("TEST02")
        room.players = {
            "one": make_player("One", [[100, 100], [80, 100], [60, 100]], "RIGHT"),
            "two": make_player("Two", [[700, 500], [720, 500], [740, 500]], "LEFT"),
        }
        room.food = [120, 100]

        room.tick()

        self.assertEqual(room.players["one"]["score"], 10)
        self.assertEqual(len(room.players["one"]["body"]), 4)
        self.assertNotIn(room.food, room.players["one"]["body"])

    def test_head_on_collision_finishes_match_and_captures_scores(self):
        room = Room("TEST03")
        room.players = {
            "one": make_player("One", [[100, 100], [80, 100], [60, 100]], "RIGHT"),
            "two": make_player("Two", [[140, 100], [160, 100], [180, 100]], "LEFT"),
        }
        room.food = [400, 300]

        room.tick()

        self.assertTrue(room.finished)
        self.assertFalse(room.players["one"]["alive"])
        self.assertFalse(room.players["two"]["alive"])
        self.assertEqual(room.final_scores, [("One", 0), ("Two", 0)])


class ResultPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_persists_both_players_after_a_disconnect(self):
        room = Room("TEST04")
        room.players = {
            "two": make_player("Two", [[700, 500], [720, 500], [740, 500]], "LEFT")
        }
        room.final_scores = [("One", 10), ("Two", 20)]

        with patch("backend.server.save_game") as save_game:
            await room.persist_results()

        save_game.assert_has_calls([call("One", 10), call("Two", 20)])


if __name__ == "__main__":
    unittest.main()
