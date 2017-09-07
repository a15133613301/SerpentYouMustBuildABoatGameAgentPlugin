__all__ = [
    "generate_game_board_vector_data",
    "predict_game_move"
]

import numpy as np

import random


rows = ["A", "B", "C", "D", "E", "F"]
columns = [1, 2, 3, 4, 5, 6, 7, 8]


def generate_game_board_vector_data(game_board, game):
    game_board_vector_data = list()
    seen_vector_data = set()

    scores = list()

    game_board_deltas = game.api.generate_game_board_deltas(game_board)
    boolean_game_board_deltas = game.api.generate_boolean_game_board_deltas(game_board_deltas)

    for game_move, boolean_game_boards in boolean_game_board_deltas.items():
        for boolean_game_board in boolean_game_boards:
            for i in range(6):
                row = boolean_game_board[i, :]

                if tuple(row) not in seen_vector_data:
                    game_board_vector_data.append(row)
                    seen_vector_data.add(tuple(row))

                    scores.append(game.api.score_game_board_vector(row))

            for i in range(8):
                column = boolean_game_board[:, i]
                column = np.append(column, [False, False])

                if tuple(column) not in seen_vector_data:
                    game_board_vector_data.append(column)
                    seen_vector_data.add(tuple(column))

                    scores.append(game.api.score_game_board_vector(column))

    return game_board_vector_data, scores


def predict_game_move(model, boolean_game_board_deltas, distribution=None):
    game_move_scores = dict()

    for game_move, boolean_game_boards in boolean_game_board_deltas.items():
        split_game_move = game_move.split(" to ")
        axis = "ROW" if split_game_move[0][0] == split_game_move[1][0] else "COLUMN"

        total_score = 0

        for boolean_game_board in boolean_game_boards:
            input_vectors = list()

            if axis == "ROW":
                row_index = rows.index(split_game_move[0][0])
                row = boolean_game_board[row_index, :]

                input_vectors.append(row)

                for ii in range(8):
                    column = boolean_game_board[:, ii]
                    column = np.append(column, [False, False])

                    input_vectors.append(column)
            elif axis == "COLUMN":
                for ii in range(6):
                    row = boolean_game_board[ii, :]
                    input_vectors.append(row)

                column_index = columns.index(int(split_game_move[0][1]))
                column = boolean_game_board[:, column_index]
                column = np.append(column, [False, False])

                input_vectors.append(column)

            prediction = model.predict(input_vectors)
            total_score += max(prediction)

        game_move_scores[game_move] = total_score

    sorted_game_moves = sorted(game_move_scores.items(), key=lambda x: x[1], reverse=True)

    game_move_index_distribution = distribution or [0, 1, 2, 3, 4]
    game_move_index = random.choice(game_move_index_distribution)

    return sorted_game_moves[game_move_index][0].split(" to ")
