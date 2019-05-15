import os
import unittest
import numpy as np
from AlphaGo import go
from AlphaGo.ai import ValuePlayer
from AlphaGo.go import GameState
from AlphaGo.models.value import CNNValue


class TestCNNValue(unittest.TestCase):

    def test_default_value(self):

        state = GameState()

        value = CNNValue(["board", "liberties", "sensibleness", "capture_size"])
        value.eval_state(state)
        # just hope nothing breaks

    def test_batch_eval_state(self):

        value = CNNValue(["board", "liberties", "sensibleness", "capture_size"])
        results = value.batch_eval_state([GameState(), GameState()])
        self.assertEqual(len(results), 2)  # one result per GameState
        self.assertTrue(isinstance(results[0], np.float64))
        self.assertTrue(isinstance(results[1], np.float64))

    def test_output_size(self):

        state = GameState()

        value19 = CNNValue(["board", "liberties", "sensibleness", "capture_size"], board=19)
        output = value19.forward(value19.preprocessor.state_to_tensor(state))
        self.assertEqual(output.shape, (1, 1))

        state = GameState(size=13)

        value13 = CNNValue(["board", "liberties", "sensibleness", "capture_size"], board=13)
        output = value13.forward(value13.preprocessor.state_to_tensor(state))
        self.assertEqual(output.shape, (1, 1))

    def test_save_load(self):
        value = CNNValue(["board", "liberties", "sensibleness", "capture_size"])

        model_file = 'TESTVALUE.json'
        weights_file = 'TESTWEIGHTS.h5'
        model_file2 = 'TESTVALUE2.json'
        weights_file2 = 'TESTWEIGHTS2.h5'

        # test saving model/weights separately
        value.save_model(model_file)
        value.model.save_weights(weights_file, overwrite=True)
        # test saving them together
        value.save_model(model_file2, weights_file2)

        copyvalue = CNNValue.load_model(model_file)
        copyvalue.model.load_weights(weights_file)

        copyvalue2 = CNNValue.load_model(model_file2)

        for w1, w2 in zip(copyvalue.model.get_weights(), copyvalue2.model.get_weights()):
            self.assertTrue(np.all(w1 == w2))

        os.remove(model_file)
        os.remove(weights_file)
        os.remove(model_file2)
        os.remove(weights_file2)


class TestValuePlayers(unittest.TestCase):

    def test_greedy_player(self):

        gs = GameState(size=9)

        value = CNNValue(["board", "ones", "turns_since"], board=9)
        player = ValuePlayer(value, greedy_start=0)
        for i in range(10):
            move = player.get_move(gs)
            self.assertNotEqual(move, go.PASS)
            gs.do_move(move)

    def test_probabilistic_player(self):

        gs = GameState(size=9)

        value = CNNValue(["board", "ones", "turns_since"], board=9)
        player = ValuePlayer(value)
        for i in range(10):
            move = player.get_move(gs)
            self.assertNotEqual(move, go.PASS)
            gs.do_move(move)

    def test_sensible_probabilistic(self):

        gs = GameState()

        value = CNNValue(["board", "ones", "turns_since"])
        player = ValuePlayer(value)
        empty = (10, 10)
        for x in range(19):
            for y in range(19):
                if (x, y) != empty:
                    gs.do_move((x, y), go.BLACK)
        gs.set_current_player(go.BLACK)
        self.assertEqual(player.get_move(gs), go.PASS)

    def test_sensible_greedy(self):

        gs = GameState()

        value = CNNValue(["board", "ones", "turns_since"])
        player = ValuePlayer(value, greedy_start=0)
        empty = (10, 10)
        for x in range(19):
            for y in range(19):
                if (x, y) != empty:
                    gs.do_move((x, y), go.BLACK)
        gs.set_current_player(go.BLACK)
        self.assertEqual(player.get_move(gs), go.PASS)


if __name__ == '__main__':
    unittest.main()
